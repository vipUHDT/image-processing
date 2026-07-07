"""Configuration dataclasses and model factory for SAHI-based detection."""

from dataclasses import dataclass, field
from typing import Any, Dict, Type, overload

from sahi import AutoDetectionModel
from sahi.models.base import DetectionModel
from sahi.postprocess.combine import (
    GreedyNMMPostprocess,
    LSNMSPostprocess,
    NMMPostprocess,
    NMSPostprocess,
    PostprocessPredictions,
)


class SahiDetectionModel(AutoDetectionModel):
    """
    Loads a DetectionModel from given path.

    Args:
        model_type: str
            Name of the detection framework (example: "ultralytics", "huggingface", "torchvision")
        model_path: str
            Path of the detection model (ex. 'model.pt')
        model: Any
            A pre-initialized model instance, if available
        config_path: str
            Path of the config file (ex. 'mmdet/configs/cascade_rcnn_r50_fpn_1x.py')
        device: str
            Device, "cpu" or "cuda:0"
        mask_threshold: float
            Value to threshold mask pixels, should be between 0 and 1
        confidence_threshold: float
            All predictions with score < confidence_threshold will be discarded
        category_mapping: dict: str to str
            Mapping from category id (str) to category name (str) e.g. {"1": "pedestrian"}
        category_remapping: dict: str to int
            Remap category ids based on category names, after performing inference e.g. {"car": 3}
        load_at_init: bool
            If True, automatically loads the model at initialization
        image_size: int
            Inference input size.

    Returns:
        Returns an instance of a DetectionModel

    Raises:
        ImportError: If given {model_type} framework is not installed
    """
    @overload
    def __new__(
        cls,
        *,
        model_type: str,
        model_path: str | None = None,
        model: Any | None = None,
        config_path: str | None = None,
        device: str = "cpu",
        mask_threshold: float | None = None,
        confidence_threshold: float | None = None,
        category_mapping: dict[str, str] | None = None,
        category_remapping: dict[str, int] | None = None,
        load_at_init: bool | None = None,
        image_size: int | None = None,
        **kwargs: Any,
    ) -> DetectionModel: ...
    

    def __new__(cls, *args: Any, **kwargs: Any) -> DetectionModel:
        return AutoDetectionModel.from_pretrained(*args, **kwargs)

    
    def __init__(
        self,
        *,
        model_type: str,
        model_path: str | None = None,
        model: Any | None = None,
        config_path: str | None = None,
        device: str = "cpu",
        mask_threshold: float | None = None,
        confidence_threshold: float | None = None,
        category_mapping: dict[str, str] | None = None,
        category_remapping: dict[str, int] | None = None,
        load_at_init: bool | None = None,
        image_size: int | None = None,
        **kwargs: Any,
    ) -> None:
        pass

@dataclass
class SahiConfig:
    """
    Configuration for image slicing and post-processing used in SAHI inference.

    Parameters
    ----------
    slice : bool, default=True
        Whether to enable image slicing before prediction.
    slice_height : int, default=640
        Height of each image slice in pixels.
    slice_width : int, default=640
        Width of each image slice in pixels.
    overlap_height_ratio : float, default=0.11
        Fractional vertical overlap between adjacent slices.
    overlap_width_ratio : float, default=0.11
        Fractional horizontal overlap between adjacent slices.
    perform_standard_pred : bool, default=True
        Whether to also perform full-image prediction in addition to sliced inference.
    postprocess_types : dict of {str: Type[PostprocessPredictions]}
        Mapping of available post-processing algorithms by name.
    postprocess_type : str, default="GreedyNMMPostprocess"
        Name of the post-processing method to use.
    postprocess_match_metric : str, default="IOU"
        Metric for merging overlapping predictions (e.g., "IOU", "IOS").
    postprocess_match_threshold : float, default=0.5
        Threshold for merging predictions based on the chosen metric.
    postprocess_class_agnostic : bool, default=True
        If True, ignore class labels when merging overlapping predictions.
    single_prediction : bool, default=True
        Whether to limit output to a single prediction per detected object.
    """
    slice: bool = True
    slice_height: int = 640
    slice_width: int = 640
    overlap_height_ratio: float = 0.11
    overlap_width_ratio: float = 0.11
    perform_standard_pred: bool = True
    postprocess_types: Dict[str, Type[PostprocessPredictions]] = field(
        default_factory=lambda: {
            "GreedyNMMPostprocess": GreedyNMMPostprocess,
            "LSNMSPostprocess": LSNMSPostprocess,
            "NMMPostprocess": NMMPostprocess,
            "NMSPostprocess": NMSPostprocess,
        }
    )
    postprocess_type: str = 'GreedyNMMPostprocess'
    postprocess_match_metric: str = "IOU"
    postprocess_match_threshold: float = 0.5
    postprocess_class_agnostic: bool = True
    single_prediction: bool =True

@dataclass
class ModelConfig:
    """
    Model configuration for object-detection inference.

    Parameters
    ----------
    backend : str
        Name of the inference backend (e.g., "onnxruntime", "torch").
    model_type : str
        Type or architecture of the model (e.g., "YOLOv8", "EfficientDet").
    model_path : str
        Filesystem path or URI to the trained model weights.
    confidence_threshold : float
        Minimum confidence score required to retain detections.
    device : str
        Compute device to use for inference (e.g., "cuda:0", "cpu").
    backend_config : dict or SahiConfig
        Additional backend-specific configuration parameters or SAHI slicing setup.
    """
    backend: str
    model_type: str
    model_path: str
    confidence_threshold: float
    device: str
    backend_config: Dict[str, str] | SahiConfig

