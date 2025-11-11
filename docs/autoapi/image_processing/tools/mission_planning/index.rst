image_processing.tools.mission_planning
=======================================

.. py:module:: image_processing.tools.mission_planning


Functions
---------

.. autoapisummary::

   image_processing.tools.mission_planning.haversine_distance
   image_processing.tools.mission_planning.calculate_total_distance
   image_processing.tools.mission_planning.rotate_point_local
   image_processing.tools.mission_planning.plan_mission
   image_processing.tools.mission_planning.save_to_mission_planner_file
   image_processing.tools.mission_planning.export_search_area_waypoints
   image_processing.tools.mission_planning.sort_coordinates
   image_processing.tools.mission_planning.export_map
   image_processing.tools.mission_planning.generate_mission_from_params


Module Contents
---------------

.. py:function:: haversine_distance(point1, point2)

.. py:function:: calculate_total_distance(waypoints)

.. py:function:: rotate_point_local(point, angle)

.. py:function:: plan_mission(airdrop_coords, photo_width_px, photo_height_px, horizontal_fov_deg, vertical_fov_deg, overlap_percent, altitude=100, row_traversal=False)

.. py:function:: save_to_mission_planner_file(waypoints, filename='mission.waypoints', reverse=False)

.. py:function:: export_search_area_waypoints(search_waypoints, filepath)

.. py:function:: sort_coordinates(coordinates)

.. py:function:: export_map(map_file_path, boundary_coords, drone_waypoints, angle, rect_centroid, transformer_to_utm, transformer_from_utm, ground_width, ground_height, n_cols, n_rows)

.. py:function:: generate_mission_from_params(bounds, photo_width, photo_height, horizontal_fov, vertical_fov, overlap, flight_altitude, waypoint_save_path='waypoints.json', html_save_path='mission_waypoints.html', is_reversed=False, row_traversal=False)

