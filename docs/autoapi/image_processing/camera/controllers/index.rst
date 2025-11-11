image_processing.camera.controllers
===================================

.. py:module:: image_processing.camera.controllers


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/image_processing/camera/controllers/Hadron640R/index


Attributes
----------

.. autoapisummary::

   image_processing.camera.controllers.LOGGER
   image_processing.camera.controllers.hadrond640


Classes
-------

.. autoapisummary::

   image_processing.camera.controllers.Camera
   image_processing.camera.controllers.CameraBackend
   image_processing.camera.controllers.RemoteCamera
   image_processing.camera.controllers.GStreamerManager
   image_processing.camera.controllers.GStreamerCamera
   image_processing.camera.controllers.Hadron640R
   image_processing.camera.controllers.Boson640
   image_processing.camera.controllers.OV64B


Functions
---------

.. autoapisummary::

   image_processing.camera.controllers.constructGstreamerPipeline


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



.. py:function:: constructGstreamerPipeline(pipeline: tuple) -> str

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


.. py:class:: GStreamerManager

   .. py:attribute:: cameras
      :type:  dict[str, image_processing.camera.Camera]


   .. py:method:: addCamera(camera: image_processing.camera.Camera, label: str | None = None) -> None


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


.. py:data:: LOGGER

.. py:class:: Hadron640R

   .. py:attribute:: backendManager


   .. py:attribute:: ports


   .. py:attribute:: processes
      :value: []



   .. py:method:: getProcessIds()


   .. py:method:: setConnection(client, host, username, password)


   .. py:method:: initialize()


   .. py:method:: capture()


   .. py:method:: terminate()


.. py:class:: Boson640

   Bases: :py:obj:`image_processing.camera.Camera`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: backend


   .. py:attribute:: RX_TEMPLATE


   .. py:attribute:: TX_TEMPLATE


   .. py:method:: setPort(port)


   .. py:method:: setTXPipeline(pipeline: string.Template | str | None = None)


   .. py:method:: setRXPipeline(pipeline: string.Template | str | None = None)


   .. py:method:: startRXPipeline()


   .. py:method:: captureFrame()


   .. py:method:: closeRXPipeline()


   .. py:method:: initialize()


   .. py:method:: initializeStream(pids)


   .. py:method:: terminate()


.. py:class:: OV64B

   Bases: :py:obj:`image_processing.camera.Camera`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: backend


   .. py:attribute:: RX_TEMPLATE


   .. py:attribute:: TX_TEMPLATE


   .. py:method:: setPort(port)


   .. py:method:: setTXPipeline(pipeline: string.Template | str | None = None)


   .. py:method:: startRXPipeline()


   .. py:method:: setRXPipeline(pipeline: string.Template | str | None = None)


   .. py:method:: captureFrame()


   .. py:method:: closeRXPipeline()


   .. py:method:: initialize()


   .. py:method:: initializeStream(pids)


   .. py:method:: terminate()


.. py:data:: hadrond640

