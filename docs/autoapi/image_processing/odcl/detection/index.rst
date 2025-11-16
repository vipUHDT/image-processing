image_processing.odcl.detection
===============================

.. py:module:: image_processing.odcl.detection

.. autoapi-nested-parse::

   Detection module for the ODCL

   This subpackage provides:

   - Low-level detection data structures (:class:`Detection`,
     :class:`DetectionModelResult`)
   - The high-level detection manager (:class:`DetectionManager`) that
     manages queued inference, threading, duplicate suppression, and
     georeferencing integration
   - SAHI-based model configuration utilities (:class:`SahiConfig`,
     :class:`ModelConfig`, and :class:`SahiDetectionModel`)

   The public API is defined in :data:`__all__` for clarity and for proper
   export during Sphinx documentation generation.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/image_processing/odcl/detection/Detection/index
   /autoapi/image_processing/odcl/detection/DetectionManager/index
   /autoapi/image_processing/odcl/detection/SahiConfig/index


Classes
-------

.. autoapisummary::

   image_processing.odcl.detection.SahiConfig
   image_processing.odcl.detection.ModelResult
   image_processing.odcl.detection.SahiDetectionModel
   image_processing.odcl.detection.ModelConfig
   image_processing.odcl.detection.Detection
   image_processing.odcl.detection.DetectionModelResult
   image_processing.odcl.detection.Detector
   image_processing.odcl.detection.SahiConfig
   image_processing.odcl.detection.QueuedImage
   image_processing.odcl.detection.PlatformState
   image_processing.odcl.detection.SahiDetectionModel
   image_processing.odcl.detection.DetectionManager
   image_processing.odcl.detection.Georeference_Engine
   image_processing.odcl.detection.Camera
   image_processing.odcl.detection.CameraBackend
   image_processing.odcl.detection.CameraMetadata
   image_processing.odcl.detection.ModelResult
   image_processing.odcl.detection.ModelConfig
   image_processing.odcl.detection.Detection
   image_processing.odcl.detection.DetectionModelResult
   image_processing.odcl.detection.Detector
   image_processing.odcl.detection.SahiDetectionModel
   image_processing.odcl.detection.SahiConfig
   image_processing.odcl.detection.ModelConfig


Functions
---------

.. autoapisummary::

   image_processing.odcl.detection.hashFile
   image_processing.odcl.detection.georeference_utm
   image_processing.odcl.detection.georeference_enu
   image_processing.odcl.detection.georeference_aeqd
   image_processing.odcl.detection.georeference_manual
   image_processing.odcl.detection.haversine
   image_processing.odcl.detection.constructGstreamerPipeline
   image_processing.odcl.detection.hashFile


Package Contents
----------------

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



.. py:class:: ModelResult(model_name: Optional[str] = None, model_hash: Optional[str] = None)

   Bases: :py:obj:`abc.ABC`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: model_name
      :value: None



   .. py:attribute:: model_hash
      :value: None



.. py:function:: hashFile(file_path: str, algorithm: str = 'md5', chunk_size: int = 8192) -> str

   Compute a cryptographic hash of a file using streaming (chunked) reads.

   :param file_path: Path to the file to hash.
   :type file_path: str
   :param algorithm: Hash algorithm to use. Must be supported by `hashlib.new`
                     (e.g., "md5", "sha1", "sha256", "sha512"). Default is "md5".
   :type algorithm: str, optional
   :param chunk_size: Number of bytes to read per iteration. Larger values improve
                      performance for large files but use more memory. Default is 8192.
   :type chunk_size: int, optional

   :returns: Hexadecimal digest string representing the computed hash.
   :rtype: str

   :raises ValueError: If an unsupported hashing algorithm is provided.
   :raises FileNotFoundError: If the target file does not exist.
   :raises PermissionError: If the file cannot be opened or read.

   .. rubric:: Notes

   - File contents are processed in a memory-efficient streaming manner.
   - The returned digest is deterministic for a given `algorithm`.


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


.. py:class:: Detection(classification: str, confidence: float, pixel_coords: tuple[int, int], image: cv2.typing.MatLike, cropped_image: cv2.typing.MatLike | None = None, gps_coords: tuple[float, float] | None = None, timestamp: str | None = None)

   Container for a single object detection.

   This class stores classification metadata, confidence, pixel location,
   and optional GPS/time information, along with the full source image
   and an optional cropped region around the detection.

   :param classification: Predicted class label for the detection.
   :type classification: str
   :param confidence: Confidence score associated with the detection, expected to be in
                      the range [0.0, 1.0].
   :type confidence: float
   :param pixel_coords: Pixel coordinates of the detection center in image coordinates,
                        typically (x, y).
   :type pixel_coords: tuple of int
   :param image: The full source image in which the detection was made.
   :type image: cv2.typing.MatLike
   :param cropped_image: Cropped image region corresponding to the detection bounding box,
                         by default None.
   :type cropped_image: cv2.typing.MatLike or None, optional
   :param gps_coords: Optional GPS coordinates (e.g., (latitude, longitude)) associated
                      with the detection, by default None.
   :type gps_coords: tuple of float or None, optional
   :param timestamp: Optional timestamp string associated with the frame or detection,
                     by default None.
   :type timestamp: str or None, optional


   .. py:attribute:: classification


   .. py:attribute:: gps_coords
      :value: None



   .. py:attribute:: timestamp
      :value: None



   .. py:attribute:: image


   .. py:attribute:: pixel_coords


   .. py:attribute:: confidence


   .. py:attribute:: cropped_image
      :value: None



   .. py:method:: get_gps_coords()

      Return the GPS coordinates associated with this detection.

      :returns: GPS coordinates (e.g., (latitude, longitude)) if available,
                otherwise None.
      :rtype: tuple of float or None



   .. py:method:: get_pixel_coords()

      Return the pixel coordinates of the detection center.

      :returns: Center point (x, y) of the detection in image coordinates.
      :rtype: tuple of int



   .. py:method:: get_timestamp()

      Return the timestamp associated with this detection.

      :returns: Timestamp string if available, otherwise None.
      :rtype: str or None



   .. py:method:: get_confidence()

      Return the confidence score for this detection.

      The confidence is validated to be within [0.0, 1.0].

      :returns: Confidence score for the detection.
      :rtype: float

      :raises ValueError: If the stored confidence is outside the range [0.0, 1.0].



   .. py:method:: get_image()

      Return the full source image for this detection.

      :returns: The image in which this detection was made.
      :rtype: cv2.typing.MatLike



.. py:class:: DetectionModelResult(model_name: Optional[str] = None, model_hash: Optional[str] = None, image: Optional[cv2.typing.MatLike] = None)

   Bases: :py:obj:`image_processing.results.ModelResult`


   Model result that aggregates detections and their source image.

   This extends :class:`ModelResult` by attaching an image and a list of
   :class:`Detection` instances produced by a single model run.

   :param model_name: Name or identifier of the detection model, by default None.
   :type model_name: str or None, optional
   :param model_hash: Hash or version identifier for the model artefact, by default None.
   :type model_hash: str or None, optional
   :param image: Image associated with the detections, by default None.
   :type image: cv2.typing.MatLike or None, optional

   .. attribute:: image

      Image used for the detections.

      :type: cv2.typing.MatLike or None

   .. attribute:: detections

      List of detection objects associated with this result.

      :type: list of Detection


   .. py:attribute:: image
      :value: None



   .. py:attribute:: detections
      :value: []



   .. py:method:: add(detection: Detection)

      Add a detection to the result's detection list.

      :param detection: Detection instance to append to the result.
      :type detection: Detection



.. py:class:: Detector(model_config: Optional[image_processing.odcl.detection.SahiConfig.ModelConfig] = None)

   Detection model wrapper with SAHI-based backend support.

   This class encapsulates configuration, loading, and inference for
   object detection models. The current implementation supports SAHI
   slicing or standard prediction modes via :class:`SahiDetectionModel`,
   and exposes utilities to convert raw predictions into internal
   :class:`Detection` objects.

   :param model_config: Configuration for the detection model and its backend, including
                        model path, type, device, and SAHI-specific slicing parameters.
   :type model_config: ModelConfig or None, optional

   .. attribute:: backend

      Name of the backend in use (e.g., ``"sahi"``) or None if not set.

      :type: str or None

   .. attribute:: model_config

      Active model configuration.

      :type: ModelConfig or None

   .. attribute:: model

      Loaded model instance (e.g., :class:`SahiDetectionModel`) once
      :meth:`loadModel` has been called.

      :type: Any

   .. attribute:: model_path

      Path to the model artefact. May be used to track or hash the model.

      :type: str or None

   .. attribute:: model_hash

      Optional hash used to identify the specific model build.

      :type: str or None


   .. py:attribute:: backend
      :value: None



   .. py:attribute:: model_config
      :type:  image_processing.odcl.detection.SahiConfig.ModelConfig | None
      :value: None



   .. py:attribute:: model
      :value: None



   .. py:attribute:: model_path
      :value: None



   .. py:attribute:: model_hash
      :value: None



   .. py:method:: setModelConfig(model_config: Optional[image_processing.odcl.detection.SahiConfig.ModelConfig])

      Set the model configuration and determine the backend type.

      If the configuration includes a SAHI backend, the backend name
      is set to ``"sahi"``; otherwise, backend is left as None.

      :param model_config: New model configuration to apply.
      :type model_config: ModelConfig or None



   .. py:method:: loadModel()

      Load the detection model based on the current configuration.

      Currently, this initializes a :class:`SahiDetectionModel` when the
      backend is ``"sahi"`` and a valid :class:`ModelConfig` is present.



   .. py:method:: initializeModel()

      Warm up the detection model by running a dummy forward pass.

      This can be used to trigger any lazy initialization inside the
      underlying framework (e.g., CUDA context, graph compilation) so
      that the first real inference call is faster.



   .. py:method:: exportVisuals(results: sahi.prediction.PredictionResult, export_dir: str = os.getcwd(), file_name: str = 'visual.png')

      Export visualizations of detection results to disk.

      For SAHI backends, this delegates to
      :meth:`sahi.prediction.PredictionResult.export_visuals`.

      :param results: Prediction results object produced by SAHI.
      :type results: PredictionResult
      :param export_dir: Directory where the visualization image will be saved, by default
                         the current working directory.
      :type export_dir: str, optional
      :param file_name: File name for the exported visualization image, by default
                        ``"visual.png"``.
      :type file_name: str, optional



   .. py:method:: parseResults(results: sahi.prediction.PredictionResult, padding=0) -> tuple[DetectionModelResult, list[Detection]]

      Convert a :class:`PredictionResult` into internal detection objects.

      This method converts a SAHI :class:`PredictionResult` into a
      :class:`DetectionModelResult` and a list of :class:`Detection`
      instances, optionally expanding bounding boxes by a given padding
      while keeping them within image bounds.

      :param results: SAHI prediction results object to parse.
      :type results: PredictionResult
      :param padding: Number of pixels to expand each bounding box in all directions
                      before cropping, by default 0.
      :type padding: int, optional

      :returns: * *DetectionModelResult* -- Aggregated result containing the source image and its detections.
                * *list of Detection* -- Flat list of per-object detection instances created from the
                  prediction result.



   .. py:method:: run(image: cv2.typing.MatLike) -> Optional[sahi.prediction.PredictionResult]

      Run the detection model on an input image.

      For SAHI backends, this either performs sliced prediction or
      standard prediction, depending on :class:`SahiConfig`. Post-processing
      is configured according to the SAHI backend settings.

      :param image: Input image (e.g., NumPy array) to run detection on.
      :type image: cv2.typing.MatLike

      :returns: SAHI prediction result object if the model and configuration
                are valid, otherwise None.
      :rtype: PredictionResult or None



   .. py:method:: cropDetection(image: cv2.typing.MatLike, bounding_box: tuple[int, int, int, int]) -> cv2.typing.MatLike

      Crop a region of interest from an image using a bounding box.

      The bounding box is provided in `[x_min, y_min, x_max, y_max]` format.
      OpenCV images are indexed as `[row, col] = [y, x]`, so the slice order
      is `[y_min:y_max, x_min:x_max]`.

      :param image: The source image as a NumPy array.
      :type image: cv2.typing.MatLike
      :param bounding_box: The bounding box coordinates
                           in `[x_min, y_min, x_max, y_max]` format.
      :type bounding_box: tuple[int, int, int, int]

      :returns: The cropped image region corresponding to the
                bounding box.
      :rtype: cv2.typing.MatLike



   .. py:method:: getBoundingBox(object_prediction: sahi.prediction.ObjectPrediction | None) -> Optional[tuple[int, int, int, int]]

      Return the bounding box for a given object prediction in
      `[x_min, y_min, x_max, y_max]` format.

      This method normalizes bounding box outputs so that the same format is
      returned regardless of the configured backend. If the prediction is
      invalid, None, or cannot be converted, an empty list is returned.

      :param object_prediction: The prediction object
                                from which to extract the bounding box.
      :type object_prediction: ObjectPrediction | None

      :returns: A list of four float values representing the bounding box
                coordinates `[x_min, y_min, x_max, y_max]`. Returns an empty list if
                no valid bounding box can be obtained.
      :rtype: Optional[tuple[int, int, int, int]]



   .. py:method:: getBoundingBoxCenter(bounding_box: tuple[int, int, int, int]) -> tuple[int, int]

      Compute the center point of an object's bounding box.

      The bounding box is first extracted in `[x_min, y_min, x_max, y_max]` format
      using `getBoundingBox`. The center coordinates are then calculated as the
      midpoint of the bounding box edges.

      :param object_prediction: The prediction object
                                from which to extract the bounding box. If None or invalid, the
                                result will be (None, None).
      :type object_prediction: ObjectPrediction | None

      :returns: A tuple `(center_x, center_y)`
                representing the bounding box center in image coordinates. If no valid
                bounding box is available, returns `(None, None)`.
      :rtype: tuple[float | None, float | None]



   .. py:method:: adjustBoundingBox(bounding_box: tuple[int, int, int, int], padding: int, img_width: int, img_height: int) -> tuple[int, int, int, int]

      Expand a bounding box by a given padding while ensuring it stays
      within image boundaries.

      The method iteratively applies padding around the bounding box until
      either the requested expansion is applied or further padding would
      exceed the image dimensions. If padding cannot be fully applied,
      it is reduced step by step until a valid box is obtained.

      :param bb: The original bounding box
                 in `[x_min, y_min, x_max, y_max]` format.
      :type bb: tuple[float, float, float, float]
      :param padding: The number of pixels to expand the bounding box
                      in all directions.
      :type padding: int
      :param img_width: Width of the image (upper bound for `x_max`).
      :type img_width: int
      :param img_height: Height of the image (upper bound for `y_max`).
      :type img_height: int

      :returns: The adjusted bounding box in
                `[x_min, y_min, x_max, y_max]` format, guaranteed to fit within
                the image dimensions.
      :rtype: tuple[float, float, float, float]



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



.. py:class:: QueuedImage

   Container for an image paired with the corresponding platform state,
   used for asynchronous or batched image processing pipelines.

   :param image: The captured image frame (BGR or grayscale), typically originating
                 from a live stream or logged dataset.
   :type image: cv2.typing.MatLike
   :param platform_state: The telemetry and attitude state at the time of image acquisition.
   :type platform_state: PlatformState

   .. rubric:: Notes

   Instances of this type are typically passed into worker queues inside
   :class:`~image_processing.odcl.detection.DetectionManager`.


   .. py:attribute:: image
      :type:  cv2.typing.MatLike


   .. py:attribute:: platform_state
      :type:  PlatformState


.. py:class:: PlatformState

   Platform telemetry and attitude state associated with an image capture
   event or detection cycle.

   This structure is intended to be populated from onboard sensors
   (e.g., GNSS, IMU) or log data, and used by geolocation functions to
   project pixel detections into Earth-referenced coordinates.

   :param altitude: Platform altitude above ground level in meters.
   :type altitude: float, optional
   :param latitude: Geographic latitude (positive north) in decimal degrees.
   :type latitude: float, optional
   :param longitude: Geographic longitude (positive east) in decimal degrees.
   :type longitude: float, optional
   :param pitch: Platform pitch angle in degrees (positive nose-up).
   :type pitch: float, optional
   :param yaw: Platform yaw/heading angle in degrees (0° = North, +CW).
   :type yaw: float, optional
   :param roll: Platform roll angle in degrees (positive right-wing-down).
   :type roll: float, optional


   .. py:attribute:: altitude
      :type:  Optional[float]
      :value: None



   .. py:attribute:: latitude
      :type:  Optional[float]
      :value: None



   .. py:attribute:: longitude
      :type:  Optional[float]
      :value: None



   .. py:attribute:: pitch
      :type:  Optional[float]
      :value: None



   .. py:attribute:: yaw
      :type:  Optional[float]
      :value: None



   .. py:attribute:: roll
      :type:  Optional[float]
      :value: None



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


.. py:class:: DetectionManager(detection_model_config: Optional[image_processing.odcl.detection.Detection.ModelConfig] = None, camera_metadata: image_processing.odcl.Localize.CameraMetadata | None = None, georeference_engine: image_processing.odcl.Localize.Georeference_Engine | None = None)

   Manager for running detection and localization on queued images.

   This class maintains several queues (images, detections, results, GPS)
   and a pool of worker threads that process images as they arrive. For
   each queued image, it runs ODCL via a :class:`Detector`, converts
   detections into GPS coordinates using a :class:`Georeference_Engine`
   and :class:`CameraMetadata`, and stores unique detections based on
   spatial proximity.

   :param detection_model_config: Configuration used to construct the underlying detection model.
   :type detection_model_config: ModelConfig or None, optional
   :param camera_metadata: Intrinsic camera metadata used for georeferencing, if available.
   :type camera_metadata: CameraMetadata or None, optional
   :param georeference_engine: Georeferencing engine responsible for converting pixel coordinates
                               into GPS coordinates.
   :type georeference_engine: Georeference_Engine or None, optional

   .. attribute:: detection_model_config

      Detection model configuration.

      :type: ModelConfig or None

   .. attribute:: image_queue

      Queue of :class:`QueuedImage` instances to be processed.

      :type: queue.Queue

   .. attribute:: detections_queue

      Queue of detections produced by worker threads.

      :type: queue.Queue

   .. attribute:: results_queue

      Queue of :class:`DetectionModelResult` instances, one per processed image.

      :type: queue.Queue

   .. attribute:: gps_queue

      Queue of GPS coordinates (from georeferenced detections).

      :type: queue.Queue

   .. attribute:: detections

      Accumulated list of all detections processed so far.

      :type: list of Detection

   .. attribute:: results

      Accumulated list of model results.

      :type: list of DetectionModelResult

   .. attribute:: active_threads

      Currently running worker threads.

      :type: list of threading.Thread

   .. attribute:: workers

      Maximum number of worker threads used to process queued images.

      :type: int

   .. attribute:: max_concurrent_queue_process

      Upper bound for how many queued items may be processed at once
      (currently not enforced directly in this implementation).

      :type: int

   .. attribute:: duplicate_threshold

      Spatial threshold (in the units of `haversine`) used to treat two
      detections as duplicates.

      :type: float

   .. attribute:: camera

      Camera metadata used for georeferencing.

      :type: CameraMetadata or None

   .. attribute:: georeference_engine

      Engine used to convert pixel coordinates to GPS.

      :type: Georeference_Engine or None

   .. attribute:: terminated

      Flag that can be used to mark the manager as shut down.

      :type: bool


   .. py:attribute:: detection_model_config
      :value: None



   .. py:attribute:: image_queue


   .. py:attribute:: detections_queue


   .. py:attribute:: results_queue


   .. py:attribute:: gps_queue


   .. py:attribute:: detections
      :value: []



   .. py:attribute:: results
      :value: []



   .. py:attribute:: active_threads
      :type:  list[threading.Thread]
      :value: []



   .. py:attribute:: workers
      :value: 5



   .. py:attribute:: max_concurrent_queue_process
      :value: 10



   .. py:attribute:: duplicate_threshold
      :value: 2



   .. py:attribute:: camera
      :type:  image_processing.odcl.Localize.CameraMetadata | None
      :value: None



   .. py:attribute:: georeference_engine
      :value: None



   .. py:attribute:: terminated
      :value: False



   .. py:method:: update()

      Poll internal queues and update detection and result lists.

      This method should be called periodically (e.g., in a main loop)
      to move items from internal queues into the `detections` and
      `results` lists.



   .. py:method:: updateResults()

      Move a single queued result (if any) into the `results` list.

      Uses a non-blocking queue get; if no item is available, this
      method returns immediately.



   .. py:method:: updateDetections()

      Move a single queued detection (if any) into the `detections` list.

      Detected GPS coordinates are also forwarded into the `gps_queue`
      for separate retrieval.



   .. py:method:: getGPS()

      Retrieve a single GPS coordinate from the GPS queue, if available.

      :returns: Next GPS entry from the queue, or None if the queue is empty.
      :rtype: Any or None



   .. py:method:: queueImage(image: image_processing.QueuedImage)

      Enqueue an image (and platform state) for detection processing.

      :param image: Object containing an image and associated platform state to be
                    processed by ODCL.
      :type image: QueuedImage



   .. py:method:: processQueuedImages()

      Spawn worker threads to process queued images.

      This method prunes inactive threads and, while there are items in
      the image queue and fewer than `workers` active threads, pops
      images and launches new threads targeting :meth:`processQueuedImage`.



   .. py:method:: processGPSQueue()

      Drain up to 10 GPS entries from the GPS queue.

      :returns: List of GPS coordinate entries retrieved from the queue
                (up to a maximum of 10 items).
      :rtype: list



   .. py:method:: pruneThreads()

      Remove inactive worker threads from the internal tracking list.



   .. py:method:: processQueuedImage(queued_image: image_processing.QueuedImage)

      Process a single queued image by running ODCL.

      :param queued_image: Object containing an image and corresponding platform state.
      :type queued_image: QueuedImage



   .. py:method:: addResult(result: image_processing.odcl.detection.Detection.DetectionModelResult)

      Enqueue a model result for later retrieval.

      :param result: Result object containing image-level detection information.
      :type result: DetectionModelResult



   .. py:method:: addDetection(detection: image_processing.odcl.detection.Detection.Detection, platform_state: image_processing.PlatformState)

      Add a single detection, optionally georeferencing and deduplicating.

      If a georeference engine and camera metadata are configured, the
      detection's pixel coordinates are converted into GPS coordinates.
      Detections within `duplicate_threshold` distance (in `haversine`
      units) of existing detections are discarded.

      :param detection: Detection object to process and potentially enqueue.
      :type detection: Detection
      :param platform_state: Platform/vehicle state at the time of detection, used for
                             georeferencing.
      :type platform_state: PlatformState



   .. py:method:: checkForDuplicates(detection: image_processing.odcl.detection.Detection.Detection)

      Check if a detection is a spatial duplicate of an existing one.

      Two detections are considered duplicates if the `haversine` distance
      between their GPS locations is less than :attr:`duplicate_threshold`.

      :param detection: Detection to compare against previously recorded detections.
      :type detection: Detection

      :returns: True if a sufficiently close detection already exists,
                otherwise False.
      :rtype: bool



   .. py:method:: setGeoreferenceEngine(georeference_backend, altitude_offset=0)

      Initialize and attach a georeference engine.

      :param georeference_backend: Backend implementation used by :class:`Georeference_Engine`.
      :type georeference_backend: Any
      :param altitude_offset: Altitude offset passed to the georeference engine, by default 0.
      :type altitude_offset: float, optional



   .. py:method:: georeference(target_pixel_coordinates, platform_state, camera_metadata, altitude_offset)

      Convert pixel coordinates into GPS coordinates using the georeference engine.

      :param target_pixel_coordinates: Target pixel coordinates (e.g., (x, y)) in image space.
      :type target_pixel_coordinates: Any
      :param platform_state: Platform/vehicle state associated with this frame.
      :type platform_state: PlatformState
      :param camera_metadata: Intrinsic camera metadata required for georeferencing.
      :type camera_metadata: CameraMetadata
      :param altitude_offset: Altitude offset parameter passed to the georeference engine.
      :type altitude_offset: float

      :returns: Georeferenced coordinates, as returned by the georeference engine.
      :rtype: Any



   .. py:method:: addDetections(detections: list[image_processing.odcl.detection.Detection.Detection], platform_state: image_processing.PlatformState)

      Add and process a list of detections for a given platform state.

      :param detections: List of detection objects to process.
      :type detections: list of Detection
      :param platform_state: Platform/vehicle state corresponding to these detections.
      :type platform_state: PlatformState



   .. py:method:: ODCL(image, platform_state)

      Run the full ODCL pipeline on a single image and platform state.

      This constructs a :class:`Detector` using the configured model
      config, loads the model, performs detection on the provided image,
      parses the results into :class:`Detection` objects, and queues
      results and detections for later retrieval.

      :param image: Image (e.g., NumPy array) on which to run detection.
      :type image: Any
      :param platform_state: Platform/vehicle state at the time of the image acquisition.
      :type platform_state: PlatformState



   .. py:method:: getAllDetections()

      Return the list of all detections processed so far.

      :returns: All stored detections.
      :rtype: list of Detection



   .. py:method:: filterByClassification(classification: str)

      Filter detections by classification label.

      This assumes that each :class:`Detection` implements a
      ``classify_object`` method that can be used to check the
      classification label.

      :param classification: Class label to filter by.
      :type classification: str

      :returns: Detections whose `classify_object` result matches the
                requested classification.
      :rtype: list of Detection



   .. py:method:: filterByConfidence(threshold: float)

      Filter detections by confidence threshold.

      :param threshold: Minimum confidence required for a detection to be included.
                        Must be in the range [0.0, 1.0].
      :type threshold: float

      :returns: Detections whose confidence score is greater than or equal
                to `threshold`.
      :rtype: list of Detection

      :raises ValueError: If `threshold` is outside the range [0.0, 1.0].



   .. py:method:: clearDetections()

      Clear all stored detections from memory.

      This does not affect queued detections or results.



.. py:class:: Georeference_Engine(backend, altitude_offset=0)

   Engine for converting pixel coordinates into GPS coordinates.

   This class selects one of several backend functions for georeferencing
   (e.g., UTM, ENU, azimuthal-equidistant, or manual) and calls it with
   a unified interface based on platform state and camera metadata.

   :param backend: Name of the georeferencing backend to use. Must be one of
                   ``"utm"``, ``"enu"``, ``"aeqd"``, or ``"manual"``.
   :type backend: str
   :param altitude_offset: Offset applied to the drone altitude prior to computing the ground
                           footprint, by default 0.
   :type altitude_offset: float, optional

   .. attribute:: camera_metadata

      Optional camera metadata (not directly used in current implementation).

      :type: CameraMetadata or None

   .. attribute:: backend

      Selected backend function implementing georeferencing logic.

      :type: callable

   .. attribute:: altitude_offset

      Stored altitude offset passed through to the backend.

      :type: float


   .. py:attribute:: camera_metadata
      :value: None



   .. py:attribute:: backend


   .. py:attribute:: altitude_offset
      :value: 0



   .. py:method:: getBackends(backend)

      Resolve a backend name into a georeferencing function.

      :param backend: Name of the georeferencing backend (``"utm"``, ``"enu"``,
                      ``"aeqd"``, or ``"manual"``).
      :type backend: str

      :returns: Backend function implementing the requested georeference method.
      :rtype: callable

      :raises ValueError: If an unknown backend name is provided.



   .. py:method:: georeference(target_pixel_coordinates: tuple[int, int], platform_state: image_processing.PlatformState, camera_metadata: image_processing.camera.CameraMetadata, altitude_offset=0)

      Georeference a pixel coordinate into latitude/longitude.

      This method unpacks platform state and camera metadata into the
      arguments expected by the configured backend, and returns the
      resulting GPS coordinates.

      :param target_pixel_coordinates: Pixel coordinates :math:`(x, y)` of the target in image space.
      :type target_pixel_coordinates: tuple of int
      :param platform_state: Platform (drone) state containing altitude, latitude, longitude,
                             pitch, yaw, and roll (in that order).
      :type platform_state: PlatformState
      :param camera_metadata: Camera metadata containing sensor dimensions, image resolution,
                              and focal length.
      :type camera_metadata: CameraMetadata
      :param altitude_offset: Offset to subtract from platform altitude before computing
                              ground footprint, by default 0.
      :type altitude_offset: float, optional

      :returns: Target latitude and longitude in degrees.
      :rtype: tuple of float



.. py:function:: georeference_utm(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

   Georeference using a UTM projection.

   This backend:

   1. Computes camera field-of-view (FOV) from sensor size and focal length:

      .. math::

         \text{FOV}_x = 2 \arctan\left( \frac{w}{2 f} \right), \quad
         \text{FOV}_y = 2 \arctan\left( \frac{h}{2 f} \right).

   2. Computes the ground footprint width/height at altitude:

      .. math::

         W = 2 h \tan\left( \frac{\text{FOV}_x}{2} \right), \quad
         H = 2 h \tan\left( \frac{\text{FOV}_y}{2} \right).

   3. Converts drone lat/lon to UTM, applies pixel-based offsets scaled
      to :math:`W, H` and rotated by yaw, and converts back to WGS84
      coordinates.

   :param target_pixel_coordinates: Target pixel coordinates :math:`(x, y)` in image space.
   :type target_pixel_coordinates: tuple of int
   :param drone_latitude: Drone latitude in degrees.
   :type drone_latitude: float
   :param drone_longitude: Drone longitude in degrees.
   :type drone_longitude: float
   :param drone_altitude: Drone altitude above ground/sea level (units consistent with offset).
   :type drone_altitude: float
   :param altitude_offset: Altitude offset to subtract before computing footprint.
   :type altitude_offset: float
   :param drone_yaw: Drone yaw (heading) in degrees.
   :type drone_yaw: float
   :param sensor_w: Sensor width (same units as :paramref:`focal_length`).
   :type sensor_w: float
   :param sensor_h: Sensor height (same units as :paramref:`focal_length`).
   :type sensor_h: float
   :param pix_width: Image width in pixels.
   :type pix_width: int
   :param pix_height: Image height in pixels.
   :type pix_height: int
   :param focal_length: Camera focal length (same units as :paramref:`sensor_w` and
                        :paramref:`sensor_h`).
   :type focal_length: float

   :returns: Target latitude and longitude in degrees.
   :rtype: tuple of float


.. py:function:: georeference_enu(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

   Georeference using a local ENU (East–North–Up) frame.

   This backend:

   - Computes FOV and footprint size as in :func:`georeference_utm`.
   - Converts pixel offsets (relative to image center) into meters.
   - Rotates those offsets by yaw into ENU directions.
   - Uses :func:`pymap3d.enu2geodetic` to convert ENU offsets to
     latitude/longitude.

   :param target_pixel_coordinates: Target pixel coordinates :math:`(x, y)` in image space.
   :type target_pixel_coordinates: tuple of int
   :param drone_latitude: Drone latitude in degrees.
   :type drone_latitude: float
   :param drone_longitude: Drone longitude in degrees.
   :type drone_longitude: float
   :param drone_altitude: Drone altitude above reference.
   :type drone_altitude: float
   :param altitude_offset: Altitude offset to subtract before computing footprint.
   :type altitude_offset: float
   :param drone_yaw: Drone yaw (heading) in degrees.
   :type drone_yaw: float
   :param sensor_w: Sensor width (same units as :paramref:`focal_length`).
   :type sensor_w: float
   :param sensor_h: Sensor height (same units as :paramref:`focal_length`).
   :type sensor_h: float
   :param pix_width: Image width in pixels.
   :type pix_width: int
   :param pix_height: Image height in pixels.
   :type pix_height: int
   :param focal_length: Camera focal length.
   :type focal_length: float

   :returns: Target latitude and longitude in degrees.
   :rtype: tuple of float


.. py:function:: georeference_aeqd(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

   Georeference using a local Azimuthal Equidistant projection.

   This backend constructs an azimuthal equidistant (AEQD) projection
   centered on the drone position, performs all offsets in that local
   metric space, and converts back to WGS84 coordinates.

   :param target_pixel_coordinates: Target pixel coordinates :math:`(x, y)` in image space.
   :type target_pixel_coordinates: tuple of int
   :param drone_latitude: Drone latitude in degrees.
   :type drone_latitude: float
   :param drone_longitude: Drone longitude in degrees.
   :type drone_longitude: float
   :param drone_altitude: Drone altitude above reference.
   :type drone_altitude: float
   :param altitude_offset: Altitude offset to subtract before computing footprint.
   :type altitude_offset: float
   :param drone_yaw: Drone yaw (heading) in degrees.
   :type drone_yaw: float
   :param sensor_w: Sensor width.
   :type sensor_w: float
   :param sensor_h: Sensor height.
   :type sensor_h: float
   :param pix_width: Image width in pixels.
   :type pix_width: int
   :param pix_height: Image height in pixels.
   :type pix_height: int
   :param focal_length: Camera focal length.
   :type focal_length: float

   :returns: Target latitude and longitude in degrees.
   :rtype: tuple of float


.. py:function:: georeference_manual(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

   Georeference using a simple manual flat-earth approximation.

   This backend uses a constant meters-per-degree approximation to convert
   camera-plane offsets to latitude and longitude. It is less accurate at
   large distances or high latitudes, but is simple and lightweight.

   Specifically:

   .. math::

      \Delta \varphi \approx \frac{y_{\text{meters}}}{R_\varphi}, \quad
      \Delta \lambda \approx \frac{x_{\text{meters}}}{R_\lambda \cos \varphi},

   where :math:`R_\varphi \approx R_\lambda \approx 111319.944` meters
   per degree near the equator.

   :param target_pixel_coordinates: Target pixel coordinates :math:`(x, y)` in image space.
   :type target_pixel_coordinates: tuple of int
   :param drone_latitude: Drone latitude in degrees.
   :type drone_latitude: float
   :param drone_longitude: Drone longitude in degrees.
   :type drone_longitude: float
   :param drone_altitude: Drone altitude above reference.
   :type drone_altitude: float
   :param altitude_offset: Altitude offset to subtract before computing footprint.
   :type altitude_offset: float
   :param drone_yaw: Drone yaw (heading) in degrees.
   :type drone_yaw: float
   :param sensor_w: Sensor width.
   :type sensor_w: float
   :param sensor_h: Sensor height.
   :type sensor_h: float
   :param pix_width: Image width in pixels.
   :type pix_width: int
   :param pix_height: Image height in pixels.
   :type pix_height: int
   :param focal_length: Camera focal length.
   :type focal_length: float

   :returns: Target latitude and longitude in degrees.
   :rtype: tuple of float


.. py:function:: haversine(lat1, lon1, lat2, lon2)

   Compute great-circle distance between two GPS points using the haversine formula.

   The haversine distance on a sphere of radius :math:`R` is:

   .. math::

      d = 2 R \arctan2\left(
          \sqrt{a},
          \sqrt{1 - a}
      \right),

   where

   .. math::

      a = \sin^2\left( \frac{\Delta\varphi}{2} \right)
        + \cos \varphi_1 \cos \varphi_2 \sin^2\left( \frac{\Delta\lambda}{2} \right),

   and :math:`\Delta\varphi` and :math:`\Delta\lambda` are latitude and
   longitude differences in radians. This implementation uses
   :math:`R = 6371` km and returns distance in meters.

   :param lat1: Latitude of the first point in degrees.
   :type lat1: float
   :param lon1: Longitude of the first point in degrees.
   :type lon1: float
   :param lat2: Latitude of the second point in degrees.
   :type lat2: float
   :param lon2: Longitude of the second point in degrees.
   :type lon2: float

   :returns: Great-circle distance between the two points in meters.
   :rtype: float


.. py:class:: Camera(name: str, metadata: Optional[CameraMetadata] = None)

   Bases: :py:obj:`abc.ABC`


   Abstract representation of a camera device.

   This class manages common properties such as the camera name,
   associated backend, connection credentials, and optional
   metadata. Concrete subclasses must implement :meth:`captureFrame`
   to define how a frame is acquired.

   :param name: Logical name or identifier for the camera instance.
   :type name: str
   :param metadata: Intrinsic parameters and resolution for the camera, if known.
   :type metadata: CameraMetadata, optional


   .. py:attribute:: name


   .. py:attribute:: backend
      :value: None



   .. py:attribute:: resolution
      :value: None



   .. py:attribute:: gstreamer_pipeline
      :value: None



   .. py:attribute:: client
      :type:  None | str
      :value: None



   .. py:attribute:: host
      :type:  None | str
      :value: None



   .. py:attribute:: username
      :type:  None | str
      :value: None



   .. py:attribute:: password
      :type:  None | str
      :value: None



   .. py:attribute:: metadata
      :type:  Optional[CameraMetadata]
      :value: None



   .. py:method:: setBackend(backend)

      Select and configure the camera backend by name.

      The backend string is validated against a list of supported
      backend identifiers and, if valid, the corresponding backend
      instance is created.

      :param backend: Name of the backend to use (e.g., ``"rb5"``).
      :type backend: str

      :raises ValueError: If the requested backend is not in the list of supported
          backends.



   .. py:method:: getBackend(backend)

      Instantiate and return a backend by name.

      This helper imports the backend factory from
      ``image_processing.camera.backends`` and constructs a backend
      instance corresponding to the given identifier.

      :param backend: Name of the backend to retrieve.
      :type backend: str

      :returns: The instantiated backend associated with the given name.
      :rtype: CameraBackend



   .. py:method:: setConnection(client, host, username, password)

      Set connection parameters and propagate them to the backend.

      :param client: Identifier or role of the current client (e.g., local host name).
      :type client: str
      :param host: Hostname or IP address of the remote device or service.
      :type host: str
      :param username: Username used for authentication with the remote endpoint.
      :type username: str
      :param password: Password or token used for authentication with the remote endpoint.
      :type password: str



   .. py:method:: connect()

      Establish a connection through the configured backend.

      This method uses the connection credentials stored on the
      camera instance to instruct the backend to establish a session
      (e.g., network connection) required for frame acquisition.



   .. py:method:: initialize()

      Initialize the backend prior to frame capture.

      If a backend is configured, this method forwards the call to
      :meth:`CameraBackend.initialize` so that all required resources
      are ready before capturing frames.



   .. py:method:: captureFrame()
      :abstractmethod:


      Capture a single frame from the camera.

      Concrete subclasses must implement this method to define how
      a frame is acquired from the underlying backend.

      :returns: The captured frame object. The exact type depends on the
                backend and implementation (e.g., NumPy array, raw bytes).
      :rtype: Any



.. py:class:: CameraBackend

   Bases: :py:obj:`abc.ABC`


   Abstract base class for camera backends.

   Concrete implementations wrap specific camera hardware or
   streaming sources (e.g., RB5, remote cameras) and provide a
   unified interface for initialization and connection handling.


   .. py:method:: initialize() -> None
      :abstractmethod:


      Perform backend initialization before capturing frames.

      This method is intended for tasks such as opening device
      handles, starting pipelines, or validating configuration
      prior to streaming.



   .. py:method:: setConnection(client: str, host: str, username: str, password: str) -> None
      :abstractmethod:


      Configure connection parameters for the backend.

      :param client: Identifier or role of the current client (e.g., local host name
                     or logical client type).
      :type client: str
      :param host: Hostname or IP address of the remote device or service.
      :type host: str
      :param username: Username used for authentication with the remote endpoint.
      :type username: str
      :param password: Password or token used for authentication with the remote endpoint.
      :type password: str



   .. py:method:: connect() -> None
      :abstractmethod:


      Establish a connection using the configured parameters.

      Implementations should use the connection parameters provided via
      :meth:`setConnection` to open network sessions, SSH tunnels, or any
      other transport needed for frame acquisition.



.. py:class:: CameraMetadata

   Structured container for intrinsic camera properties.

   :param sensor_width: Physical width of the image sensor in mm.
   :type sensor_width: float
   :param sensor_height: Physical height of the image sensor in mm.
   :type sensor_height: float
   :param image_width: Horizontal resolution of captured images in pixels.
   :type image_width: int
   :param image_height: Vertical resolution of captured images in pixels.
   :type image_height: int
   :param focal_length: Focal length of the lens, expressed in millimeters or equivalent units.
   :type focal_length: int


   .. py:attribute:: sensor_width
      :type:  float


   .. py:attribute:: sensor_height
      :type:  float


   .. py:attribute:: image_width
      :type:  int


   .. py:attribute:: image_height
      :type:  int


   .. py:attribute:: focal_length
      :type:  int


.. py:function:: constructGstreamerPipeline(pipeline: tuple) -> str

   Construct a GStreamer pipeline string from a tuple of elements.

   The elements in the input tuple are joined with the ``" ! "`` separator
   to form a valid GStreamer pipeline description.

   :param pipeline: Ordered sequence of GStreamer elements (e.g., caps, sources,
                    converters, sinks).
   :type pipeline: tuple of str

   :returns: GStreamer pipeline string suitable for use with GStreamer-based
             APIs.
   :rtype: str


.. py:class:: ModelResult(model_name: Optional[str] = None, model_hash: Optional[str] = None)

   Bases: :py:obj:`abc.ABC`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: model_name
      :value: None



   .. py:attribute:: model_hash
      :value: None



.. py:function:: hashFile(file_path: str, algorithm: str = 'md5', chunk_size: int = 8192) -> str

   Compute a cryptographic hash of a file using streaming (chunked) reads.

   :param file_path: Path to the file to hash.
   :type file_path: str
   :param algorithm: Hash algorithm to use. Must be supported by `hashlib.new`
                     (e.g., "md5", "sha1", "sha256", "sha512"). Default is "md5".
   :type algorithm: str, optional
   :param chunk_size: Number of bytes to read per iteration. Larger values improve
                      performance for large files but use more memory. Default is 8192.
   :type chunk_size: int, optional

   :returns: Hexadecimal digest string representing the computed hash.
   :rtype: str

   :raises ValueError: If an unsupported hashing algorithm is provided.
   :raises FileNotFoundError: If the target file does not exist.
   :raises PermissionError: If the file cannot be opened or read.

   .. rubric:: Notes

   - File contents are processed in a memory-efficient streaming manner.
   - The returned digest is deterministic for a given `algorithm`.


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


.. py:class:: Detection(classification: str, confidence: float, pixel_coords: tuple[int, int], image: cv2.typing.MatLike, cropped_image: cv2.typing.MatLike | None = None, gps_coords: tuple[float, float] | None = None, timestamp: str | None = None)

   Container for a single object detection.

   This class stores classification metadata, confidence, pixel location,
   and optional GPS/time information, along with the full source image
   and an optional cropped region around the detection.

   :param classification: Predicted class label for the detection.
   :type classification: str
   :param confidence: Confidence score associated with the detection, expected to be in
                      the range [0.0, 1.0].
   :type confidence: float
   :param pixel_coords: Pixel coordinates of the detection center in image coordinates,
                        typically (x, y).
   :type pixel_coords: tuple of int
   :param image: The full source image in which the detection was made.
   :type image: cv2.typing.MatLike
   :param cropped_image: Cropped image region corresponding to the detection bounding box,
                         by default None.
   :type cropped_image: cv2.typing.MatLike or None, optional
   :param gps_coords: Optional GPS coordinates (e.g., (latitude, longitude)) associated
                      with the detection, by default None.
   :type gps_coords: tuple of float or None, optional
   :param timestamp: Optional timestamp string associated with the frame or detection,
                     by default None.
   :type timestamp: str or None, optional


   .. py:attribute:: classification


   .. py:attribute:: gps_coords
      :value: None



   .. py:attribute:: timestamp
      :value: None



   .. py:attribute:: image


   .. py:attribute:: pixel_coords


   .. py:attribute:: confidence


   .. py:attribute:: cropped_image
      :value: None



   .. py:method:: get_gps_coords()

      Return the GPS coordinates associated with this detection.

      :returns: GPS coordinates (e.g., (latitude, longitude)) if available,
                otherwise None.
      :rtype: tuple of float or None



   .. py:method:: get_pixel_coords()

      Return the pixel coordinates of the detection center.

      :returns: Center point (x, y) of the detection in image coordinates.
      :rtype: tuple of int



   .. py:method:: get_timestamp()

      Return the timestamp associated with this detection.

      :returns: Timestamp string if available, otherwise None.
      :rtype: str or None



   .. py:method:: get_confidence()

      Return the confidence score for this detection.

      The confidence is validated to be within [0.0, 1.0].

      :returns: Confidence score for the detection.
      :rtype: float

      :raises ValueError: If the stored confidence is outside the range [0.0, 1.0].



   .. py:method:: get_image()

      Return the full source image for this detection.

      :returns: The image in which this detection was made.
      :rtype: cv2.typing.MatLike



.. py:class:: DetectionModelResult(model_name: Optional[str] = None, model_hash: Optional[str] = None, image: Optional[cv2.typing.MatLike] = None)

   Bases: :py:obj:`image_processing.results.ModelResult`


   Model result that aggregates detections and their source image.

   This extends :class:`ModelResult` by attaching an image and a list of
   :class:`Detection` instances produced by a single model run.

   :param model_name: Name or identifier of the detection model, by default None.
   :type model_name: str or None, optional
   :param model_hash: Hash or version identifier for the model artefact, by default None.
   :type model_hash: str or None, optional
   :param image: Image associated with the detections, by default None.
   :type image: cv2.typing.MatLike or None, optional

   .. attribute:: image

      Image used for the detections.

      :type: cv2.typing.MatLike or None

   .. attribute:: detections

      List of detection objects associated with this result.

      :type: list of Detection


   .. py:attribute:: image
      :value: None



   .. py:attribute:: detections
      :value: []



   .. py:method:: add(detection: Detection)

      Add a detection to the result's detection list.

      :param detection: Detection instance to append to the result.
      :type detection: Detection



.. py:class:: Detector(model_config: Optional[image_processing.odcl.detection.SahiConfig.ModelConfig] = None)

   Detection model wrapper with SAHI-based backend support.

   This class encapsulates configuration, loading, and inference for
   object detection models. The current implementation supports SAHI
   slicing or standard prediction modes via :class:`SahiDetectionModel`,
   and exposes utilities to convert raw predictions into internal
   :class:`Detection` objects.

   :param model_config: Configuration for the detection model and its backend, including
                        model path, type, device, and SAHI-specific slicing parameters.
   :type model_config: ModelConfig or None, optional

   .. attribute:: backend

      Name of the backend in use (e.g., ``"sahi"``) or None if not set.

      :type: str or None

   .. attribute:: model_config

      Active model configuration.

      :type: ModelConfig or None

   .. attribute:: model

      Loaded model instance (e.g., :class:`SahiDetectionModel`) once
      :meth:`loadModel` has been called.

      :type: Any

   .. attribute:: model_path

      Path to the model artefact. May be used to track or hash the model.

      :type: str or None

   .. attribute:: model_hash

      Optional hash used to identify the specific model build.

      :type: str or None


   .. py:attribute:: backend
      :value: None



   .. py:attribute:: model_config
      :type:  image_processing.odcl.detection.SahiConfig.ModelConfig | None
      :value: None



   .. py:attribute:: model
      :value: None



   .. py:attribute:: model_path
      :value: None



   .. py:attribute:: model_hash
      :value: None



   .. py:method:: setModelConfig(model_config: Optional[image_processing.odcl.detection.SahiConfig.ModelConfig])

      Set the model configuration and determine the backend type.

      If the configuration includes a SAHI backend, the backend name
      is set to ``"sahi"``; otherwise, backend is left as None.

      :param model_config: New model configuration to apply.
      :type model_config: ModelConfig or None



   .. py:method:: loadModel()

      Load the detection model based on the current configuration.

      Currently, this initializes a :class:`SahiDetectionModel` when the
      backend is ``"sahi"`` and a valid :class:`ModelConfig` is present.



   .. py:method:: initializeModel()

      Warm up the detection model by running a dummy forward pass.

      This can be used to trigger any lazy initialization inside the
      underlying framework (e.g., CUDA context, graph compilation) so
      that the first real inference call is faster.



   .. py:method:: exportVisuals(results: sahi.prediction.PredictionResult, export_dir: str = os.getcwd(), file_name: str = 'visual.png')

      Export visualizations of detection results to disk.

      For SAHI backends, this delegates to
      :meth:`sahi.prediction.PredictionResult.export_visuals`.

      :param results: Prediction results object produced by SAHI.
      :type results: PredictionResult
      :param export_dir: Directory where the visualization image will be saved, by default
                         the current working directory.
      :type export_dir: str, optional
      :param file_name: File name for the exported visualization image, by default
                        ``"visual.png"``.
      :type file_name: str, optional



   .. py:method:: parseResults(results: sahi.prediction.PredictionResult, padding=0) -> tuple[DetectionModelResult, list[Detection]]

      Convert a :class:`PredictionResult` into internal detection objects.

      This method converts a SAHI :class:`PredictionResult` into a
      :class:`DetectionModelResult` and a list of :class:`Detection`
      instances, optionally expanding bounding boxes by a given padding
      while keeping them within image bounds.

      :param results: SAHI prediction results object to parse.
      :type results: PredictionResult
      :param padding: Number of pixels to expand each bounding box in all directions
                      before cropping, by default 0.
      :type padding: int, optional

      :returns: * *DetectionModelResult* -- Aggregated result containing the source image and its detections.
                * *list of Detection* -- Flat list of per-object detection instances created from the
                  prediction result.



   .. py:method:: run(image: cv2.typing.MatLike) -> Optional[sahi.prediction.PredictionResult]

      Run the detection model on an input image.

      For SAHI backends, this either performs sliced prediction or
      standard prediction, depending on :class:`SahiConfig`. Post-processing
      is configured according to the SAHI backend settings.

      :param image: Input image (e.g., NumPy array) to run detection on.
      :type image: cv2.typing.MatLike

      :returns: SAHI prediction result object if the model and configuration
                are valid, otherwise None.
      :rtype: PredictionResult or None



   .. py:method:: cropDetection(image: cv2.typing.MatLike, bounding_box: tuple[int, int, int, int]) -> cv2.typing.MatLike

      Crop a region of interest from an image using a bounding box.

      The bounding box is provided in `[x_min, y_min, x_max, y_max]` format.
      OpenCV images are indexed as `[row, col] = [y, x]`, so the slice order
      is `[y_min:y_max, x_min:x_max]`.

      :param image: The source image as a NumPy array.
      :type image: cv2.typing.MatLike
      :param bounding_box: The bounding box coordinates
                           in `[x_min, y_min, x_max, y_max]` format.
      :type bounding_box: tuple[int, int, int, int]

      :returns: The cropped image region corresponding to the
                bounding box.
      :rtype: cv2.typing.MatLike



   .. py:method:: getBoundingBox(object_prediction: sahi.prediction.ObjectPrediction | None) -> Optional[tuple[int, int, int, int]]

      Return the bounding box for a given object prediction in
      `[x_min, y_min, x_max, y_max]` format.

      This method normalizes bounding box outputs so that the same format is
      returned regardless of the configured backend. If the prediction is
      invalid, None, or cannot be converted, an empty list is returned.

      :param object_prediction: The prediction object
                                from which to extract the bounding box.
      :type object_prediction: ObjectPrediction | None

      :returns: A list of four float values representing the bounding box
                coordinates `[x_min, y_min, x_max, y_max]`. Returns an empty list if
                no valid bounding box can be obtained.
      :rtype: Optional[tuple[int, int, int, int]]



   .. py:method:: getBoundingBoxCenter(bounding_box: tuple[int, int, int, int]) -> tuple[int, int]

      Compute the center point of an object's bounding box.

      The bounding box is first extracted in `[x_min, y_min, x_max, y_max]` format
      using `getBoundingBox`. The center coordinates are then calculated as the
      midpoint of the bounding box edges.

      :param object_prediction: The prediction object
                                from which to extract the bounding box. If None or invalid, the
                                result will be (None, None).
      :type object_prediction: ObjectPrediction | None

      :returns: A tuple `(center_x, center_y)`
                representing the bounding box center in image coordinates. If no valid
                bounding box is available, returns `(None, None)`.
      :rtype: tuple[float | None, float | None]



   .. py:method:: adjustBoundingBox(bounding_box: tuple[int, int, int, int], padding: int, img_width: int, img_height: int) -> tuple[int, int, int, int]

      Expand a bounding box by a given padding while ensuring it stays
      within image boundaries.

      The method iteratively applies padding around the bounding box until
      either the requested expansion is applied or further padding would
      exceed the image dimensions. If padding cannot be fully applied,
      it is reduced step by step until a valid box is obtained.

      :param bb: The original bounding box
                 in `[x_min, y_min, x_max, y_max]` format.
      :type bb: tuple[float, float, float, float]
      :param padding: The number of pixels to expand the bounding box
                      in all directions.
      :type padding: int
      :param img_width: Width of the image (upper bound for `x_max`).
      :type img_width: int
      :param img_height: Height of the image (upper bound for `y_max`).
      :type img_height: int

      :returns: The adjusted bounding box in
                `[x_min, y_min, x_max, y_max]` format, guaranteed to fit within
                the image dimensions.
      :rtype: tuple[float, float, float, float]



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


