image_processing.odcl.detection.Detection
=========================================

.. py:module:: image_processing.odcl.detection.Detection

.. autoapi-nested-parse::

   Detection data structures and model wrapper for ODCL.

   This module defines the core abstractions for representing individual
   detections, aggregating model outputs, and running object detection
   via configurable backends. The primary implementation uses SAHI-based
   models to perform sliced or standard predictions and converts the
   results into internal :class:`Detection` objects with bounding boxes,
   centers, and cropped image regions.



Classes
-------

.. autoapisummary::

   image_processing.odcl.detection.Detection.Detection
   image_processing.odcl.detection.Detection.DetectionModelResult
   image_processing.odcl.detection.Detection.Detector


Module Contents
---------------

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



