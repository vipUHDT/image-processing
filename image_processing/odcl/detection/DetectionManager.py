"""
Detection manager for batched, threaded ODCL processing.

This module defines :class:`DetectionManager`, which coordinates the
object detection and localization (ODCL) workflow. It manages queues of
incoming images and platform states, dispatches worker threads to run
detection using a configured model, georeferences detection pixel
coordinates into GPS coordinates, deduplicates overlapping detections,
and stores aggregated detections and model results for downstream use.
"""

import cv2
from image_processing.odcl.Localize import *
from .SahiConfig import SahiConfig
from image_processing.camera import *
from image_processing.odcl.Localize import *
from .Detection import *
from queue import Queue, Empty
from image_processing import QueuedImage, PlatformState
from sahi.models.base import DetectionModel
from .SahiConfig import SahiDetectionModel
import threading
from typing import Optional

class DetectionManager:
    """
    Manager for running detection and localization on queued images.

    This class maintains several queues (images, detections, results, GPS)
    and a pool of worker threads that process images as they arrive. For
    each queued image, it runs ODCL via a :class:`Detector`, converts
    detections into GPS coordinates using a :class:`Georeference_Engine`
    and :class:`CameraMetadata`, and stores unique detections based on
    spatial proximity.

    Parameters
    ----------
    detection_model_config : ModelConfig or None, optional
        Configuration used to construct the underlying detection model.
    camera_metadata : CameraMetadata or None, optional
        Intrinsic camera metadata used for georeferencing, if available.
    georeference_engine : Georeference_Engine or None, optional
        Georeferencing engine responsible for converting pixel coordinates
        into GPS coordinates.

    Attributes
    ----------
    detection_model_config : ModelConfig or None
        Detection model configuration.
    image_queue : queue.Queue
        Queue of :class:`QueuedImage` instances to be processed.
    detections_queue : queue.Queue
        Queue of detections produced by worker threads.
    results_queue : queue.Queue
        Queue of :class:`DetectionModelResult` instances, one per processed image.
    gps_queue : queue.Queue
        Queue of GPS coordinates (from georeferenced detections).
    detections : list of Detection
        Accumulated list of all detections processed so far.
    results : list of DetectionModelResult
        Accumulated list of model results.
    active_threads : list of threading.Thread
        Currently running worker threads.
    workers : int
        Maximum number of worker threads used to process queued images.
    max_concurrent_queue_process : int
        Upper bound for how many queued items may be processed at once
        (currently not enforced directly in this implementation).
    duplicate_threshold : float
        Spatial threshold (in the units of `haversine`) used to treat two
        detections as duplicates.
    camera : CameraMetadata or None
        Camera metadata used for georeferencing.
    georeference_engine : Georeference_Engine or None
        Engine used to convert pixel coordinates to GPS.
    terminated : bool
        Flag that can be used to mark the manager as shut down.
    """

    def __init__(self, detection_model_config: Optional[ModelConfig]= None, camera_metadata: CameraMetadata | None = None, georeference_engine: Georeference_Engine | None = None):
        self.detection_model_config = detection_model_config
        self.image_queue = Queue()
        self.detections_queue = Queue()
        self.results_queue = Queue()
        self.gps_queue = Queue()

        self.detections = []
        self.results = []
        
        self.active_threads: list[threading.Thread] = []
        self.workers = 5
        self.max_concurrent_queue_process = 10
        
        self.duplicate_threshold = 2
        self.camera: CameraMetadata | None = camera_metadata
        self.georeference_engine = georeference_engine
        self.terminated = False


    def update(self):
        """
        Poll internal queues and update detection and result lists.

        This method should be called periodically (e.g., in a main loop)
        to move items from internal queues into the `detections` and
        `results` lists.
        """
        self.updateDetections()
        self.updateResults()

    
    def updateResults(self):
        """
        Move a single queued result (if any) into the `results` list.

        Uses a non-blocking queue get; if no item is available, this
        method returns immediately.
        """
        try:
            result = self.results_queue.get_nowait()
        except Empty:
            pass
        else:
            self.results.append(result)

    def updateDetections(self):
        """
        Move a single queued detection (if any) into the `detections` list.

        Detected GPS coordinates are also forwarded into the `gps_queue`
        for separate retrieval.
        """
        try:
            detection = self.detections_queue.get_nowait()
        except Empty:
            pass
        else:
            print(detection.gps_coords)
            self.gps_queue.put(detection.gps_coords)
            self.detections.append(detection)

    
    def getGPS(self):
        """
        Retrieve a single GPS coordinate from the GPS queue, if available.

        Returns
        -------
        Any or None
            Next GPS entry from the queue, or None if the queue is empty.
        """
        if self.gps_queue.qsize() > 0:
            return self.gps_queue.get()
        else:
            return None



    
    def queueImage(self, image: QueuedImage):
        """
        Enqueue an image (and platform state) for detection processing.

        Parameters
        ----------
        image : QueuedImage
            Object containing an image and associated platform state to be
            processed by ODCL.
        """
        self.image_queue.put(image)

    def processQueuedImages(self):
        """
        Spawn worker threads to process queued images.

        This method prunes inactive threads and, while there are items in
        the image queue and fewer than `workers` active threads, pops
        images and launches new threads targeting :meth:`processQueuedImage`.
        """
        self.pruneThreads()
        if (self.image_queue.qsize() > 0):
            for i in range(self.workers):
                if len(self.active_threads) < self.workers:
                    try:
                        queued_image = self.image_queue.get_nowait()
                    except Empty:
                        break
                    else:
                        if queued_image:
                            t = threading.Thread(
                                target=self.processQueuedImage,
                                args=((queued_image,)),
                                daemon=True,
                                name="DetectionManager"
                            )
                            t.start()
                            self.active_threads.append(t)


    def processGPSQueue(self):
        """
        Drain up to 10 GPS entries from the GPS queue.

        Returns
        -------
        list
            List of GPS coordinate entries retrieved from the queue
            (up to a maximum of 10 items).
        """
        gps_coords = []
        while (self.gps_queue.qsize() > 0):
            try:
                gps_info = self.gps_queue.get_nowait()
            except Empty:
                break
            else:
                gps_coords.append(gps_info)
                if len(gps_coords) > 10:
                    break
        return gps_coords


    def pruneThreads(self):
        """
        Remove inactive worker threads from the internal tracking list.
        """
        self.active_threads = [ t for t in self.active_threads if t.is_alive()]

    def processQueuedImage(self, queued_image: QueuedImage):
        """
        Process a single queued image by running ODCL.

        Parameters
        ----------
        queued_image : QueuedImage
            Object containing an image and corresponding platform state.
        """
        image = queued_image.image
        platform_state = queued_image.platform_state
        self.ODCL(image, platform_state)

    def addResult(self, result: DetectionModelResult):
        """
        Enqueue a model result for later retrieval.

        Parameters
        ----------
        result : DetectionModelResult
            Result object containing image-level detection information.
        """
        self.results_queue.put(result)

    def addDetection(self, detection: Detection, platform_state: PlatformState):
        """
        Add a single detection, optionally georeferencing and deduplicating.

        If a georeference engine and camera metadata are configured, the
        detection's pixel coordinates are converted into GPS coordinates.
        Detections within `duplicate_threshold` distance (in `haversine`
        units) of existing detections are discarded.

        Parameters
        ----------
        detection : Detection
            Detection object to process and potentially enqueue.
        platform_state : PlatformState
            Platform/vehicle state at the time of detection, used for
            georeferencing.
        """
        if isinstance(self.georeference_engine, Georeference_Engine) and isinstance(self.camera, CameraMetadata):
            detection.gps_coords = self.georeference(detection.pixel_coords, platform_state, self.camera, self.georeference_engine.altitude_offset)
        
        if not self.checkForDuplicates(detection):
            self.gps_queue.put(detection.gps_coords)
            self.detections_queue.put(detection)
    
    def checkForDuplicates(self, detection: Detection):
        """
        Check if a detection is a spatial duplicate of an existing one.

        Two detections are considered duplicates if the `haversine` distance
        between their GPS locations is less than :attr:`duplicate_threshold`.

        Parameters
        ----------
        detection : Detection
            Detection to compare against previously recorded detections.

        Returns
        -------
        bool
            True if a sufficiently close detection already exists,
            otherwise False.
        """
        for existing_detection in self.detections:
            if detection.gps_coords and abs(haversine(detection.gps_coords[0], detection.gps_coords[1], existing_detection.gps_coords[0], existing_detection.gps_coords[1])) < self.duplicate_threshold:
                return True
    
    def setGeoreferenceEngine(self, georeference_backend, altitude_offset = 0):
        """
        Initialize and attach a georeference engine.

        Parameters
        ----------
        georeference_backend : Any
            Backend implementation used by :class:`Georeference_Engine`.
        altitude_offset : float, optional
            Altitude offset passed to the georeference engine, by default 0.
        """
        self.georeference_engine = Georeference_Engine(georeference_backend, altitude_offset)

    def georeference(self, target_pixel_coordinates, platform_state, camera_metadata, altitude_offset):
        """
        Convert pixel coordinates into GPS coordinates using the georeference engine.

        Parameters
        ----------
        target_pixel_coordinates : Any
            Target pixel coordinates (e.g., (x, y)) in image space.
        platform_state : PlatformState
            Platform/vehicle state associated with this frame.
        camera_metadata : CameraMetadata
            Intrinsic camera metadata required for georeferencing.
        altitude_offset : float
            Altitude offset parameter passed to the georeference engine.

        Returns
        -------
        Any
            Georeferenced coordinates, as returned by the georeference engine.
        """
        if self.georeference_engine:
            return self.georeference_engine.georeference(target_pixel_coordinates, platform_state, camera_metadata, altitude_offset)
    
    def addDetections(self, detections: list[Detection], platform_state: PlatformState):
        """
        Add and process a list of detections for a given platform state.

        Parameters
        ----------
        detections : list of Detection
            List of detection objects to process.
        platform_state : PlatformState
            Platform/vehicle state corresponding to these detections.
        """
        for detection in detections:
            self.addDetection(detection, platform_state)

    def ODCL(self, image, platform_state):
        """
        Run the full ODCL pipeline on a single image and platform state.

        This constructs a :class:`Detector` using the configured model
        config, loads the model, performs detection on the provided image,
        parses the results into :class:`Detection` objects, and queues
        results and detections for later retrieval.

        Parameters
        ----------
        image : Any
            Image (e.g., NumPy array) on which to run detection.
        platform_state : PlatformState
            Platform/vehicle state at the time of the image acquisition.
        """
        detector = Detector(self.detection_model_config)
        detector.loadModel()
        if isinstance(detector, Detector):
            results = detector.run(image)
            if isinstance(results, PredictionResult):
                detection_model_result, detections = detector.parseResults(results)
                self.addResult(detection_model_result)
                self.addDetections(detections, platform_state)
                
    def getAllDetections(self):
        """
        Return the list of all detections processed so far.

        Returns
        -------
        list of Detection
            All stored detections.
        """
        return self.detections

    def filterByClassification(self, classification: str):
        """
        Filter detections by classification label.

        This assumes that each :class:`Detection` implements a
        ``classify_object`` method that can be used to check the
        classification label.

        Parameters
        ----------
        classification : str
            Class label to filter by.

        Returns
        -------
        list of Detection
            Detections whose `classify_object` result matches the
            requested classification.
        """
        return [
            d
            for d in self.detections
            if d.classify_object(classification) == classification
        ]

    def filterByConfidence(self, threshold: float):
        """
        Filter detections by confidence threshold.

        Parameters
        ----------
        threshold : float
            Minimum confidence required for a detection to be included.
            Must be in the range [0.0, 1.0].

        Returns
        -------
        list of Detection
            Detections whose confidence score is greater than or equal
            to `threshold`.

        Raises
        ------
        ValueError
            If `threshold` is outside the range [0.0, 1.0].
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        return [d for d in self.detections if d.get_confidence() >= threshold]

    def clearDetections(self):
        """
        Clear all stored detections from memory.

        This does not affect queued detections or results.
        """
        self.detections.clear()