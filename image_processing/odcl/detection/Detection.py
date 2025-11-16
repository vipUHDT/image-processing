"""
Detection data structures and model wrapper for ODCL.

This module defines the core abstractions for representing individual
detections, aggregating model outputs, and running object detection
via configurable backends. The primary implementation uses SAHI-based
models to perform sliced or standard predictions and converts the
results into internal :class:`Detection` objects with bounding boxes,
centers, and cropped image regions.
"""

from sahi.predict import get_sliced_prediction, get_prediction
import os
import cv2
from sahi.prediction import ObjectPrediction, PredictionResult
from .SahiConfig import SahiConfig
from typing import Optional
import numpy as np
from image_processing.results import ModelResult
from image_processing.tools.hash import hashFile
from sahi.models.base import DetectionModel
from .SahiConfig import SahiDetectionModel, ModelConfig


class Detection:
    """
    Container for a single object detection.

    This class stores classification metadata, confidence, pixel location,
    and optional GPS/time information, along with the full source image
    and an optional cropped region around the detection.

    Parameters
    ----------
    classification : str
        Predicted class label for the detection.
    confidence : float
        Confidence score associated with the detection, expected to be in
        the range [0.0, 1.0].
    pixel_coords : tuple of int
        Pixel coordinates of the detection center in image coordinates,
        typically (x, y).
    image : cv2.typing.MatLike
        The full source image in which the detection was made.
    cropped_image : cv2.typing.MatLike or None, optional
        Cropped image region corresponding to the detection bounding box,
        by default None.
    gps_coords : tuple of float or None, optional
        Optional GPS coordinates (e.g., (latitude, longitude)) associated
        with the detection, by default None.
    timestamp : str or None, optional
        Optional timestamp string associated with the frame or detection,
        by default None.
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
        """
        Return the GPS coordinates associated with this detection.

        Returns
        -------
        tuple of float or None
            GPS coordinates (e.g., (latitude, longitude)) if available,
            otherwise None.
        """
        return self.gps_coords

    def get_pixel_coords(self):
        """
        Return the pixel coordinates of the detection center.

        Returns
        -------
        tuple of int
            Center point (x, y) of the detection in image coordinates.
        """
        return self.pixel_coords

    def get_timestamp(self):
        """
        Return the timestamp associated with this detection.

        Returns
        -------
        str or None
            Timestamp string if available, otherwise None.
        """
        return self.timestamp

    def get_confidence(self):
        """
        Return the confidence score for this detection.

        The confidence is validated to be within [0.0, 1.0].

        Returns
        -------
        float
            Confidence score for the detection.

        Raises
        ------
        ValueError
            If the stored confidence is outside the range [0.0, 1.0].
        """
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return self.confidence

    def get_image(self):
        """
        Return the full source image for this detection.

        Returns
        -------
        cv2.typing.MatLike
            The image in which this detection was made.
        """
        return self.image


class DetectionModelResult(ModelResult):
    """
    Model result that aggregates detections and their source image.

    This extends :class:`ModelResult` by attaching an image and a list of
    :class:`Detection` instances produced by a single model run.

    Parameters
    ----------
    model_name : str or None, optional
        Name or identifier of the detection model, by default None.
    model_hash : str or None, optional
        Hash or version identifier for the model artefact, by default None.
    image : cv2.typing.MatLike or None, optional
        Image associated with the detections, by default None.

    Attributes
    ----------
    image : cv2.typing.MatLike or None
        Image used for the detections.
    detections : list of Detection
        List of detection objects associated with this result.
    """

    def __init__(self, model_name: Optional[str] = None, model_hash: Optional[str] = None, image: Optional[cv2.typing.MatLike] = None):
        super().__init__(model_name, model_hash)
        self.image = image
        self.detections = []
    
    def add(self, detection: Detection):
        """
        Add a detection to the result's detection list.

        Parameters
        ----------
        detection : Detection
            Detection instance to append to the result.
        """
        self.detections.append(detection)


class Detector:
    """
    Detection model wrapper with SAHI-based backend support.

    This class encapsulates configuration, loading, and inference for
    object detection models. The current implementation supports SAHI
    slicing or standard prediction modes via :class:`SahiDetectionModel`,
    and exposes utilities to convert raw predictions into internal
    :class:`Detection` objects.

    Parameters
    ----------
    model_config : ModelConfig or None, optional
        Configuration for the detection model and its backend, including
        model path, type, device, and SAHI-specific slicing parameters.

    Attributes
    ----------
    backend : str or None
        Name of the backend in use (e.g., ``"sahi"``) or None if not set.
    model_config : ModelConfig or None
        Active model configuration.
    model : Any
        Loaded model instance (e.g., :class:`SahiDetectionModel`) once
        :meth:`loadModel` has been called.
    model_path : str or None
        Path to the model artefact. May be used to track or hash the model.
    model_hash : str or None
        Optional hash used to identify the specific model build.
    """
    
    def __init__(self, model_config: Optional[ModelConfig]  = None):
        self.backend = None
        self.model_config: ModelConfig | None = None
        self.model = None
        self.model_path = None
        self.model_hash = None

        self.setModelConfig(model_config)
    
    def setModelConfig(self, model_config: Optional[ModelConfig]):
        """
        Set the model configuration and determine the backend type.

        If the configuration includes a SAHI backend, the backend name
        is set to ``"sahi"``; otherwise, backend is left as None.

        Parameters
        ----------
        model_config : ModelConfig or None
            New model configuration to apply.
        """
        self.model_config = model_config
        if self.model_config and isinstance(self.model_config.backend_config, SahiConfig):
            self.backend = "sahi"
        else:
            self.backend = None
       
    def loadModel(self):
        """
        Load the detection model based on the current configuration.

        Currently, this initializes a :class:`SahiDetectionModel` when the
        backend is ``"sahi"`` and a valid :class:`ModelConfig` is present.
        """
        if isinstance(self.model_config, ModelConfig):
            if self.backend == "sahi":
                self.model = SahiDetectionModel(
                    model_type = self.model_config.model_type,
                    model_path = self.model_config.model_path,
                    confidence_threshold = self.model_config.confidence_threshold,
                    device = self.model_config.device
                )

    def initializeModel(self):
        """
        Warm up the detection model by running a dummy forward pass.

        This can be used to trigger any lazy initialization inside the
        underlying framework (e.g., CUDA context, graph compilation) so
        that the first real inference call is faster.
        """
        h, w = (64, 64)
        dummy = np.zeros((h, w, 3), dtype=np.uint8)
        _ = self.run(dummy)


    def exportVisuals(
        self,
        results: PredictionResult,
        export_dir: str = os.getcwd(),
        file_name: str = "visual.png",
    ):
        """
        Export visualizations of detection results to disk.

        For SAHI backends, this delegates to
        :meth:`sahi.prediction.PredictionResult.export_visuals`.

        Parameters
        ----------
        results : PredictionResult
            Prediction results object produced by SAHI.
        export_dir : str, optional
            Directory where the visualization image will be saved, by default
            the current working directory.
        file_name : str, optional
            File name for the exported visualization image, by default
            ``"visual.png"``.
        """
        if results and self.backend:
            if self.backend == "sahi":
                results.export_visuals(export_dir=export_dir, file_name=file_name)

    def parseResults(self, results: PredictionResult, padding=0) -> tuple[DetectionModelResult, list[Detection]]:
        """
        Convert a :class:`PredictionResult` into internal detection objects.

        This method converts a SAHI :class:`PredictionResult` into a
        :class:`DetectionModelResult` and a list of :class:`Detection`
        instances, optionally expanding bounding boxes by a given padding
        while keeping them within image bounds.

        Parameters
        ----------
        results : PredictionResult
            SAHI prediction results object to parse.
        padding : int, optional
            Number of pixels to expand each bounding box in all directions
            before cropping, by default 0.

        Returns
        -------
        DetectionModelResult
            Aggregated result containing the source image and its detections.
        list of Detection
            Flat list of per-object detection instances created from the
            prediction result.
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
        """
        Run the detection model on an input image.

        For SAHI backends, this either performs sliced prediction or
        standard prediction, depending on :class:`SahiConfig`. Post-processing
        is configured according to the SAHI backend settings.

        Parameters
        ----------
        image : cv2.typing.MatLike
            Input image (e.g., NumPy array) to run detection on.

        Returns
        -------
        PredictionResult or None
            SAHI prediction result object if the model and configuration
            are valid, otherwise None.
        """
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
        returned regardless of the configured backend. If the prediction is
        invalid, None, or cannot be converted, an empty list is returned.

        Args:
            object_prediction (ObjectPrediction | None): The prediction object
                from which to extract the bounding box.

        Returns:
            Optional[tuple[int, int, int, int]]: A list of four float values representing the bounding box
            coordinates `[x_min, y_min, x_max, y_max]`. Returns an empty list if
            no valid bounding box can be obtained.
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
