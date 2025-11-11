image_processing.tools
======================

.. py:module:: image_processing.tools


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


Package Contents
----------------

.. py:function:: hashFile(file_path: str, algorithm: str = 'md5', chunk_size: int = 8192) -> str

.. py:function:: mapPixelCoordinates(pixel_position: tuple[int, int], homography_matrix: Optional[cv2.typing.MatLike] = None, homography_points: Optional[tuple[numpy.ndarray, numpy.ndarray]] = None) -> list[float] | list[None]

   Map a pixel coordinate (x, y) from one image to another using a homography.
   Returns the mapped coordinate as [x', y'] or None if mapping fails.


.. py:function:: extractMetadata(file_name)

.. py:function:: execute(command)

.. py:function:: embedMetadata(file_name, latitude, longitudate, pitch, yaw, roll)

.. py:class:: UbloxGPSController(port: str = '/dev/ttyACM0', baudrate: int = 38400, timeout: int = 1)

   .. py:attribute:: port
      :value: '/dev/ttyACM0'



   .. py:attribute:: baudrate
      :value: 38400



   .. py:attribute:: timeout
      :value: 1



   .. py:attribute:: connection
      :type:  Optional[ublox_gps.UbloxGps]
      :value: None



   .. py:method:: connect(port: Optional[str] = None, baudrate: Optional[int] = None, timeout: Optional[int] = None) -> bool


   .. py:method:: has_fix(pvt: Any) -> bool


   .. py:method:: getFixInfo() -> Optional[Dict[str, Any]]


   .. py:method:: getGPS() -> Optional[Tuple[float, float]]


   .. py:method:: waitForFix(timeout_s: float = 30.0) -> Optional[Tuple[float, float]]


   .. py:method:: getAttitude() -> Optional[Tuple[float, float, float]]


   .. py:method:: disconnect()


.. py:function:: haversine_distance(point1, point2)

.. py:function:: calculate_total_distance(waypoints)

.. py:function:: rotate_point_local(point, angle)

.. py:function:: plan_mission(airdrop_coords, photo_width_px, photo_height_px, horizontal_fov_deg, vertical_fov_deg, overlap_percent, altitude=100, row_traversal=False)

.. py:function:: save_to_mission_planner_file(waypoints, filename='mission.waypoints', reverse=False)

.. py:function:: export_search_area_waypoints(search_waypoints, filepath)

.. py:function:: sort_coordinates(coordinates)

.. py:function:: export_map(map_file_path, boundary_coords, drone_waypoints, angle, rect_centroid, transformer_to_utm, transformer_from_utm, ground_width, ground_height, n_cols, n_rows)

.. py:function:: generate_mission_from_params(bounds, photo_width, photo_height, horizontal_fov, vertical_fov, overlap, flight_altitude, waypoint_save_path='waypoints.json', html_save_path='mission_waypoints.html', is_reversed=False, row_traversal=False)

