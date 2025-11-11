image_processing.camera
=======================

.. py:module:: image_processing.camera

.. autoapi-nested-parse::

   The `image_processing.camera` package provides classes and utilities
   for handling camera input, streaming, and configuration.

   It includes:
   - `backends` for different camera sources (e.g., GStreamer, remote).
   - `controllers` for specific sensors like the Hadron 640R.
   - `camera` core definitions and metadata structures.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/image_processing/camera/backends/index
   /autoapi/image_processing/camera/camera/index
   /autoapi/image_processing/camera/controllers/index


Classes
-------

.. autoapisummary::

   image_processing.camera.Camera
   image_processing.camera.CameraBackend
   image_processing.camera.CameraMetadata


Functions
---------

.. autoapisummary::

   image_processing.camera.constructGstreamerPipeline


Package Contents
----------------

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

