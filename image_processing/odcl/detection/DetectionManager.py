import cv2
from image_processing.odcl.Localize import *
from .SahiConfig import SahiConfig
from image_processing.camera import *
from image_processing.odcl.Localize import *
from .Detection import *

class DetectionManager:
    def __init__(self, detection_backend, detector: Detector, camera_metadata: CameraMetadata | None = None, georeference_engine: Georeference_Engine | None = None):
        self.detections = []
        self.duplicate_threshold = 2
        self.detector: Detector | None = detector
        self.detection_backend = detection_backend
        self.sahi_config: SahiConfig | None = None
        self.platform_state = PlatformState()
        self.camera: CameraMetadata | None = camera_metadata
        self.georeference_engine = georeference_engine

    def addDetection(self, detection: Detection):
        is_duplicate = False
        if isinstance(self.georeference_engine, Georeference_Engine) and isinstance(self.camera, CameraMetadata):
            detection.gps_coords = self.georeference(detection.pixel_coords, self.platform_state, self.camera, self.georeference_engine.altitude_offset)
        for existing_detection in self.detections:
            if detection.gps_coords and abs(haversine(detection.gps_coords[0], detection.gps_coords[1], existing_detection.gps_coords[0], existing_detection.gps_coords[1])) < self.duplicate_threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            self.detections.append(detection)
    
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
                parsed_results = self.detector.parseResults(results)
                self.addDetections(parsed_results)
                
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
