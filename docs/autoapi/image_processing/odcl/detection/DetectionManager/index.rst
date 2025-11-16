image_processing.odcl.detection.DetectionManager
================================================

.. py:module:: image_processing.odcl.detection.DetectionManager

.. autoapi-nested-parse::

   Detection manager for batched, threaded ODCL processing.

   This module defines :class:`DetectionManager`, which coordinates the
   object detection and localization (ODCL) workflow. It manages queues of
   incoming images and platform states, dispatches worker threads to run
   detection using a configured model, georeferences detection pixel
   coordinates into GPS coordinates, deduplicates overlapping detections,
   and stores aggregated detections and model results for downstream use.



Classes
-------

.. autoapisummary::

   image_processing.odcl.detection.DetectionManager.DetectionManager


Module Contents
---------------

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



