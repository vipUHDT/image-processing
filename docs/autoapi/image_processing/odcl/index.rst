image_processing.odcl
=====================

.. py:module:: image_processing.odcl

.. autoapi-nested-parse::

   ODCL (Onboard Detection, Classification, and Localization) package.

   This package aggregates object detection, object classification, and
   geospatial localization components. The :class:`ODCL` class provided here
   is currently a placeholder for a higher-level pipeline controller.

   Typical ODCL workflow components:
       - Detection (image -> pixel-level detections)
       - Classification (detection class assignments)
       - Localization (convert pixel coordinates -> GPS)



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

   Engine for converting pixel coordinates into GPS coordinates.

   This class selects one of several backend functions for georeferencing
   (e.g., UTM, ENU, azimuthal-equidistant, or manual) and calls it with
   a unified interface based on platform state and camera metadata.

   :param backend: Name of the georeferencing backend to use. Must be one of
                   ``"utm"``, ``"enu"``, ``"aeqd"``, or ``"manual"``.
   :type backend: str
   :param altitude_offset: Offset applied to the drone altitude prior to computing the ground
                           footprint, by default 0.
   :type altitude_offset: float, optional

   .. attribute:: camera_metadata

      Optional camera metadata (not directly used in current implementation).

      :type: CameraMetadata or None

   .. attribute:: backend

      Selected backend function implementing georeferencing logic.

      :type: callable

   .. attribute:: altitude_offset

      Stored altitude offset passed through to the backend.

      :type: float


   .. py:attribute:: camera_metadata
      :value: None



   .. py:attribute:: backend


   .. py:attribute:: altitude_offset
      :value: 0



   .. py:method:: getBackends(backend)

      Resolve a backend name into a georeferencing function.

      :param backend: Name of the georeferencing backend (``"utm"``, ``"enu"``,
                      ``"aeqd"``, or ``"manual"``).
      :type backend: str

      :returns: Backend function implementing the requested georeference method.
      :rtype: callable

      :raises ValueError: If an unknown backend name is provided.



   .. py:method:: georeference(target_pixel_coordinates: tuple[int, int], platform_state: image_processing.PlatformState, camera_metadata: image_processing.camera.CameraMetadata, altitude_offset=0)

      Georeference a pixel coordinate into latitude/longitude.

      This method unpacks platform state and camera metadata into the
      arguments expected by the configured backend, and returns the
      resulting GPS coordinates.

      :param target_pixel_coordinates: Pixel coordinates :math:`(x, y)` of the target in image space.
      :type target_pixel_coordinates: tuple of int
      :param platform_state: Platform (drone) state containing altitude, latitude, longitude,
                             pitch, yaw, and roll (in that order).
      :type platform_state: PlatformState
      :param camera_metadata: Camera metadata containing sensor dimensions, image resolution,
                              and focal length.
      :type camera_metadata: CameraMetadata
      :param altitude_offset: Offset to subtract from platform altitude before computing
                              ground footprint, by default 0.
      :type altitude_offset: float, optional

      :returns: Target latitude and longitude in degrees.
      :rtype: tuple of float



.. py:function:: georeference_utm(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

   Georeference using a UTM projection.

   This backend:

   1. Computes camera field-of-view (FOV) from sensor size and focal length:

      .. math::

         \text{FOV}_x = 2 \arctan\left( \frac{w}{2 f} \right), \quad
         \text{FOV}_y = 2 \arctan\left( \frac{h}{2 f} \right).

   2. Computes the ground footprint width/height at altitude:

      .. math::

         W = 2 h \tan\left( \frac{\text{FOV}_x}{2} \right), \quad
         H = 2 h \tan\left( \frac{\text{FOV}_y}{2} \right).

   3. Converts drone lat/lon to UTM, applies pixel-based offsets scaled
      to :math:`W, H` and rotated by yaw, and converts back to WGS84
      coordinates.

   :param target_pixel_coordinates: Target pixel coordinates :math:`(x, y)` in image space.
   :type target_pixel_coordinates: tuple of int
   :param drone_latitude: Drone latitude in degrees.
   :type drone_latitude: float
   :param drone_longitude: Drone longitude in degrees.
   :type drone_longitude: float
   :param drone_altitude: Drone altitude above ground/sea level (units consistent with offset).
   :type drone_altitude: float
   :param altitude_offset: Altitude offset to subtract before computing footprint.
   :type altitude_offset: float
   :param drone_yaw: Drone yaw (heading) in degrees.
   :type drone_yaw: float
   :param sensor_w: Sensor width (same units as :paramref:`focal_length`).
   :type sensor_w: float
   :param sensor_h: Sensor height (same units as :paramref:`focal_length`).
   :type sensor_h: float
   :param pix_width: Image width in pixels.
   :type pix_width: int
   :param pix_height: Image height in pixels.
   :type pix_height: int
   :param focal_length: Camera focal length (same units as :paramref:`sensor_w` and
                        :paramref:`sensor_h`).
   :type focal_length: float

   :returns: Target latitude and longitude in degrees.
   :rtype: tuple of float


.. py:function:: georeference_enu(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

   Georeference using a local ENU (East–North–Up) frame.

   This backend:

   - Computes FOV and footprint size as in :func:`georeference_utm`.
   - Converts pixel offsets (relative to image center) into meters.
   - Rotates those offsets by yaw into ENU directions.
   - Uses :func:`pymap3d.enu2geodetic` to convert ENU offsets to
     latitude/longitude.

   :param target_pixel_coordinates: Target pixel coordinates :math:`(x, y)` in image space.
   :type target_pixel_coordinates: tuple of int
   :param drone_latitude: Drone latitude in degrees.
   :type drone_latitude: float
   :param drone_longitude: Drone longitude in degrees.
   :type drone_longitude: float
   :param drone_altitude: Drone altitude above reference.
   :type drone_altitude: float
   :param altitude_offset: Altitude offset to subtract before computing footprint.
   :type altitude_offset: float
   :param drone_yaw: Drone yaw (heading) in degrees.
   :type drone_yaw: float
   :param sensor_w: Sensor width (same units as :paramref:`focal_length`).
   :type sensor_w: float
   :param sensor_h: Sensor height (same units as :paramref:`focal_length`).
   :type sensor_h: float
   :param pix_width: Image width in pixels.
   :type pix_width: int
   :param pix_height: Image height in pixels.
   :type pix_height: int
   :param focal_length: Camera focal length.
   :type focal_length: float

   :returns: Target latitude and longitude in degrees.
   :rtype: tuple of float


.. py:function:: georeference_aeqd(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

   Georeference using a local Azimuthal Equidistant projection.

   This backend constructs an azimuthal equidistant (AEQD) projection
   centered on the drone position, performs all offsets in that local
   metric space, and converts back to WGS84 coordinates.

   :param target_pixel_coordinates: Target pixel coordinates :math:`(x, y)` in image space.
   :type target_pixel_coordinates: tuple of int
   :param drone_latitude: Drone latitude in degrees.
   :type drone_latitude: float
   :param drone_longitude: Drone longitude in degrees.
   :type drone_longitude: float
   :param drone_altitude: Drone altitude above reference.
   :type drone_altitude: float
   :param altitude_offset: Altitude offset to subtract before computing footprint.
   :type altitude_offset: float
   :param drone_yaw: Drone yaw (heading) in degrees.
   :type drone_yaw: float
   :param sensor_w: Sensor width.
   :type sensor_w: float
   :param sensor_h: Sensor height.
   :type sensor_h: float
   :param pix_width: Image width in pixels.
   :type pix_width: int
   :param pix_height: Image height in pixels.
   :type pix_height: int
   :param focal_length: Camera focal length.
   :type focal_length: float

   :returns: Target latitude and longitude in degrees.
   :rtype: tuple of float


.. py:function:: georeference_manual(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

   Georeference using a simple manual flat-earth approximation.

   This backend uses a constant meters-per-degree approximation to convert
   camera-plane offsets to latitude and longitude. It is less accurate at
   large distances or high latitudes, but is simple and lightweight.

   Specifically:

   .. math::

      \Delta \varphi \approx \frac{y_{\text{meters}}}{R_\varphi}, \quad
      \Delta \lambda \approx \frac{x_{\text{meters}}}{R_\lambda \cos \varphi},

   where :math:`R_\varphi \approx R_\lambda \approx 111319.944` meters
   per degree near the equator.

   :param target_pixel_coordinates: Target pixel coordinates :math:`(x, y)` in image space.
   :type target_pixel_coordinates: tuple of int
   :param drone_latitude: Drone latitude in degrees.
   :type drone_latitude: float
   :param drone_longitude: Drone longitude in degrees.
   :type drone_longitude: float
   :param drone_altitude: Drone altitude above reference.
   :type drone_altitude: float
   :param altitude_offset: Altitude offset to subtract before computing footprint.
   :type altitude_offset: float
   :param drone_yaw: Drone yaw (heading) in degrees.
   :type drone_yaw: float
   :param sensor_w: Sensor width.
   :type sensor_w: float
   :param sensor_h: Sensor height.
   :type sensor_h: float
   :param pix_width: Image width in pixels.
   :type pix_width: int
   :param pix_height: Image height in pixels.
   :type pix_height: int
   :param focal_length: Camera focal length.
   :type focal_length: float

   :returns: Target latitude and longitude in degrees.
   :rtype: tuple of float


.. py:function:: haversine(lat1, lon1, lat2, lon2)

   Compute great-circle distance between two GPS points using the haversine formula.

   The haversine distance on a sphere of radius :math:`R` is:

   .. math::

      d = 2 R \arctan2\left(
          \sqrt{a},
          \sqrt{1 - a}
      \right),

   where

   .. math::

      a = \sin^2\left( \frac{\Delta\varphi}{2} \right)
        + \cos \varphi_1 \cos \varphi_2 \sin^2\left( \frac{\Delta\lambda}{2} \right),

   and :math:`\Delta\varphi` and :math:`\Delta\lambda` are latitude and
   longitude differences in radians. This implementation uses
   :math:`R = 6371` km and returns distance in meters.

   :param lat1: Latitude of the first point in degrees.
   :type lat1: float
   :param lon1: Longitude of the first point in degrees.
   :type lon1: float
   :param lat2: Latitude of the second point in degrees.
   :type lat2: float
   :param lon2: Longitude of the second point in degrees.
   :type lon2: float

   :returns: Great-circle distance between the two points in meters.
   :rtype: float


.. py:class:: PlatformState

   Platform telemetry and attitude state associated with an image capture
   event or detection cycle.

   This structure is intended to be populated from onboard sensors
   (e.g., GNSS, IMU) or log data, and used by geolocation functions to
   project pixel detections into Earth-referenced coordinates.

   :param altitude: Platform altitude above ground level in meters.
   :type altitude: float, optional
   :param latitude: Geographic latitude (positive north) in decimal degrees.
   :type latitude: float, optional
   :param longitude: Geographic longitude (positive east) in decimal degrees.
   :type longitude: float, optional
   :param pitch: Platform pitch angle in degrees (positive nose-up).
   :type pitch: float, optional
   :param yaw: Platform yaw/heading angle in degrees (0° = North, +CW).
   :type yaw: float, optional
   :param roll: Platform roll angle in degrees (positive right-wing-down).
   :type roll: float, optional


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

   Container for an image paired with the corresponding platform state,
   used for asynchronous or batched image processing pipelines.

   :param image: The captured image frame (BGR or grayscale), typically originating
                 from a live stream or logged dataset.
   :type image: cv2.typing.MatLike
   :param platform_state: The telemetry and attitude state at the time of image acquisition.
   :type platform_state: PlatformState

   .. rubric:: Notes

   Instances of this type are typically passed into worker queues inside
   :class:`~image_processing.odcl.detection.DetectionManager`.


   .. py:attribute:: image
      :type:  cv2.typing.MatLike


   .. py:attribute:: platform_state
      :type:  PlatformState


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


.. py:class:: ODCL

   .. py:attribute:: pipeline
      :value: []



