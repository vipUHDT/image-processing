import cv2
from image_processing.odcl.Localize import *
from .SahiConfig import SahiConfig
from image_processing.camera import *
from image_processing.odcl.Localize import *
from .Detection import *
from queue import Queue
from image_processing import QueuedImage, PlatformState
import threading

class DetectionManager:
    def __init__(self, detection_backend, detector: Detector, camera_metadata: CameraMetadata | None = None, georeference_engine: Georeference_Engine | None = None):
        self.image_queue = Queue()
        self.detections_queue = Queue()
        self.results_queue = Queue()
        self.gps_queue = Queue()
        self.active_threads: list[threading.Thread] = []
        self.detections = []
        self.workers = 5
        self.max_concurrent_images = 10
        self.duplicate_threshold = 2
        self.detector: Detector | None = detector
        self.detection_backend = detection_backend
        self.sahi_config: SahiConfig | None = None
        self.platform_state = PlatformState()
        self.camera: CameraMetadata | None = camera_metadata
        self.georeference_engine = georeference_engine
        self.terminated = False

        if detector:
            detector.initializeModel()

    
    def queueImage(self, image: QueuedImage):
        self.image_queue.put(image)

    def processQueue(self):
        self.pruneThreads()
        if (self.image_queue.qsize() > 0):
            for i in range(self.max_concurrent_images):
                if len(self.active_threads) < self.max_concurrent_images:
                    queued_image = self.image_queue.get()
                    if queued_image:
                        t = threading.Thread(
                            target=self.processQueuedImage,
                            args=((queued_image,)),
                            daemon=True,
                            name="DetectionManager"
                        )
                        t.start()
                        self.active_threads.append(t)


    def pruneThreads(self):
        self.active_threads = [ t for t in self.active_threads if t.is_alive()]

    def processQueuedImage(self, queued_image: QueuedImage):
        image = queued_image.image
        platform_state = queued_image.platform_state
        self.ODCL(image, platform_state)

    def addResult(self, result: DetectionModelResult):
        self.results_queue.put(result)

    def addDetection(self, detection: Detection):
        if isinstance(self.georeference_engine, Georeference_Engine) and isinstance(self.camera, CameraMetadata):
            detection.gps_coords = self.georeference(detection.pixel_coords, self.platform_state, self.camera, self.georeference_engine.altitude_offset)
        
        if not self.checkForDuplicates(detection):
            self.gps_queue.put(detection.gps_coords)
            self.detections.append(detection)
    
    def checkForDuplicates(self, detection: Detection):
        for existing_detection in self.detections:
            if detection.gps_coords and abs(haversine(detection.gps_coords[0], detection.gps_coords[1], existing_detection.gps_coords[0], existing_detection.gps_coords[1])) < self.duplicate_threshold:
                return True
    
    def setSahiConfig(self, sahi_config: SahiConfig):
        self.sahi_config = sahi_config

    def setBackend(self, detection_backend):
        valid_backends = ["sahi"]
        if detection_backend in valid_backends:
            self.detection_backend = detection_backend
    
    def setGeoreferenceEngine(self, georeference_backend, altitude_offset = 0):
        self.georeference_engine = Georeference_Engine(georeference_backend, altitude_offset)

    def georeference(self, target_pixel_coordinates, platform_state, camera_metadata, altitude_offset):
        if self.georeference_engine:
            return self.georeference_engine.georeference(target_pixel_coordinates, platform_state, camera_metadata, altitude_offset)

    def initializeDetector(self):
        self.detector = Detector(self.detection_backend)
        if self.sahi_config:
            self.detector.setSahiConfig(self.sahi_config)
    
    def addDetections(self, detections: list[Detection]):
        for detection in detections:
            self.addDetection(detection)

    def ODCL(self, image, platform_state):
        self.platform_state.altitude, self.platform_state.latitude, self.platform_state.longitude, self.platform_state.pitch, self.platform_state.yaw, self.platform_state.roll = astuple(platform_state)
        if isinstance(self.detector, Detector):
            results = self.detector.run(image)
            if isinstance(results, PredictionResult):
                detection_model_result, detections = self.detector.parseResults(results)
                self.addResult(detection_model_result)
                self.addDetections(detections)
                
    def processGPSQueue(self):
        gps_coords = []
        while (self.gps_queue.qsize() > 0):
            gps_coords.append(self.gps_queue.get())
            if len(gps_coords) > 10:
                break
        return gps_coords



        


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