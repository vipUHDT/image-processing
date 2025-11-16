image_processing.tools.mission_planning
=======================================

.. py:module:: image_processing.tools.mission_planning

.. autoapi-nested-parse::

   Mission-planning utilities for coverage flights and airdrop areas.

   This module computes camera footprints and waypoint grids for a given
   search/airdrop polygon, based on camera field of view (FOV), image size,
   desired overlap, and flight altitude. It also exports waypoints in formats
   compatible with Mission Planner and as an interactive Folium HTML map.

   Core steps
   ----------
   1. Convert the boundary polygon to a suitable projected coordinate system.
   2. Compute the minimum rotated bounding rectangle and its orientation.
   3. Build an evenly spaced grid of waypoints in that rotated frame, honoring
      a given image overlap percentage.
   4. Convert the grid back to latitude/longitude.
   5. Optionally export:

      - A Mission Planner `.waypoints` file.
      - A JSON file of search area waypoints.
      - A Folium map showing boundary, waypoints, and per-image footprints.

   Distances on the sphere use the haversine formula:

   .. math::

       d = 2 R \arctan2\left( \sqrt{a}, \sqrt{1 - a} \right),

   with

   .. math::

       a = \sin^2\left( \frac{\Delta\varphi}{2} \right)
         + \cos \varphi_1 \cos \varphi_2 \sin^2\left( \frac{\Delta\lambda}{2} \right),

   and :math:`R = 6371000` meters.



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

