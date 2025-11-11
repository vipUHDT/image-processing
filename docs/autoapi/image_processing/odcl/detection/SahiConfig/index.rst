image_processing.odcl.detection.SahiConfig
==========================================

.. py:module:: image_processing.odcl.detection.SahiConfig


Classes
-------

.. autoapisummary::

   image_processing.odcl.detection.SahiConfig.SahiDetectionModel
   image_processing.odcl.detection.SahiConfig.SahiConfig
   image_processing.odcl.detection.SahiConfig.ModelConfig


Module Contents
---------------

.. py:class:: SahiDetectionModel(*, model_type: str, model_path: str | None = None, model: Any | None = None, config_path: str | None = None, device: str = 'cpu', mask_threshold: float | None = None, confidence_threshold: float | None = None, category_mapping: dict[str, str] | None = None, category_remapping: dict[str, int] | None = None, load_at_init: bool | None = None, image_size: int | None = None, **kwargs: Any)

   Bases: :py:obj:`sahi.AutoDetectionModel`


   Loads a DetectionModel from given path.

   :param model_type: str
                      Name of the detection framework (example: "ultralytics", "huggingface", "torchvision")
   :param model_path: str
                      Path of the detection model (ex. 'model.pt')
   :param model: Any
                 A pre-initialized model instance, if available
   :param config_path: str
                       Path of the config file (ex. 'mmdet/configs/cascade_rcnn_r50_fpn_1x.py')
   :param device: str
                  Device, "cpu" or "cuda:0"
   :param mask_threshold: float
                          Value to threshold mask pixels, should be between 0 and 1
   :param confidence_threshold: float
                                All predictions with score < confidence_threshold will be discarded
   :param category_mapping: dict: str to str
                            Mapping from category id (str) to category name (str) e.g. {"1": "pedestrian"}
   :param category_remapping: dict: str to int
                              Remap category ids based on category names, after performing inference e.g. {"car": 3}
   :param load_at_init: bool
                        If True, automatically loads the model at initialization
   :param image_size: int
                      Inference input size.

   :returns: Returns an instance of a DetectionModel

   :raises ImportError: If given {model_type} framework is not installed


.. py:class:: SahiConfig

   Configuration for image slicing and post-processing used in SAHI inference.

   :param slice: Whether to enable image slicing before prediction.
   :type slice: bool, default=True
   :param slice_height: Height of each image slice in pixels.
   :type slice_height: int, default=640
   :param slice_width: Width of each image slice in pixels.
   :type slice_width: int, default=640
   :param overlap_height_ratio: Fractional vertical overlap between adjacent slices.
   :type overlap_height_ratio: float, default=0.11
   :param overlap_width_ratio: Fractional horizontal overlap between adjacent slices.
   :type overlap_width_ratio: float, default=0.11
   :param perform_standard_pred: Whether to also perform full-image prediction in addition to sliced inference.
   :type perform_standard_pred: bool, default=True
   :param postprocess_types: Mapping of available post-processing algorithms by name.
   :type postprocess_types: dict of {str: Type[PostprocessPredictions]}
   :param postprocess_type: Name of the post-processing method to use.
   :type postprocess_type: str, default="GreedyNMMPostprocess"
   :param postprocess_match_metric: Metric for merging overlapping predictions (e.g., "IOU", "IOS").
   :type postprocess_match_metric: str, default="IOU"
   :param postprocess_match_threshold: Threshold for merging predictions based on the chosen metric.
   :type postprocess_match_threshold: float, default=0.5
   :param postprocess_class_agnostic: If True, ignore class labels when merging overlapping predictions.
   :type postprocess_class_agnostic: bool, default=True
   :param single_prediction: Whether to limit output to a single prediction per detected object.
   :type single_prediction: bool, default=True


   .. py:attribute:: slice
      :type:  bool
      :value: True



   .. py:attribute:: slice_height
      :type:  int
      :value: 640



   .. py:attribute:: slice_width
      :type:  int
      :value: 640



   .. py:attribute:: overlap_height_ratio
      :type:  float
      :value: 0.11



   .. py:attribute:: overlap_width_ratio
      :type:  float
      :value: 0.11



   .. py:attribute:: perform_standard_pred
      :type:  bool
      :value: True



   .. py:attribute:: postprocess_types
      :type:  Dict[str, Type[sahi.postprocess.combine.PostprocessPredictions]]


   .. py:attribute:: postprocess_type
      :type:  str
      :value: 'GreedyNMMPostprocess'



   .. py:attribute:: postprocess_match_metric
      :type:  str
      :value: 'IOU'



   .. py:attribute:: postprocess_match_threshold
      :type:  float
      :value: 0.5



   .. py:attribute:: postprocess_class_agnostic
      :type:  bool
      :value: True



   .. py:attribute:: single_prediction
      :type:  bool
      :value: True



.. py:class:: ModelConfig

   Model configuration for object-detection inference.

   :param backend: Name of the inference backend (e.g., "onnxruntime", "torch").
   :type backend: str
   :param model_type: Type or architecture of the model (e.g., "YOLOv8", "EfficientDet").
   :type model_type: str
   :param model_path: Filesystem path or URI to the trained model weights.
   :type model_path: str
   :param confidence_threshold: Minimum confidence score required to retain detections.
   :type confidence_threshold: float
   :param device: Compute device to use for inference (e.g., "cuda:0", "cpu").
   :type device: str
   :param backend_config: Additional backend-specific configuration parameters or SAHI slicing setup.
   :type backend_config: dict or SahiConfig


   .. py:attribute:: backend
      :type:  str


   .. py:attribute:: model_type
      :type:  str


   .. py:attribute:: model_path
      :type:  str


   .. py:attribute:: confidence_threshold
      :type:  float


   .. py:attribute:: device
      :type:  str


   .. py:attribute:: backend_config
      :type:  Dict[str, str] | SahiConfig


