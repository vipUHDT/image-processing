from sahi.predict import get_sliced_prediction, get_prediction
import os
import cv2
from sahi.prediction import ObjectPrediction, PredictionResult
from .SahiConfig import SahiConfig
from typing import Optional
import numpy as np
class Detection:
    def __init__(
        self,
        classification: str,
        confidence: float,
        pixel_coords: tuple[int, int],
        image: cv2.typing.MatLike,
        cropped_image: cv2.typing.MatLike | None = None,
        gps_coords: tuple[float, float] | None = None,
        timestamp: str | None = None,
    ):
        self.classification = classification
        self.gps_coords = gps_coords
        self.timestamp = timestamp
        self.image = image
        self.pixel_coords = pixel_coords
        self.confidence = confidence
        self.cropped_image = cropped_image

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
    
class Detector:
    def __init__(self, backend="sahi"):
        self.backend = backend
        self.sahi_config: SahiConfig | None = None

    def setSahiConfig(self, sahi_config: SahiConfig):
        self.sahi_config = sahi_config

    def exportVisuals(self, results: PredictionResult, export_dir: str = os.getcwd(), file_name: str = "visual.png"):
        if results and self.backend:
            if self.backend == "sahi":
                results.export_visuals(export_dir=export_dir, file_name=file_name)
    
    def parseResults(self, results: PredictionResult, padding=0) -> list[Detection]:
        detections: list[Detection] = []
        if results and self.backend:
            if self.backend == "sahi":
                for object_prediction in results.object_prediction_list:
                    predicted_classes = object_prediction.category.name
                    confidence_scores = float(object_prediction.score.value)
                    bounding_box = self.getBoundingBox(object_prediction)
                    image = np.array(results.image)
                    width, height = results.image_width, results.image_height
                    adjusted_bounding_box = self.adjustBoundingBox(bounding_box, padding, width, height)
                    cropped_image = self.cropDetection(image, adjusted_bounding_box)
                    center_x, center_y = self.getBoundingBoxCenter(adjusted_bounding_box)
                    cropped_image = self.cropDetection(image, adjusted_bounding_box)
                    detection = Detection(predicted_classes,confidence_scores, (center_x, center_y), image, cropped_image)
                    detections.append(detection)
        return detections



    """
    def saveCroppedDetections(self, results: PredictionResult):
        if results and self.backend:
            if self.backend == "sahi":
                for i in range(len(results.object_prediction_list)):
                    predicted_classes = results.object_prediction_list[i].category
                    confidence_scores = results.object_prediction_list[i].score.value
    """

    def run(self, image: cv2.typing.MatLike) -> Optional[PredictionResult]:
        if self.backend == "sahi" and self.sahi_config:
            if self.sahi_config.slice:
                result = get_sliced_prediction(
                    image,
                    detection_model=self.sahi_config.detection_model,
                    slice_height=self.sahi_config.slice_height,
                    slice_width=self.sahi_config.slice_width,
                    overlap_height_ratio=self.sahi_config.overlap_height_ratio,
                    overlap_width_ratio=self.sahi_config.overlap_width_ratio,
                    perform_standard_pred=self.sahi_config.perform_standard_pred,
                    postprocess_match_metric=self.sahi_config.postprocess_match_metric,
                    postprocess_match_threshold=self.sahi_config.postprocess_match_threshold,
                    postprocess_class_agnostic=self.sahi_config.postprocess_class_agnostic,
                )
            else:
                postprocess_type = self.sahi_config.postprocess_types[self.sahi_config.postprocess_type](
                    match_threshold=self.sahi_config.postprocess_match_threshold,
                    match_metric=self.sahi_config.postprocess_match_metric,
                    class_agnostic=self.sahi_config.postprocess_class_agnostic
                )
                
                result = get_prediction(
                    image=image,
                    detection_model=self.sahi_config.detection_model,
                    postprocess=postprocess_type,
                )

            return result
    
    def cropDetection(self, image: cv2.typing.MatLike, bounding_box: tuple[int, int, int, int]) -> cv2.typing.MatLike:
        """
        Crop a region of interest from an image using a bounding box.

        The bounding box is provided in `[x_min, y_min, x_max, y_max]` format.
        OpenCV images are indexed as `[row, col] = [y, x]`, so the slice order
        is `[y_min:y_max, x_min:x_max]`.

        Args:
            image (cv2.typing.MatLike): The source image as a NumPy array.
            bounding_box (tuple[int, int, int, int]): The bounding box coordinates
                in `[x_min, y_min, x_max, y_max]` format.

        Returns:
            cv2.typing.MatLike: The cropped image region corresponding to the
            bounding box.
        """
        x_min, y_min, x_max, y_max = bounding_box
        cropped_img = image[x_min:x_max, y_min:y_max]
        return cropped_img

    def getBoundingBox(self, object_prediction: ObjectPrediction | None) -> list[float]:
        """
        Return the bounding box for a given object prediction in
        `[x_min, y_min, x_max, y_max]` format.

        This method normalizes bounding box outputs so that the same format is
        returned regardless of the configured backend. If the prediction is
        invalid, None, or cannot be converted, an empty list is returned.

        Args:
            object_prediction (ObjectPrediction | None): The prediction object
                from which to extract the bounding box.

        Returns:
            list[float]: A list of four float values representing the bounding box
            coordinates `[x_min, y_min, x_max, y_max]`. Returns an empty list if
            no valid bounding box can be obtained.
        """
        if self.backend:
            if self.backend == "sahi" and isinstance(object_prediction, ObjectPrediction):
                return object_prediction.bbox.to_voc_bbox()
        return []
    
    def getBoundingBoxCenter(self, bounding_box: list[float]) -> tuple[int | None, int | None]:
        """
        Compute the center point of an object's bounding box.

        The bounding box is first extracted in `[x_min, y_min, x_max, y_max]` format
        using `getBoundingBox`. The center coordinates are then calculated as the
        midpoint of the bounding box edges.

        Args:
            object_prediction (ObjectPrediction | None): The prediction object
                from which to extract the bounding box. If None or invalid, the
                result will be (None, None).

        Returns:
            tuple[float | None, float | None]: A tuple `(center_x, center_y)`
            representing the bounding box center in image coordinates. If no valid
            bounding box is available, returns `(None, None)`.
        """
        center_x, center_y = None, None
        if self.backend:
            if self.backend == "sahi":
                min_x, min_y, max_x, max_y = bounding_box
                center_x = int((min_x + max_x) / 2)
                center_y = int((min_y + max_y) / 2)
        return center_x, center_y

    def adjustBoundingBox(self, bounding_box, padding, img_width, img_height):
        """
        Expand a bounding box by a given padding while ensuring it stays
        within image boundaries.

        The method iteratively applies padding around the bounding box until
        either the requested expansion is applied or further padding would
        exceed the image dimensions. If padding cannot be fully applied,
        it is reduced step by step until a valid box is obtained.

        Args:
            bb (tuple[float, float, float, float]): The original bounding box
                in `[x_min, y_min, x_max, y_max]` format.
            padding (int): The number of pixels to expand the bounding box
                in all directions.
            img_width (int): Width of the image (upper bound for `x_max`).
            img_height (int): Height of the image (upper bound for `y_max`).

        Returns:
            tuple[float, float, float, float]: The adjusted bounding box in
            `[x_min, y_min, x_max, y_max]` format, guaranteed to fit within
            the image dimensions.
        """
        x_min, y_min, x_max, y_max = bounding_box
        while True:
            new_x_min = max(x_min - padding, 0)
            new_y_min = max(y_min - padding, 0)
            new_x_max = min(x_max + padding, img_width)
            new_y_max = min(y_max + padding, img_height)

            if (
                new_x_min == x_min
                and new_y_min == y_min
                and new_x_max == x_max
                and new_y_max == y_max
            ):
                break

            x_min, y_min, x_max, y_max = new_x_min, new_y_min, new_x_max, new_y_max
            padding -= 1

        return (int(new_x_min), int(new_y_min), int(new_x_max), int(new_y_max))
