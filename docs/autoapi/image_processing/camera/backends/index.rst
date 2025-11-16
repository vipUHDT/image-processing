image_processing.camera.backends
================================

.. py:module:: image_processing.camera.backends

.. autoapi-nested-parse::

   Backend factory and public exports for camera backend implementations.

   This module exposes the available backend classes (e.g., remote and
   GStreamer-based backends) and provides :func:`getBackend`, a simple factory
   function for retrieving backend instances by name. Backends defined here are
   used by higher-level camera controllers to abstract away connection and
   transport details.



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


   Backend that communicates with a remote camera host using SSH.

   This backend is intended for camera systems that do not run locally
   and require remote command execution to configure, initialize, or
   manage streaming pipelines (e.g., via GStreamer). It assumes that
   the remote endpoint supports process management and allows launching
   background commands over SSH.

   :param client: Identifier for the client receiving streamed data (e.g., its hostname or IP).
   :type client: str or None, optional
   :param host: Hostname or IP address of the remote device where camera processes run.
   :type host: str or None, optional
   :param username: Username for SSH authentication.
   :type username: str or None, optional
   :param password: Password or credential used for SSH authentication.
   :type password: str or None, optional

   .. attribute:: name

      Identifier for the backend, default is ``"RB5 Backend"``.

      :type: str

   .. attribute:: connection_manager

      Active SSH connection wrapper once :meth:`connect` is called.

      :type: SSH_Controller or None


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

      Update SSH connection credentials.

      :param client: Identifier of the local client receiving video.
      :type client: str
      :param host: Hostname or IP of the remote SSH device.
      :type host: str
      :param username: Username used for authentication.
      :type username: str
      :param password: Password or credential used for authentication.
      :type password: str



   .. py:method:: connect() -> None

      Create and open an SSH connection to the remote camera host.



   .. py:method:: initializeStream(pipeline) -> None

      Launch a streaming pipeline remotely in the background.

      :param pipeline: Command or pipeline string to execute remotely, such as
                       a GStreamer launch command. Executed in background mode.
      :type pipeline: str



   .. py:method:: getProcessID(keyword) -> list[str]

      Query remote process IDs that match a given keyword.

      :param keyword: Search term used with ``pgrep`` to filter process names.
      :type keyword: str

      :returns: List of matching process IDs returned by the remote host.
                Returns an empty list if no connection is active.
      :rtype: list of str



   .. py:method:: setGstreamerPid(gstreamer_pid) -> None

      Store a process ID associated with a remote GStreamer pipeline.

      :param gstreamer_pid: Process ID to be stored for later termination or tracking.
      :type gstreamer_pid: str or None



   .. py:method:: terminateProcessID(pid: None | str = None)

      Terminate a remote process by PID using SIGINT.

      :param pid: Remote PID to terminate. If ``None``, no action is taken.
      :type pid: str or None

      :returns: Output from the remote command, if executed.
      :rtype: Any



   .. py:method:: terminateProcessName(pname: None | str)

      Terminate remote processes that match a process name.

      :param pname: Name used with ``pkill`` to terminate matching processes.
      :type pname: str or None

      :returns: Output from the remote command, if executed.
      :rtype: Any



   .. py:method:: disconnect()

      Disconnect the active SSH session.



   .. py:method:: initialize() -> None

      Initialize the backend by establishing the SSH connection.



.. py:data:: LOGGER

.. py:class:: Camera(name: str, metadata: Optional[CameraMetadata] = None)

   Bases: :py:obj:`abc.ABC`


   Abstract representation of a camera device.

   This class manages common properties such as the camera name,
   associated backend, connection credentials, and optional
   metadata. Concrete subclasses must implement :meth:`captureFrame`
   to define how a frame is acquired.

   :param name: Logical name or identifier for the camera instance.
   :type name: str
   :param metadata: Intrinsic parameters and resolution for the camera, if known.
   :type metadata: CameraMetadata, optional


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

      Select and configure the camera backend by name.

      The backend string is validated against a list of supported
      backend identifiers and, if valid, the corresponding backend
      instance is created.

      :param backend: Name of the backend to use (e.g., ``"rb5"``).
      :type backend: str

      :raises ValueError: If the requested backend is not in the list of supported
          backends.



   .. py:method:: getBackend(backend)

      Instantiate and return a backend by name.

      This helper imports the backend factory from
      ``image_processing.camera.backends`` and constructs a backend
      instance corresponding to the given identifier.

      :param backend: Name of the backend to retrieve.
      :type backend: str

      :returns: The instantiated backend associated with the given name.
      :rtype: CameraBackend



   .. py:method:: setConnection(client, host, username, password)

      Set connection parameters and propagate them to the backend.

      :param client: Identifier or role of the current client (e.g., local host name).
      :type client: str
      :param host: Hostname or IP address of the remote device or service.
      :type host: str
      :param username: Username used for authentication with the remote endpoint.
      :type username: str
      :param password: Password or token used for authentication with the remote endpoint.
      :type password: str



   .. py:method:: connect()

      Establish a connection through the configured backend.

      This method uses the connection credentials stored on the
      camera instance to instruct the backend to establish a session
      (e.g., network connection) required for frame acquisition.



   .. py:method:: initialize()

      Initialize the backend prior to frame capture.

      If a backend is configured, this method forwards the call to
      :meth:`CameraBackend.initialize` so that all required resources
      are ready before capturing frames.



   .. py:method:: captureFrame()
      :abstractmethod:


      Capture a single frame from the camera.

      Concrete subclasses must implement this method to define how
      a frame is acquired from the underlying backend.

      :returns: The captured frame object. The exact type depends on the
                backend and implementation (e.g., NumPy array, raw bytes).
      :rtype: Any



.. py:type:: GStreamerRemoteConnection
   :canonical: tuple[str, str, str, str]


.. py:class:: GStreamerCamera(name: str, remote_connection: GStreamerRemoteConnection | None = None)

   Camera backend that streams video using GStreamer and OpenCV.

   This class wraps a :class:`RemoteCamera` instance and manages both
   transmit (TX) and receive (RX) GStreamer pipelines. RX pipelines are
   opened using :func:`cv2.VideoCapture` with the GStreamer backend, while
   TX pipelines are launched remotely over SSH via the underlying
   :class:`RemoteCamera`.

   :param name: Logical name of the camera associated with this backend.
   :type name: str
   :param remote_connection: Optional tuple ``(client, host, username, password)`` used to
                             construct a :class:`RemoteCamera` on initialization if no
                             connection has been set explicitly.
   :type remote_connection: tuple of (str, str, str, str), optional

   .. attribute:: name

      Name of the camera associated with this backend.

      :type: str

   .. attribute:: tx_pipeline

      GStreamer pipeline string used for transmitting video (remote side).

      :type: str or None

   .. attribute:: rx_pipeline

      GStreamer pipeline string used for receiving video (local side).

      :type: str or None

   .. attribute:: pid

      Process ID of the remote streaming process, if known.

      :type: str or None

   .. attribute:: remote

      Remote backend used to execute streaming commands over SSH.

      :type: RemoteCamera or None

   .. attribute:: connected

      Flag indicating whether a remote connection has been initialized.

      :type: bool

   .. attribute:: capture

      OpenCV capture object used for reading frames from the RX pipeline.

      :type: cv2.VideoCapture or None

   .. attribute:: port

      UDP port on which the RX/TX pipelines operate.

      :type: int or None


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

      Create a RemoteCamera with the provided connection parameters.

      :param client: Identifier or address of the client receiving video.
      :type client: str
      :param host: Hostname or IP address of the remote camera host.
      :type host: str
      :param username: Username used to authenticate to the remote host.
      :type username: str
      :param password: Password or credential used to authenticate to the remote host.
      :type password: str



   .. py:method:: setPort(port)

      Set the UDP port used for streaming.

      :param port: UDP port number for the GStreamer TX/RX pipelines.
      :type port: int



   .. py:method:: connect()

      Establish the SSH connection to the remote camera host.



   .. py:method:: initialize()

      Initialize the remote connection based on configured settings.

      If a :class:`RemoteCamera` has already been created, this method
      connects to it. Otherwise, if a ``remote_connection`` tuple was
      provided at construction time, a new :class:`RemoteCamera` is created
      and connected. If neither is available, an error string is returned.

      :returns: ``None`` if initialization succeeds, otherwise the string
                ``"Invalid connection"`` when no connection parameters are set.
      :rtype: None or str



   .. py:method:: setTXPipeline(pipeline: string.Template | str)

      Configure the TX (transmit) GStreamer pipeline.

      If a :class:`Template` is provided, the placeholders ``$client`` and
      ``$port`` are substituted using the remote connection and the local
      port before the pipeline is stored.

      :param pipeline: GStreamer pipeline template or string to use for transmission.
      :type pipeline: Template or str



   .. py:method:: setRXPipeline(pipeline)

      Configure the RX (receive) GStreamer pipeline.

      If a :class:`Template` is provided, the placeholder ``$port`` is
      substituted using the configured port before the pipeline is stored.

      :param pipeline: GStreamer pipeline template or string to use for reception.
      :type pipeline: Template or str



   .. py:method:: startRXPipeline()

      Open the RX pipeline as an OpenCV VideoCapture stream.

      :raises RuntimeError: If the RX pipeline is set but the stream fails to open.



   .. py:method:: closeRXPipeline()

      Release the OpenCV capture associated with the RX pipeline.



   .. py:method:: captureFrame()

      Capture a single frame from the RX pipeline.

      :returns: The captured frame, typically a NumPy array in BGR format.
                Returns ``None`` if reading fails.
      :rtype: Any



   .. py:method:: initializeStream(process_ids, pipeline=None)

      Start the remote TX pipeline and record its process ID.

      :param process_ids: Existing process IDs used to filter out already-known GStreamer
                          processes when searching for the new one.
      :type process_ids: list of str
      :param pipeline: Optional explicit pipeline command to use instead of the
                       previously configured :attr:`tx_pipeline`.
      :type pipeline: str or Template or None, optional



   .. py:method:: getGstreamerProcessID(process_ids: list[str])

      Identify the newly started GStreamer process ID.

      This method queries the remote host for processes matching ``"gst"``
      and returns the first process ID that is not already present in
      the provided ``process_ids`` list.

      :param process_ids: List of process IDs known prior to starting the new pipeline.
      :type process_ids: list of str

      :returns: The newly detected GStreamer process ID, or ``None`` if no
                suitable process is found.
      :rtype: str or None



   .. py:method:: terminate()

      Terminate the associated remote GStreamer process, if any.

      This sends a SIGINT to the recorded process ID via the underlying
      :class:`RemoteCamera`, clears the stored PID, and marks the backend
      as disconnected.



.. py:class:: GStreamerManager

   Registry for managing multiple camera instances by name or label.

   This class stores :class:`Camera` instances in a dictionary, keyed either
   by an explicit label or by the camera's :attr:`name` attribute. It is
   primarily used to organize and access multiple camera controllers in a
   larger imaging system.

   .. attribute:: cameras

      Mapping from label or camera name to the corresponding camera object.

      :type: dict of str to Camera


   .. py:attribute:: cameras
      :type:  dict[str, image_processing.camera.Camera]


   .. py:method:: addCamera(camera: image_processing.camera.Camera, label: str | None = None) -> None

      Register a camera instance with an optional label.

      :param camera: Camera instance to register in the manager.
      :type camera: Camera
      :param label: Optional label to use as the key. If omitted, the camera's
                    :attr:`name` attribute is used instead.
      :type label: str or None, optional



.. py:class:: CameraBackend

   Bases: :py:obj:`abc.ABC`


   Abstract base class for camera backends.

   Concrete implementations wrap specific camera hardware or
   streaming sources (e.g., RB5, remote cameras) and provide a
   unified interface for initialization and connection handling.


   .. py:method:: initialize() -> None
      :abstractmethod:


      Perform backend initialization before capturing frames.

      This method is intended for tasks such as opening device
      handles, starting pipelines, or validating configuration
      prior to streaming.



   .. py:method:: setConnection(client: str, host: str, username: str, password: str) -> None
      :abstractmethod:


      Configure connection parameters for the backend.

      :param client: Identifier or role of the current client (e.g., local host name
                     or logical client type).
      :type client: str
      :param host: Hostname or IP address of the remote device or service.
      :type host: str
      :param username: Username used for authentication with the remote endpoint.
      :type username: str
      :param password: Password or token used for authentication with the remote endpoint.
      :type password: str



   .. py:method:: connect() -> None
      :abstractmethod:


      Establish a connection using the configured parameters.

      Implementations should use the connection parameters provided via
      :meth:`setConnection` to open network sessions, SSH tunnels, or any
      other transport needed for frame acquisition.



.. py:function:: getBackend(backend: str) -> image_processing.camera.CameraBackend | None

   Return an initialized backend instance by backend name.

   :param backend: Name of the backend to create. Currently supported:
                   - ``"rb5"`` → :class:`RemoteCamera`
   :type backend: str

   :returns: A backend instance if the name is recognized, otherwise ``None``.
   :rtype: CameraBackend or None

   .. rubric:: Notes

   Backends are instantiated immediately, not lazily. If authentication or
   connection details are required, they must be provided via the backend's
   own configuration methods.


