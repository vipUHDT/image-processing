image_processing.odcl.detection
===============================

.. py:module:: image_processing.odcl.detection


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


   .. py:method:: get_pixel_coords()


   .. py:method:: get_timestamp()


   .. py:method:: get_confidence()


   .. py:method:: get_image()


.. py:class:: DetectionModelResult(model_name: Optional[str] = None, model_hash: Optional[str] = None, image: Optional[cv2.typing.MatLike] = None)

   Bases: :py:obj:`image_processing.results.ModelResult`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: image
      :value: None



   .. py:attribute:: detections
      :value: []



   .. py:method:: add(detection: Detection)


.. py:class:: Detector(model_config: Optional[image_processing.odcl.detection.SahiConfig.ModelConfig] = None)

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


   .. py:method:: loadModel()


   .. py:method:: initializeModel()


   .. py:method:: exportVisuals(results: sahi.prediction.PredictionResult, export_dir: str = os.getcwd(), file_name: str = 'visual.png')


   .. py:method:: parseResults(results: sahi.prediction.PredictionResult, padding=0) -> tuple[DetectionModelResult, list[Detection]]


   .. py:method:: run(image: cv2.typing.MatLike) -> Optional[sahi.prediction.PredictionResult]


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

   .. py:attribute:: image
      :type:  cv2.typing.MatLike


   .. py:attribute:: platform_state
      :type:  PlatformState


.. py:class:: PlatformState

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


   .. py:method:: updateResults()


   .. py:method:: updateDetections()


   .. py:method:: getGPS()


   .. py:method:: queueImage(image: image_processing.QueuedImage)


   .. py:method:: processQueuedImages()


   .. py:method:: processGPSQueue()


   .. py:method:: pruneThreads()


   .. py:method:: processQueuedImage(queued_image: image_processing.QueuedImage)


   .. py:method:: addResult(result: image_processing.odcl.detection.Detection.DetectionModelResult)


   .. py:method:: addDetection(detection: image_processing.odcl.detection.Detection.Detection, platform_state: image_processing.PlatformState)


   .. py:method:: checkForDuplicates(detection: image_processing.odcl.detection.Detection.Detection)


   .. py:method:: setGeoreferenceEngine(georeference_backend, altitude_offset=0)


   .. py:method:: georeference(target_pixel_coordinates, platform_state, camera_metadata, altitude_offset)


   .. py:method:: addDetections(detections: list[image_processing.odcl.detection.Detection.Detection], platform_state: image_processing.PlatformState)


   .. py:method:: ODCL(image, platform_state)


   .. py:method:: getAllDetections()


   .. py:method:: filterByClassification(classification: str)


   .. py:method:: filterByConfidence(threshold: float)


   .. py:method:: clearDetections()


.. py:class:: Georeference_Engine(backend, altitude_offset=0)

   .. py:attribute:: camera_metadata
      :value: None



   .. py:attribute:: backend


   .. py:attribute:: altitude_offset
      :value: 0



   .. py:method:: getBackends(backend)


   .. py:method:: georeference(target_pixel_coordinates: tuple[int, int], platform_state: image_processing.PlatformState, camera_metadata: image_processing.camera.CameraMetadata, altitude_offset=0)


.. py:function:: georeference_utm(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

.. py:function:: georeference_enu(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

.. py:function:: georeference_aeqd(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

.. py:function:: georeference_manual(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

.. py:function:: haversine(lat1, lon1, lat2, lon2)

.. py:class:: Camera(name: str, metadata: Optional[CameraMetadata] = None)

   Bases: :py:obj:`abc.ABC`


   Helper class that provides a standard way to create an ABC using
   inheritance.


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


   .. py:method:: getBackend(backend)


   .. py:method:: setConnection(client, host, username, password)


   .. py:method:: connect()


   .. py:method:: initialize()


   .. py:method:: captureFrame()
      :abstractmethod:



.. py:class:: CameraBackend

   Bases: :py:obj:`abc.ABC`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:method:: initialize() -> None
      :abstractmethod:



   .. py:method:: setConnection(client: str, host: str, username: str, password: str) -> None
      :abstractmethod:



   .. py:method:: connect() -> None
      :abstractmethod:



.. py:class:: CameraMetadata

   .. py:attribute:: sensor_width
      :type:  int


   .. py:attribute:: sensor_height
      :type:  int


   .. py:attribute:: image_width
      :type:  int


   .. py:attribute:: image_height
      :type:  int


   .. py:attribute:: focal_length
      :type:  int


.. py:function:: constructGstreamerPipeline(pipeline: tuple) -> str

.. py:class:: ModelResult(model_name: Optional[str] = None, model_hash: Optional[str] = None)

   Bases: :py:obj:`abc.ABC`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: model_name
      :value: None



   .. py:attribute:: model_hash
      :value: None



.. py:function:: hashFile(file_path: str, algorithm: str = 'md5', chunk_size: int = 8192) -> str

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


   .. py:method:: get_pixel_coords()


   .. py:method:: get_timestamp()


   .. py:method:: get_confidence()


   .. py:method:: get_image()


.. py:class:: DetectionModelResult(model_name: Optional[str] = None, model_hash: Optional[str] = None, image: Optional[cv2.typing.MatLike] = None)

   Bases: :py:obj:`image_processing.results.ModelResult`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: image
      :value: None



   .. py:attribute:: detections
      :value: []



   .. py:method:: add(detection: Detection)


.. py:class:: Detector(model_config: Optional[image_processing.odcl.detection.SahiConfig.ModelConfig] = None)

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


   .. py:method:: loadModel()


   .. py:method:: initializeModel()


   .. py:method:: exportVisuals(results: sahi.prediction.PredictionResult, export_dir: str = os.getcwd(), file_name: str = 'visual.png')


   .. py:method:: parseResults(results: sahi.prediction.PredictionResult, padding=0) -> tuple[DetectionModelResult, list[Detection]]


   .. py:method:: run(image: cv2.typing.MatLike) -> Optional[sahi.prediction.PredictionResult]


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


