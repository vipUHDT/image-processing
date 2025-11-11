image_processing.odcl
=====================

.. py:module:: image_processing.odcl


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/image_processing/odcl/Classification/index
   /autoapi/image_processing/odcl/Localize/index
   /autoapi/image_processing/odcl/detection/index


Classes
-------

.. autoapisummary::

   image_processing.odcl.Georeference_Engine
   image_processing.odcl.PlatformState
   image_processing.odcl.QueuedImage
   image_processing.odcl.Camera
   image_processing.odcl.CameraBackend
   image_processing.odcl.CameraMetadata
   image_processing.odcl.ODCL


Functions
---------

.. autoapisummary::

   image_processing.odcl.georeference_utm
   image_processing.odcl.georeference_enu
   image_processing.odcl.georeference_aeqd
   image_processing.odcl.georeference_manual
   image_processing.odcl.haversine
   image_processing.odcl.constructGstreamerPipeline


Package Contents
----------------

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



.. py:class:: QueuedImage

   .. py:attribute:: image
      :type:  cv2.typing.MatLike


   .. py:attribute:: platform_state
      :type:  PlatformState


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

.. py:class:: ODCL

   .. py:attribute:: pipeline
      :value: []



