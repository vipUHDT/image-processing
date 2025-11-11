image_processing.odcl.detection.Detection
=========================================

.. py:module:: image_processing.odcl.detection.Detection


Classes
-------

.. autoapisummary::

   image_processing.odcl.detection.Detection.Detection
   image_processing.odcl.detection.Detection.DetectionModelResult
   image_processing.odcl.detection.Detection.Detector


Module Contents
---------------

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



