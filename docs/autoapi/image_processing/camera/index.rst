image_processing.camera
=======================

.. py:module:: image_processing.camera

.. autoapi-nested-parse::

   Camera subsystem initialization and public API exports.

   This subpackage defines the core camera abstraction layer used throughout
   the image_processing framework. It exposes:

   - Generic camera interface and metadata structures
   - Abstract backend contract for concrete camera implementations
   - GStreamer pipeline construction utility

   Concrete backends and controllers are located in the ``backends`` and
   ``controllers`` submodules respectively.



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



.. py:class:: CameraMetadata

   Structured container for intrinsic camera properties.

   :param sensor_width: Physical width of the image sensor in mm.
   :type sensor_width: float
   :param sensor_height: Physical height of the image sensor in mm.
   :type sensor_height: float
   :param image_width: Horizontal resolution of captured images in pixels.
   :type image_width: int
   :param image_height: Vertical resolution of captured images in pixels.
   :type image_height: int
   :param focal_length: Focal length of the lens, expressed in millimeters or equivalent units.
   :type focal_length: int


   .. py:attribute:: sensor_width
      :type:  float


   .. py:attribute:: sensor_height
      :type:  float


   .. py:attribute:: image_width
      :type:  int


   .. py:attribute:: image_height
      :type:  int


   .. py:attribute:: focal_length
      :type:  int


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


