"""Threaded detection pipeline: queues images, runs inference, and georeferences results."""

import logging
import threading
from queue import Empty, Queue
from typing import Optional

from sahi.prediction import PredictionResult

from image_processing import PlatformState, QueuedImage
from image_processing.camera import CameraMetadata
from image_processing.odcl.Localize import Georeference_Engine, haversine

from .Detection import Detection, DetectionModelResult, Detector
from .SahiConfig import ModelConfig

LOGGER = logging.getLogger(__name__)


class DetectionManager:
    """
    Run object detection on queued images in worker threads.

    Images are queued with their platform state, processed by ``Detector``
    workers, georeferenced (when an engine and camera metadata are
    configured), de-duplicated by GPS proximity, and collected into
    ``detections`` and ``results`` via ``update``.

    Parameters
    ----------
    detection_model_config : ModelConfig, optional
        Model configuration passed to each ``Detector``.
    camera_metadata : CameraMetadata, optional
        Camera intrinsics used for georeferencing.
    georeference_engine : Georeference_Engine, optional
        Engine used to convert pixel coordinates to GPS coordinates.
    """

    def __init__(
        self,
        detection_model_config: Optional[ModelConfig] = None,
        camera_metadata: CameraMetadata | None = None,
        georeference_engine: Georeference_Engine | None = None,
    ):
        self.detection_model_config = detection_model_config
        self.image_queue = Queue()
        self.detections_queue = Queue()
        self.results_queue = Queue()
        self.gps_callback = None

        self.detections = []
        self.results = []

        self.active_threads: list[threading.Thread] = []
        self.workers = 5
        self.max_concurrent_queue_process = 10

        self.duplicate_threshold = 2  # meters
        self.camera: CameraMetadata | None = camera_metadata
        self.georeference_engine = georeference_engine
        self.terminated = False

    def setGPSCallback(self, callback):
        """Register a callable invoked with each new detection's GPS coordinates."""
        self.gps_callback = callback

    def update(self):
        """Drain one item each from the detection and result queues into their lists."""
        self.updateDetections()
        self.updateResults()

    def updateResults(self):
        """Move one pending model result from the queue to ``results``, if any."""
        try:
            result = self.results_queue.get_nowait()
        except Empty:
            pass
        else:
            self.results.append(result)

    def updateDetections(self):
        """Move one pending detection from the queue to ``detections``, if any."""
        try:
            detection = self.detections_queue.get_nowait()
        except Empty:
            pass
        else:
            LOGGER.debug("New detection at %s", detection.gps_coords)
            self.detections.append(detection)

    def queueImage(self, image: QueuedImage):
        """Add an image (with platform state) to the processing queue."""
        self.image_queue.put(image)

    def processQueuedImages(self):
        """Start worker threads for queued images, up to the ``workers`` limit."""
        self.pruneThreads()
        if self.image_queue.qsize() > 0:
            for _ in range(self.workers):
                if len(self.active_threads) < self.workers:
                    try:
                        queued_image = self.image_queue.get_nowait()
                    except Empty:
                        break
                    if queued_image:
                        t = threading.Thread(
                            target=self.processQueuedImage,
                            args=(queued_image,),
                            daemon=True,
                            name="DetectionManager",
                        )
                        t.start()
                        self.active_threads.append(t)

    def pruneThreads(self):
        """Drop finished worker threads from the active list."""
        self.active_threads = [t for t in self.active_threads if t.is_alive()]

    def processQueuedImage(self, queued_image: QueuedImage):
        """Run the detection pipeline on a single queued image."""
        self.ODCL(queued_image.image, queued_image.platform_state)

    def addResult(self, result: DetectionModelResult):
        """Queue a model result for collection by ``update``."""
        self.results_queue.put(result)

    def addDetection(self, detection: Detection, platform_state: PlatformState):
        """Georeference a detection and queue it unless it duplicates an existing one."""
        if isinstance(self.georeference_engine, Georeference_Engine) and isinstance(self.camera, CameraMetadata):
            detection.gps_coords = self.georeference(
                detection.pixel_coords,
                platform_state,
                self.camera,
                self.georeference_engine.altitude_offset,
            )

        if not self.checkForDuplicates(detection):
            if self.gps_callback:
                self.gps_callback(detection.gps_coords)
            self.detections_queue.put(detection)

    def checkForDuplicates(self, detection: Detection) -> bool:
        """Return True if a known detection lies within ``duplicate_threshold`` meters."""
        if not detection.gps_coords:
            return False
        for existing_detection in self.detections:
            if not existing_detection.gps_coords:
                continue
            distance = haversine(
                detection.gps_coords[0],
                detection.gps_coords[1],
                existing_detection.gps_coords[0],
                existing_detection.gps_coords[1],
            )
            if abs(distance) < self.duplicate_threshold:
                return True
        return False

    def setGeoreferenceEngine(self, georeference_backend, altitude_offset=0):
        """Create the georeference engine for the given backend name."""
        self.georeference_engine = Georeference_Engine(georeference_backend, altitude_offset)

    def georeference(self, target_pixel_coordinates, platform_state, camera_metadata, altitude_offset):
        """Convert pixel coordinates to GPS via the configured engine, or None."""
        if self.georeference_engine:
            return self.georeference_engine.georeference(
                target_pixel_coordinates, platform_state, camera_metadata, altitude_offset
            )

    def addDetections(self, detections: list[Detection], platform_state: PlatformState):
        """Add multiple detections via ``addDetection``."""
        for detection in detections:
            self.addDetection(detection, platform_state)

    def ODCL(self, image, platform_state):
        """Run object detection, classification, and localization on one image."""
        detector = Detector(self.detection_model_config)
        detector.loadModel()
        results = detector.run(image)
        if isinstance(results, PredictionResult):
            detection_model_result, detections = detector.parseResults(results)
            self.addResult(detection_model_result)
            self.addDetections(detections, platform_state)

    def getAllDetections(self):
        """Return all collected detections."""
        return self.detections

    def filterByClassification(self, classification: str):
        """Return collected detections with the given classification label."""
        return [d for d in self.detections if d.classification == classification]

    def filterByConfidence(self, threshold: float):
        """Return collected detections with confidence at or above ``threshold``."""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        return [d for d in self.detections if d.get_confidence() >= threshold]

    def clearDetections(self):
        """Remove all collected detections."""
        self.detections.clear()
