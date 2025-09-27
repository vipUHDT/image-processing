import cv2
class Detection():
    
    def __init__(self, classification: str, gps_coords: tuple[float, float], timestamp: str, image: cv2.typing.MatLike,
                 pixel_coords: tuple[int, int], confidence: float):
        self.classification = classification
        self.gps_coords = gps_coords
        self.timestamp = timestamp
        self.image = image
        self.pixel_coords = pixel_coords
        self.confidence = confidence

    def classify_object(self, classification: str):
        return self.classification
    
    def get_gps_coords(self):
        return self.gps_coords
    
    def get_pixel_coords(self):
        return self.pixel_coords
    
    def get_timestamp(self):
        return self.timestamp
    
    def get_confidence(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return self.confidence
    
    def get_image(self):
        return self.image
    

class DetectionManager():
    def __init__(self):
        self.detections = []
    
    def add_detection(self, detection: Detection):
        self.detections.append(detection)
    
    def get_all_detections(self):
        return self.detections
    
    def filter_by_classification(self, classification: str):
        return [d for d in self.detections if d.classify_object(classification) == classification]
    
    def filter_by_confidence(self, threshold: float):
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        return [d for d in self.detections if d.get_confidence() >= threshold]
    
    def clear_detections(self):
        self.detections.clear()
    
    