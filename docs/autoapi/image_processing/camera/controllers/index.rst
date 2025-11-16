image_processing.camera.controllers
===================================

.. py:module:: image_processing.camera.controllers

.. autoapi-nested-parse::

   Camera controller implementations for the image_processing.camera subsystem.

   This subpackage exposes higher-level orchestration classes that manage one or
   more camera backends, configure GStreamer pipelines, handle remote connection
   setup, and enable synchronized capture workflows for multi-sensor camera
   systems (e.g., FLIR Hadron 640R).



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/image_processing/camera/controllers/Hadron640R/index


Attributes
----------

.. autoapisummary::

   image_processing.camera.controllers.LOGGER


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



.. py:function:: constructGstreamerPipeline(pipeline: tuple) -> str

   Construct a GStreamer pipeline string from a tuple of elements.

   The elements in the input tuple are joined with the ``" ! "`` separator
   to form a valid GStreamer pipeline description.

   :param pipeline: Ordered sequence of GStreamer elements (e.g., caps, sources,
                    converters, sinks).
   :type pipeline: tuple of str

   :returns: GStreamer pipeline string suitable for use with GStreamer-based
             APIs.
   :rtype: str


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



.. py:data:: LOGGER

.. py:class:: Hadron640R

   High-level controller for the Hadron 640R RGB–IR camera pair.

   This class coordinates the OV64B (RGB) and Boson 640 (infrared) cameras
   via a :class:`GStreamerManager`. It configures remote connection
   parameters, initializes GStreamer TX/RX pipelines for each camera, and
   provides a simple interface to capture synchronized RGB and infrared
   frames.

   .. attribute:: backendManager

      Manager that holds and orchestrates the individual camera instances.

      :type: GStreamerManager

   .. attribute:: ports

      Mapping from camera name (e.g., ``"BOSON640"``, ``"OV64B"``) to UDP
      ports used for streaming.

      :type: dict of str to int

   .. attribute:: processes

      Internal list used to track process-related information, if needed.

      :type: list

   .. attribute:: client

      Identifier or address of the local client that receives streamed data.

      :type: str

   .. attribute:: host

      Hostname or IP of the remote device running the GStreamer pipelines.

      :type: str

   .. attribute:: username

      Username used for authenticating to the remote host.

      :type: str

   .. attribute:: password

      Password or credential used for authenticating to the remote host.

      :type: str


   .. py:attribute:: backendManager


   .. py:attribute:: ports


   .. py:attribute:: processes
      :value: []



   .. py:method:: getProcessIds()

      Retrieve process IDs for remote GStreamer processes.

      This method connects to the remote camera host, queries for processes
      matching the string ``"gst"`` (e.g., GStreamer pipelines), and returns
      a list of cleaned process identifiers.

      :returns: List of process IDs that match the GStreamer search on the remote
                host. Returns an empty list if connection details are incomplete
                or no matching processes are found.
      :rtype: list of str



   .. py:method:: setConnection(client, host, username, password)

      Set remote connection credentials for the Hadron system.

      :param client: Address or identifier of the client that receives streamed video.
      :type client: str
      :param host: Hostname or IP address of the remote device running the cameras.
      :type host: str
      :param username: Username used to authenticate to the remote host.
      :type username: str
      :param password: Password or credential used to authenticate to the remote host.
      :type password: str



   .. py:method:: initialize()

      Instantiate and configure OV64B and Boson640 camera pipelines.

      This method:
      1. Adds :class:`OV64B` and :class:`Boson640` camera instances to the
         backend manager.
      2. Propagates remote connection information to each camera.
      3. Sets per-camera UDP ports.
      4. Configures TX and RX GStreamer pipelines.
      5. Initializes each camera and its stream.
      6. Starts the RX pipelines so frames can be captured.



   .. py:method:: capture()

      Capture one RGB frame and one infrared frame from the Hadron system.

      :returns: A pair ``(rgb_img, infrared_img)`` where:

                * ``rgb_img`` is a frame from the OV64B RGB camera (typically a
                  BGR NumPy array).
                * ``infrared_img`` is a frame from the Boson 640 infrared camera.
      :rtype: tuple



   .. py:method:: terminate()

      Stop RX pipelines and terminate both camera streams.

      This closes the RX pipelines and tears down the underlying GStreamer
      processes for both the OV64B and Boson 640 cameras.



.. py:class:: Boson640

   Bases: :py:obj:`image_processing.camera.Camera`


   Concrete camera wrapper for the Boson 640 infrared sensor.

   This class subclasses :class:`Camera` and uses a :class:`GStreamerCamera`
   backend to configure and manage TX and RX GStreamer pipelines for the
   Boson 640 stream. It exposes convenience methods for setting ports,
   pipelines, and capturing frames.

   .. attribute:: backend

      Backend responsible for running the GStreamer pipelines.

      :type: GStreamerCamera

   .. attribute:: RX_TEMPLATE

      Default GStreamer RX pipeline template used to receive H.264 video
      over UDP and convert it into a BGR stream.

      :type: Template

   .. attribute:: TX_TEMPLATE

      Default GStreamer TX pipeline template used to stream video from
      ``/dev/video0`` over UDP to the client.

      :type: Template


   .. py:attribute:: backend


   .. py:attribute:: RX_TEMPLATE


   .. py:attribute:: TX_TEMPLATE


   .. py:method:: setPort(port)

      Set the UDP port used by the Boson 640 backend.

      :param port: UDP port number on which to send or receive the Boson 640 stream.
      :type port: int



   .. py:method:: setTXPipeline(pipeline: string.Template | str | None = None)

      Configure the TX (transmit) pipeline for the Boson 640 stream.

      :param pipeline: Custom TX pipeline to use. If ``None``, the default
                       :attr:`TX_TEMPLATE` is applied.
      :type pipeline: Template or str or None, optional



   .. py:method:: setRXPipeline(pipeline: string.Template | str | None = None)

      Configure the RX (receive) pipeline for the Boson 640 stream.

      :param pipeline: Custom RX pipeline to use. If ``None``, the default
                       :attr:`RX_TEMPLATE` is applied.
      :type pipeline: Template or str or None, optional



   .. py:method:: startRXPipeline()

      Start the RX pipeline so that frames can be received.



   .. py:method:: captureFrame()

      Capture a single infrared frame from the Boson 640 stream.

      :returns: The captured frame, typically a BGR NumPy array produced by the
                GStreamer pipeline.
      :rtype: Any



   .. py:method:: closeRXPipeline()

      Stop and close the RX pipeline for the Boson 640 stream.



   .. py:method:: initialize()

      Initialize the Boson 640 backend and allocate required resources.



   .. py:method:: initializeStream(pids)

      Initialize the Boson 640 stream, optionally using process IDs.

      :param pids: List of process identifiers (e.g., from :meth:`Hadron640R.getProcessIds`)
                   used by the backend to manage or attach to running pipelines.
      :type pids: list



   .. py:method:: terminate()

      Terminate the Boson 640 backend and clean up resources.



.. py:class:: OV64B

   Bases: :py:obj:`image_processing.camera.Camera`


   Concrete camera wrapper for the OV64B RGB sensor.

   This class subclasses :class:`Camera` and uses a :class:`GStreamerCamera`
   backend to configure and manage TX and RX GStreamer pipelines for the
   OV64B RGB stream. It exposes convenience methods for setting ports,
   pipelines, and capturing frames.

   .. attribute:: backend

      Backend responsible for running the GStreamer pipelines.

      :type: GStreamerCamera

   .. attribute:: RX_TEMPLATE

      Default GStreamer RX pipeline template used to receive H.264 video
      over UDP and convert it into a BGR stream.

      :type: Template

   .. attribute:: TX_TEMPLATE

      Default GStreamer TX pipeline template used to stream video from
      the OV64B source over UDP to the client.

      :type: Template


   .. py:attribute:: backend


   .. py:attribute:: RX_TEMPLATE


   .. py:attribute:: TX_TEMPLATE


   .. py:method:: setPort(port)

      Set the UDP port used by the OV64B backend.

      :param port: UDP port number on which to send or receive the OV64B stream.
      :type port: int



   .. py:method:: setTXPipeline(pipeline: string.Template | str | None = None)

      Configure the TX (transmit) pipeline for the OV64B stream.

      :param pipeline: Custom TX pipeline to use. If ``None``, the default
                       :attr:`TX_TEMPLATE` is applied.
      :type pipeline: Template or str or None, optional



   .. py:method:: startRXPipeline()

      Start the RX pipeline so that frames can be received.



   .. py:method:: setRXPipeline(pipeline: string.Template | str | None = None)

      Configure the RX (receive) pipeline for the OV64B stream.

      :param pipeline: Custom RX pipeline to use. If ``None``, the default
                       :attr:`RX_TEMPLATE` is applied.
      :type pipeline: Template or str or None, optional



   .. py:method:: captureFrame()

      Capture a single RGB frame from the OV64B stream.

      :returns: The captured frame, typically a BGR NumPy array produced by the
                GStreamer pipeline.
      :rtype: Any



   .. py:method:: closeRXPipeline()

      Stop and close the RX pipeline for the OV64B stream.



   .. py:method:: initialize()

      Initialize the OV64B backend and allocate required resources.



   .. py:method:: initializeStream(pids)

      Initialize the OV64B stream, optionally using process IDs.

      :param pids: List of process identifiers (e.g., from :meth:`Hadron640R.getProcessIds`)
                   used by the backend to manage or attach to running pipelines.
      :type pids: list



   .. py:method:: terminate()

      Terminate the OV64B backend and clean up resources.



