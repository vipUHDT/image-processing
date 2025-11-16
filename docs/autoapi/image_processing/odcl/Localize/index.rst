image_processing.odcl.Localize
==============================

.. py:module:: image_processing.odcl.Localize

.. autoapi-nested-parse::

   Georeferencing utilities for ODCL detections.

   This module provides:

   - :class:`Georeference_Engine`, a small wrapper that selects and invokes
     one of several georeferencing backends (UTM, ENU, azimuthal-equidistant,
     or a manual flat-earth approximation).
   - Backend functions (:func:`georeference_utm`, :func:`georeference_enu`,
     :func:`georeference_aeqd`, :func:`georeference_manual`) that convert
     pixel coordinates in an image into latitude/longitude coordinates using
     drone pose and camera intrinsics.
   - :func:`haversine`, a helper for computing great-circle distances
     between two GPS points in meters.

   All backends assume a nadir-looking camera and use the standard pinhole
   camera relation:

   .. math::

      \text{FOV} = 2 \arctan\left( \frac{\text{sensor\_size}}{2 f} \right),

   and a simple ground-footprint scaling at altitude:

   .. math::

      W = 2 h \tan\left( \frac{\text{FOV}_x}{2} \right), \quad
      H = 2 h \tan\left( \frac{\text{FOV}_y}{2} \right),

   where :math:`h` is altitude, :math:`f` is focal length, and
   :math:`W, H` are the ground-projected footprint widths in meters.



Classes
-------

.. autoapisummary::

   image_processing.odcl.Localize.Georeference_Engine


Functions
---------

.. autoapisummary::

   image_processing.odcl.Localize.georeference_utm
   image_processing.odcl.Localize.georeference_enu
   image_processing.odcl.Localize.georeference_aeqd
   image_processing.odcl.Localize.georeference_manual
   image_processing.odcl.Localize.haversine


Module Contents
---------------

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


