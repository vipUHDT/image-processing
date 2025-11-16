image_processing.tools
======================

.. py:module:: image_processing.tools

.. autoapi-nested-parse::

   Utility subpackage containing general-purpose helper functions used
   throughout the project, including:

   - File hashing utilities
   - Pixel-to-world homography mapping
   - EXIF metadata extraction and embedding
   - GPS access via u-blox receivers
   - Mission-planning utilities (grid-based waypoint generation)
   - Timestamp helper for filename-safe datetime strings

   This module consolidates commonly needed routines that are not specific
   to any individual component (e.g., camera, detection, or storage) and
   can be reused across pipelines and subsystems.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/image_processing/tools/gps/index
   /autoapi/image_processing/tools/hash/index
   /autoapi/image_processing/tools/homography/index
   /autoapi/image_processing/tools/metadata/index
   /autoapi/image_processing/tools/mission_planning/index


Classes
-------

.. autoapisummary::

   image_processing.tools.UbloxGPSController


Functions
---------

.. autoapisummary::

   image_processing.tools.hashFile
   image_processing.tools.mapPixelCoordinates
   image_processing.tools.extractMetadata
   image_processing.tools.execute
   image_processing.tools.embedMetadata
   image_processing.tools.haversine_distance
   image_processing.tools.calculate_total_distance
   image_processing.tools.rotate_point_local
   image_processing.tools.plan_mission
   image_processing.tools.save_to_mission_planner_file
   image_processing.tools.export_search_area_waypoints
   image_processing.tools.sort_coordinates
   image_processing.tools.export_map
   image_processing.tools.generate_mission_from_params
   image_processing.tools.timestamp


Package Contents
----------------

.. py:function:: hashFile(file_path: str, algorithm: str = 'md5', chunk_size: int = 8192) -> str

   Compute a cryptographic hash of a file using streaming (chunked) reads.

   :param file_path: Path to the file to hash.
   :type file_path: str
   :param algorithm: Hash algorithm to use. Must be supported by `hashlib.new`
                     (e.g., "md5", "sha1", "sha256", "sha512"). Default is "md5".
   :type algorithm: str, optional
   :param chunk_size: Number of bytes to read per iteration. Larger values improve
                      performance for large files but use more memory. Default is 8192.
   :type chunk_size: int, optional

   :returns: Hexadecimal digest string representing the computed hash.
   :rtype: str

   :raises ValueError: If an unsupported hashing algorithm is provided.
   :raises FileNotFoundError: If the target file does not exist.
   :raises PermissionError: If the file cannot be opened or read.

   .. rubric:: Notes

   - File contents are processed in a memory-efficient streaming manner.
   - The returned digest is deterministic for a given `algorithm`.


.. py:function:: mapPixelCoordinates(pixel_position: tuple[int, int], homography_matrix: Optional[cv2.typing.MatLike] = None, homography_points: Optional[tuple[numpy.ndarray, numpy.ndarray]] = None) -> list[float] | list[None]

   Map a 2D pixel coordinate from one image space to another using a homography transform.

   Either a pre-computed homography matrix (`homography_matrix`) must be provided,
   or a pair of corresponding point sets (`homography_points`) will be used to
   estimate one via RANSAC.

   :param pixel_position: Input pixel coordinate `(x, y)` to be mapped.
   :type pixel_position: tuple[int, int]
   :param homography_matrix: A 3x3 homography matrix. If provided, it is used directly without recomputing.
   :type homography_matrix: cv2.typing.MatLike, optional
   :param homography_points: A tuple `(src_points, dst_points)` where each is an array of corresponding
                             2D points with shape `(N, 2)`, used to estimate the homography via
                             `cv2.findHomography` if `homography_matrix` is not supplied.
   :type homography_points: tuple[np.ndarray, np.ndarray], optional

   :returns: The mapped pixel coordinate as `[x_mapped, y_mapped]` if successful.
             Otherwise returns `[None, None]`.
   :rtype: list[float] | list[None]

   :raises ValueError: If neither `homography_matrix` nor `homography_points` is provided.

   .. rubric:: Notes

   • Output coordinates are floating-point values and not rounded or clipped.
   • If `homography_points` is used, RANSAC with reprojection threshold 5.0 is applied.
   • Returned coordinates are in the same pixel coordinate convention as the input
     (OpenCV uses `(x, y)` = `(col, row)`).


.. py:function:: extractMetadata(file_name)

   Extract relevant camera and geospatial metadata using ExifTool.

   :param file_name: Path to the image file to inspect.
   :type file_name: str

   :returns: `(metadata, latitude, longitude, altitude, yaw, pix_width, pix_height, focal_length)`
             or `None` if the file does not contain GPS metadata.
   :rtype: tuple or None

   .. rubric:: Notes

   - EXIF GPS longitude is negated so that West values become negative.
   - `yaw` is parsed from the `File:Comment` field using the format:
     `"pitch: <val> yaw: <val> roll: <val>"`.


.. py:function:: execute(command)

   Run a command with suppressed stdout/stderr.


.. py:function:: embedMetadata(file_name, latitude, longitudate, pitch, yaw, roll)

   Embed geolocation + orientation metadata into an image using ExifTool.

   :param file_name: Path to the output image file (will be modified in-place).
   :type file_name: str
   :param latitude: Decimal latitude (North positive, South negative).
   :type latitude: float
   :param longitude: Decimal longitude (East positive, West negative).
   :type longitude: float
   :param pitch: Pitch angle in degrees.
   :type pitch: float
   :param yaw: Yaw (heading) angle in degrees.
   :type yaw: float
   :param roll: Roll angle in degrees.
   :type roll: float

   .. rubric:: Notes

   - Uses `-overwrite_original`.
   - Commands are launched as separate subprocesses.
   - If running repeatedly consider batching into one call for efficiency.


.. py:class:: UbloxGPSController(port: str = '/dev/ttyACM0', baudrate: int = 38400, timeout: int = 1)

   Controller for a u-blox GNSS receiver using :mod:`ublox_gps`.

   This class manages:

   - Opening the serial connection to the GPS module.
   - Interpreting PVT (position, velocity, time) messages to determine
     whether a valid fix is available.
   - Extracting latitude/longitude coordinates.
   - Optionally retrieving vehicle attitude (roll, pitch, heading).

   :param port: Serial device path for the GPS receiver (for example,
                ``"/dev/ttyACM0"``), by default ``"/dev/ttyACM0"``.
   :type port: str, optional
   :param baudrate: Serial baud rate, by default ``38400``.
   :type baudrate: int, optional
   :param timeout: Read timeout in seconds for the serial port, by default ``1``.
   :type timeout: int, optional

   .. attribute:: port

      Serial device path used for the connection.

      :type: str

   .. attribute:: baudrate

      Serial baud rate for the connection.

      :type: int

   .. attribute:: timeout

      Serial read timeout in seconds.

      :type: int

   .. attribute:: connection

      Instance of :class:`ublox_gps.UbloxGps` once :meth:`connect`
      succeeds, otherwise None.

      :type: UbloxGps or None


   .. py:attribute:: port
      :value: '/dev/ttyACM0'



   .. py:attribute:: baudrate
      :value: 38400



   .. py:attribute:: timeout
      :value: 1



   .. py:attribute:: connection
      :type:  Optional[UbloxGps]
      :value: None



   .. py:method:: connect(port: Optional[str] = None, baudrate: Optional[int] = None, timeout: Optional[int] = None) -> bool

      Open a serial connection and initialize the u-blox GPS interface.

      :param port: Serial device path to use. If None, uses the controller's
                   configured :attr:`port`.
      :type port: str or None, optional
      :param baudrate: Baud rate to use. If None, uses :attr:`baudrate`.
      :type baudrate: int or None, optional
      :param timeout: Read timeout in seconds. If None, uses :attr:`timeout`.
      :type timeout: int or None, optional

      :returns: True if the connection is successfully established.
      :rtype: bool

      :raises GPSConnectionError: If the serial port cannot be opened or initialization fails.



   .. py:method:: has_fix(pvt: Any) -> bool

      Determine whether a PVT structure represents a valid GNSS fix.

      The fix is considered valid if both:

      - The ``gnssFixOK`` flag bit (bit 0) is set.
      - The fix type is 2D or better (``fixType >= 2``).

      :param pvt: PVT-like structure as returned by :meth:`UbloxGps.geo_coords`.
      :type pvt: Any

      :returns: True if the PVT message indicates a valid fix, otherwise False.
      :rtype: bool



   .. py:method:: getFixInfo() -> Optional[Dict[str, Any]]

      Retrieve a dictionary with detailed fix information.

      This method queries the GPS for a PVT fix and returns a summary
      including:

      - Whether a valid fix is present.
      - Fix type.
      - ``gnssFixOK`` flag.
      - Number of satellites.
      - Latitude and longitude.

      :returns: Dictionary with keys ``"has_fix"``, ``"fix_type"``,
                ``"gnssFixOK"``, ``"num_sv"``, ``"lat"``, and ``"lon"``,
                or None if no connection is available or no PVT message
                can be retrieved.
      :rtype: dict or None



   .. py:method:: getGPS() -> Optional[Tuple[float, float]]

      Get the current GPS position, if a valid fix exists.

      This method returns longitude and latitude in degrees, but only
      when the receiver reports a valid fix and the coordinates are
      not near (0, 0).

      :returns: Tuple ``(lon, lat)`` in degrees if a valid fix is available,
                otherwise None.
      :rtype: tuple of float or None



   .. py:method:: waitForFix(timeout_s: float = 30.0) -> Optional[Tuple[float, float]]

      Wait for a valid GPS fix up to a specified timeout.

      This method repeatedly polls the receiver until:

      - A valid fix is detected via :meth:`has_fix`, and
      - The reported coordinates are not near (0, 0), or
      - The timeout is reached.

      :param timeout_s: Maximum time to wait for a fix in seconds, by default ``30.0``.
      :type timeout_s: float, optional

      :returns: Tuple ``(lon, lat)`` in degrees if a valid fix is acquired
                within the timeout, otherwise None.
      :rtype: tuple of float or None



   .. py:method:: getAttitude() -> Optional[Tuple[float, float, float]]

      Retrieve vehicle attitude from the GPS receiver, if available.

      This method queries the receiver for a ``veh_attitude`` message
      and extracts roll, pitch, and heading if present.

      :returns: Tuple ``(roll, pitch, heading)`` in degrees if attitude
                information is available and complete, otherwise None.
      :rtype: tuple of float or None



   .. py:method:: disconnect()

      Close the underlying serial port, if it is open.

      This does not reset the :attr:`connection` attribute, but ensures
      that the hardware port is closed and resources are released.



.. py:function:: haversine_distance(point1, point2)

   Compute great-circle distance between two waypoints using the haversine formula.

   :param point1: First waypoint as ``(lat, lon, alt)`` in degrees and meters.
                  Altitude is ignored for the distance calculation.
   :type point1: tuple[float, float, float]
   :param point2: Second waypoint as ``(lat, lon, alt)``.
   :type point2: tuple[float, float, float]

   :returns: Great-circle distance between the two points in meters.
   :rtype: float

   .. rubric:: Notes

   The underlying formula is:

   .. math::

       d = 2 R \arctan2\left( \sqrt{a}, \sqrt{1 - a} \right),

   where

   .. math::

       a = \sin^2\left( \frac{\Delta\varphi}{2} \right)
         + \cos \varphi_1 \cos \varphi_2 \sin^2\left( \frac{\Delta\lambda}{2} \right),

   with latitude/longitude expressed in radians and :math:`R` the Earth
   radius (here :math:`R = 6371000` m).


.. py:function:: calculate_total_distance(waypoints)

   Compute the total travel distance along an ordered list of waypoints.

   :param waypoints: Ordered list of waypoints as ``(lat, lon, alt)``. Altitude is
                     ignored when computing distances.
   :type waypoints: sequence of tuple[float, float, float]

   :returns: Total path length in meters, obtained by summing haversine
             distances between successive points.
   :rtype: float


.. py:function:: rotate_point_local(point, angle)

   Rotate a 2D point about the origin by a given angle.

   :param point: Point to rotate, as ``(x, y)`` in local coordinates.
   :type point: tuple[float, float]
   :param angle: Rotation angle in radians, counter-clockwise.
   :type angle: float

   :returns: Rotated point coordinates ``(x', y')``.
   :rtype: tuple[float, float]


.. py:function:: plan_mission(airdrop_coords, photo_width_px, photo_height_px, horizontal_fov_deg, vertical_fov_deg, overlap_percent, altitude=100, row_traversal=False)

.. py:function:: save_to_mission_planner_file(waypoints, filename='mission.waypoints', reverse=False)

.. py:function:: export_search_area_waypoints(search_waypoints, filepath)

.. py:function:: sort_coordinates(coordinates)

.. py:function:: export_map(map_file_path, boundary_coords, drone_waypoints, angle, rect_centroid, transformer_to_utm, transformer_from_utm, ground_width, ground_height, n_cols, n_rows)

.. py:function:: generate_mission_from_params(bounds, photo_width, photo_height, horizontal_fov, vertical_fov, overlap, flight_altitude, waypoint_save_path='waypoints.json', html_save_path='mission_waypoints.html', is_reversed=False, row_traversal=False)

.. py:function:: timestamp(format: str = '%d_%m_%Y_%H_%M_%S') -> str

   Generate a timestamp string based on the current time.

   :param fmt: The desired timestamp format string following `datetime.strftime` directives.
               Default is "%d_%m_%Y_%H_%M_%S".

               Common format codes include:
               ----------------------------
               %Y : Year with century (e.g., 2025)
               %y : Year without century (00–99)
               %m : Month as a zero-padded decimal number (01–12)
               %B : Full month name (e.g., November)
               %b : Abbreviated month name (e.g., Nov)
               %d : Day of the month as a zero-padded decimal number (01–31)
               %A : Full weekday name (e.g., Tuesday)
               %a : Abbreviated weekday name (e.g., Tue)
               %H : Hour (24-hour clock, 00–23)
               %I : Hour (12-hour clock, 01–12)
               %p : AM or PM
               %M : Minute (00–59)
               %S : Second (00–59)
               %f : Microsecond (000000–999999)
               %z : UTC offset (e.g., +0000)
               %Z : Time zone name
               %j : Day of the year (001–366)
               %U : Week number (Sunday as first day of week)
               %W : Week number (Monday as first day of week)
   :type fmt: str, optional

   :returns: The formatted timestamp string.
   :rtype: str


