image_processing.camera.backends
================================

.. py:module:: image_processing.camera.backends


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/image_processing/camera/backends/gstreamer/index
   /autoapi/image_processing/camera/backends/remote/index


Attributes
----------

.. autoapisummary::

   image_processing.camera.backends.LOGGER
   image_processing.camera.backends.GStreamerRemoteConnection


Classes
-------

.. autoapisummary::

   image_processing.camera.backends.RemoteCamera
   image_processing.camera.backends.Camera
   image_processing.camera.backends.GStreamerCamera
   image_processing.camera.backends.GStreamerManager
   image_processing.camera.backends.CameraBackend


Functions
---------

.. autoapisummary::

   image_processing.camera.backends.getBackend


Package Contents
----------------

.. py:class:: RemoteCamera(client: str | None = None, host: str | None = None, username: str | None = None, password: str | None = None)

   Bases: :py:obj:`image_processing.camera.CameraBackend`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: name
      :value: 'RB5 Backend'



   .. py:attribute:: client
      :value: None



   .. py:attribute:: host
      :value: None



   .. py:attribute:: username
      :value: None



   .. py:attribute:: password
      :value: None



   .. py:attribute:: connection_manager
      :type:  Optional[image_processing.connection.ssh.SSH_Controller] | None
      :value: None



   .. py:method:: setConnection(client: str, host: str, username: str, password: str) -> None


   .. py:method:: connect() -> None


   .. py:method:: initializeStream(pipeline) -> None


   .. py:method:: getProcessID(keyword) -> list[str]


   .. py:method:: setGstreamerPid(gstreamer_pid) -> None


   .. py:method:: terminateProcessID(pid: None | str = None)


   .. py:method:: terminateProcessName(pname: None | str)


   .. py:method:: disconect()


   .. py:method:: initialize() -> None


.. py:data:: LOGGER

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



.. py:type:: GStreamerRemoteConnection
   :canonical: tuple[str, str, str, str]


.. py:class:: GStreamerCamera(name: str, remote_connection: GStreamerRemoteConnection | None = None)

   .. py:attribute:: name


   .. py:attribute:: tx_pipeline
      :value: None



   .. py:attribute:: rx_pipeline
      :value: None



   .. py:attribute:: pid
      :value: None



   .. py:attribute:: remote_connection
      :type:  GStreamerRemoteConnection | None
      :value: None



   .. py:attribute:: remote
      :type:  image_processing.camera.backends.RemoteCamera | None
      :value: None



   .. py:attribute:: connected
      :value: False



   .. py:attribute:: capture
      :value: None



   .. py:attribute:: port
      :value: None



   .. py:method:: setConnection(client, host, username, password)


   .. py:method:: setPort(port)


   .. py:method:: connect()


   .. py:method:: initialize()


   .. py:method:: setTXPipeline(pipeline: string.Template | str)


   .. py:method:: setRXPipeline(pipeline)


   .. py:method:: startRXPipeline()


   .. py:method:: closeRXPipeline()


   .. py:method:: captureFrame()


   .. py:method:: initializeStream(process_ids, pipeline=None)


   .. py:method:: getGstreamerProcessID(process_ids: list[str])


   .. py:method:: terminate()


.. py:class:: GStreamerManager

   .. py:attribute:: cameras
      :type:  dict[str, image_processing.camera.Camera]


   .. py:method:: addCamera(camera: image_processing.camera.Camera, label: str | None = None) -> None


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



.. py:function:: getBackend(backend: str) -> image_processing.camera.CameraBackend | None

