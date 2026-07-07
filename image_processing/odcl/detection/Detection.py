"""Object detection primitives built on SAHI (sliced inference)."""

import os
from typing import Optional

import cv2
import numpy as np
from sahi.predict import get_prediction, get_sliced_prediction
from sahi.prediction import ObjectPrediction, PredictionResult

from image_processing.results import ModelResult

from .SahiConfig import ModelConfig, SahiConfig, SahiDetectionModel


class Detection:
    """
    A single detected object with its location and provenance.

    Parameters
    ----------
    classification : str
        Predicted class label.
    confidence : float
        Prediction confidence in ``[0, 1]``.
    pixel_coords : tuple[int, int]
        Center of the detection's bounding box in image coordinates.
    image : cv2.typing.MatLike
        Full source image the detection came from.
    cropped_image : cv2.typing.MatLike, optional
        Crop of the detection's bounding box.
    gps_coords : tuple[float, float], optional
        Georeferenced position, filled in by ``DetectionManager``.
    timestamp : str, optional
        Capture timestamp.
    """

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


class DetectionModelResult(ModelResult):
    """All detections produced by one model run on one image."""

    def __init__(self, model_name: Optional[str] = None, model_hash: Optional[str] = None, image: Optional[cv2.typing.MatLike] = None):
        super().__init__(model_name, model_hash)
        self.image = image
        self.detections = []

    def add(self, detection: Detection):
        """Append a detection to this result."""
        self.detections.append(detection)


class Detector:
    """
    Runs object-detection inference through a configured backend (currently SAHI).

    Parameters
    ----------
    model_config : ModelConfig, optional
        Model and backend configuration. A ``SahiConfig`` backend config
        selects the SAHI backend.
    """

    def __init__(self, model_config: Optional[ModelConfig]  = None):
        self.backend = None
        self.model_config: ModelConfig | None = None
        self.model = None
        self.model_path = None
        self.model_hash = None

        self.setModelConfig(model_config)
    
    def setModelConfig(self, model_config: Optional[ModelConfig]):
        """Set the model configuration and derive the backend from it."""
        self.model_config = model_config
        if self.model_config and isinstance(self.model_config.backend_config, SahiConfig):
            self.backend = "sahi"
        else:
            self.backend = None
       
    def loadModel(self):
        """Instantiate the detection model from the current configuration."""
        if isinstance(self.model_config, ModelConfig):
            if self.backend == "sahi":
                self.model = SahiDetectionModel(
                    model_type = self.model_config.model_type,
                    model_path = self.model_config.model_path,
                    confidence_threshold = self.model_config.confidence_threshold,
                    device = self.model_config.device
                )

    def initializeModel(self):
        """Warm up the model with a dummy inference to trigger lazy initialization."""
        h, w = (64, 64)
        dummy = np.zeros((h, w, 3), dtype=np.uint8)
        _ = self.run(dummy)


    def exportVisuals(
        self,
        results: PredictionResult,
        export_dir: str = os.getcwd(),
        file_name: str = "visual.png",
    ):
        """Export the backend's annotated visualization of ``results`` to disk."""
        if results and self.backend:
            if self.backend == "sahi":
                results.export_visuals(export_dir=export_dir, file_name=file_name)

    def parseResults(self, results: PredictionResult, padding=0) -> tuple[DetectionModelResult, list[Detection]]:
        """
        Convert backend predictions into ``Detection`` objects.

        Parameters
        ----------
        results : PredictionResult
            Raw backend output from ``run``.
        padding : int, optional
            Pixels of padding applied around each bounding box before
            cropping (clamped to the image bounds).

        Returns
        -------
        tuple[DetectionModelResult, list[Detection]]
            The aggregate result and the individual detections.
        """
        detections: list[Detection] = []
        detection_model_result = DetectionModelResult(self.model_path, self.model_hash)
        if results and self.backend:
            if self.backend == "sahi":
                image = np.array(results.image)
                H, W = image.shape[:2]
                detection_model_result.image = image
                for object_prediction in results.object_prediction_list:
                    predicted_classes = object_prediction.category.name
                    confidence_scores = float(object_prediction.score.value)
                    shifted_object_prediction = (
                        object_prediction.get_shifted_object_prediction()
                    )
                    bounding_box = self.getBoundingBox(shifted_object_prediction)


                    if bounding_box:
                        if padding:
                            bounding_box = self.adjustBoundingBox(
                                bounding_box, padding, W, H
                            )

                        cropped_image = self.cropDetection(image, bounding_box)
                        detection_center = self.getBoundingBoxCenter(bounding_box)

                        detection = Detection(
                            predicted_classes,
                            confidence_scores,
                            detection_center,
                            image,
                            cropped_image,
                        )
                        detection_model_result.add(detection)
                        detections.append(detection)
        return detection_model_result, detections

    def run(self, image: cv2.typing.MatLike) -> Optional[PredictionResult]:
        """Run inference on an image, sliced or whole per the backend config."""
        if self.model_config:
            if self.backend == "sahi":
                sahi_config = self.model_config.backend_config
                if isinstance(sahi_config, SahiConfig):
                    if sahi_config.slice:
                        result = get_sliced_prediction(
                            image,
                            detection_model=self.model,
                            slice_height=sahi_config.slice_height,
                            slice_width=sahi_config.slice_width,
                            overlap_height_ratio=sahi_config.overlap_height_ratio,
                            overlap_width_ratio=sahi_config.overlap_width_ratio,
                            perform_standard_pred=sahi_config.perform_standard_pred,
                            postprocess_match_metric=sahi_config.postprocess_match_metric,
                            postprocess_match_threshold=sahi_config.postprocess_match_threshold,
                            postprocess_class_agnostic=sahi_config.postprocess_class_agnostic,
                        )
                    else:
                        postprocess_type = sahi_config.postprocess_types[
                            sahi_config.postprocess_type
                        ](
                            match_threshold=sahi_config.postprocess_match_threshold,
                            match_metric=sahi_config.postprocess_match_metric,
                            class_agnostic=sahi_config.postprocess_class_agnostic,
                        )
                        result = get_prediction(
                            image=image,
                            detection_model=self.model,
                            postprocess=postprocess_type,
                        )
                    return result
        return None

    def cropDetection(
        self, image: cv2.typing.MatLike, bounding_box: tuple[int, int, int, int]
    ) -> cv2.typing.MatLike:
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
        cropped_img = image[y_min:y_max, x_min:x_max]
        return cropped_img

    def getBoundingBox(self, object_prediction: ObjectPrediction | None) -> Optional[tuple[int, int, int, int]]:
        """
        Return the bounding box for a given object prediction in
        `[x_min, y_min, x_max, y_max]` format.

        This method normalizes bounding box outputs so that the same format is
        returned regardless of the configured backend.

        Args:
            object_prediction (ObjectPrediction | None): The prediction object
                from which to extract the bounding box.

        Returns:
            Optional[tuple[int, int, int, int]]: The bounding box coordinates
            `(x_min, y_min, x_max, y_max)`, or None if no valid bounding box
            can be obtained.
        """
        if self.backend:
            if self.backend == "sahi" and isinstance(
                object_prediction, ObjectPrediction
            ):
                bounding_box =  object_prediction.bbox.to_xyxy()
                if bounding_box:
                    return int(bounding_box[0]), int(bounding_box[1]), int(bounding_box[2]), int(bounding_box[3])
        return None

    def getBoundingBoxCenter(
        self, bounding_box: tuple[int, int, int, int]
    ) -> tuple[int, int]:
        """
        Compute the center point of a bounding box.

        Args:
            bounding_box (tuple[int, int, int, int]): Bounding box in
                `(x_min, y_min, x_max, y_max)` format.

        Returns:
            tuple[int, int]: The `(center_x, center_y)` of the box in image
            coordinates, or `(-1, -1)` when no backend is configured.
        """
        center_x, center_y = None, None
        if self.backend:
            if self.backend == "sahi":
                min_x, min_y, max_x, max_y = bounding_box
                center_x = int((min_x + max_x) / 2)
                center_y = int((min_y + max_y) / 2)
                return center_x, center_y
        return (-1, -1)

    def adjustBoundingBox(
        self,
        bounding_box: tuple[int, int, int, int],
        padding: int,
        img_width: int,
        img_height: int,
    ) -> tuple[int, int, int, int]:
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
