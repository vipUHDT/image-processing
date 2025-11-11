image_processing.camera.camera
==============================

.. py:module:: image_processing.camera.camera


Attributes
----------

.. autoapisummary::

   image_processing.camera.camera.LOGGER


Classes
-------

.. autoapisummary::

   image_processing.camera.camera.CameraBackend
   image_processing.camera.camera.CameraMetadata
   image_processing.camera.camera.Camera


Functions
---------

.. autoapisummary::

   image_processing.camera.camera.constructGstreamerPipeline


Module Contents
---------------

.. py:data:: LOGGER

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



.. py:function:: constructGstreamerPipeline(pipeline: tuple) -> str

