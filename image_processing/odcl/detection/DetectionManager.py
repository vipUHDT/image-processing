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
        self.updateDetections()
        self.updateResults()

    
    def updateResults(self):
        try:
            result = self.results_queue.get_nowait()
        except Empty:
            pass
        else:
            self.results.append(result)

    def updateDetections(self):
        try:
            detection = self.detections_queue.get_nowait()
        except Empty:
            pass
        else:
            print(detection.gps_coords)
            self.gps_queue.put(detection.gps_coords)
            self.detections.append(detection)

    
    def getGPS(self):
        if self.gps_queue.qsize() > 0:
            return self.gps_queue.get()
        else:
            return None



    
    def queueImage(self, image: QueuedImage):
        self.image_queue.put(image)

    def processQueuedImages(self):
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
        self.active_threads = [ t for t in self.active_threads if t.is_alive()]

    def processQueuedImage(self, queued_image: QueuedImage):
        image = queued_image.image
        platform_state = queued_image.platform_state
        self.ODCL(image, platform_state)

    def addResult(self, result: DetectionModelResult):
        self.results_queue.put(result)

    def addDetection(self, detection: Detection, platform_state: PlatformState):
        if isinstance(self.georeference_engine, Georeference_Engine) and isinstance(self.camera, CameraMetadata):
            detection.gps_coords = self.georeference(detection.pixel_coords, platform_state, self.camera, self.georeference_engine.altitude_offset)
        
        if not self.checkForDuplicates(detection):
            self.gps_queue.put(detection.gps_coords)
            self.detections_queue.put(detection)
    
    def checkForDuplicates(self, detection: Detection):
        for existing_detection in self.detections:
            if detection.gps_coords and abs(haversine(detection.gps_coords[0], detection.gps_coords[1], existing_detection.gps_coords[0], existing_detection.gps_coords[1])) < self.duplicate_threshold:
                return True
    
    def setGeoreferenceEngine(self, georeference_backend, altitude_offset = 0):
        self.georeference_engine = Georeference_Engine(georeference_backend, altitude_offset)

    def georeference(self, target_pixel_coordinates, platform_state, camera_metadata, altitude_offset):
        if self.georeference_engine:
            return self.georeference_engine.georeference(target_pixel_coordinates, platform_state, camera_metadata, altitude_offset)
    
    def addDetections(self, detections: list[Detection], platform_state: PlatformState):
        for detection in detections:
            self.addDetection(detection, platform_state)

    def ODCL(self, image, platform_state):
        detector = Detector(self.detection_model_config)
        detector.loadModel()
        if isinstance(detector, Detector):
            results = detector.run(image)
            if isinstance(results, PredictionResult):
                detection_model_result, detections = detector.parseResults(results)
                self.addResult(detection_model_result)
                self.addDetections(detections, platform_state)
                
    def getAllDetections(self):
        return self.detections

    def filterByClassification(self, classification: str):
        return [
            d
            for d in self.detections
            if d.classify_object(classification) == classification
        ]

    def filterByConfidence(self, threshold: float):
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        return [d for d in self.detections if d.get_confidence() >= threshold]

    def clearDetections(self):
        self.detections.clear()