image_processing.odcl.detection.DetectionManager
================================================

.. py:module:: image_processing.odcl.detection.DetectionManager


Classes
-------

.. autoapisummary::

   image_processing.odcl.detection.DetectionManager.DetectionManager


Module Contents
---------------

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


