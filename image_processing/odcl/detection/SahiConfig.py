from sahi import AutoDetectionModel
from sahi.postprocess.combine import (
    GreedyNMMPostprocess,
    LSNMSPostprocess,
    NMMPostprocess,
    NMSPostprocess,
    PostprocessPredictions,
)

from dataclasses import dataclass, field
from typing import Dict, Type, Any, overload
from sahi.models.base import DetectionModel
from sahi import AutoDetectionModel

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
    detection_model: DetectionModel
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

