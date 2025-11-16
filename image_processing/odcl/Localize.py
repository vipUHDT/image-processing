"""
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

   \\text{FOV} = 2 \\arctan\\left( \\frac{\\text{sensor\\_size}}{2 f} \\right),

and a simple ground-footprint scaling at altitude:

.. math::

   W = 2 h \\tan\\left( \\frac{\\text{FOV}_x}{2} \\right), \\quad
   H = 2 h \\tan\\left( \\frac{\\text{FOV}_y}{2} \\right),

where :math:`h` is altitude, :math:`f` is focal length, and
:math:`W, H` are the ground-projected footprint widths in meters.
"""

import math
from pyproj import Transformer
import math
from image_processing import *
from image_processing.camera import *
from dataclasses import astuple
import pymap3d as pm


class Georeference_Engine:
    """
    Engine for converting pixel coordinates into GPS coordinates.

    This class selects one of several backend functions for georeferencing
    (e.g., UTM, ENU, azimuthal-equidistant, or manual) and calls it with
    a unified interface based on platform state and camera metadata.

    Parameters
    ----------
    backend : str
        Name of the georeferencing backend to use. Must be one of
        ``"utm"``, ``"enu"``, ``"aeqd"``, or ``"manual"``.
    altitude_offset : float, optional
        Offset applied to the drone altitude prior to computing the ground
        footprint, by default 0.

    Attributes
    ----------
    camera_metadata : CameraMetadata or None
        Optional camera metadata (not directly used in current implementation).
    backend : callable
        Selected backend function implementing georeferencing logic.
    altitude_offset : float
        Stored altitude offset passed through to the backend.
    """
    def __init__(self, backend, altitude_offset=0):
        self.camera_metadata = None
        self.backend = self.getBackends(backend)
        self.altitude_offset = altitude_offset

    def getBackends(self, backend):
        """
        Resolve a backend name into a georeferencing function.

        Parameters
        ----------
        backend : str
            Name of the georeferencing backend (``"utm"``, ``"enu"``,
            ``"aeqd"``, or ``"manual"``).

        Returns
        -------
        callable
            Backend function implementing the requested georeference method.

        Raises
        ------
        ValueError
            If an unknown backend name is provided.
        """
        backends = {
            "utm": georeference_utm,
            "enu": georeference_enu,
            "aeqd": georeference_aeqd,
            "manual": georeference_manual,
        }
        reference = backends.get(backend)
        if reference is None:
            raise ValueError(
                f"Unknown georeferencing backend '{backend}'. Choose one of {list(backends)}"
            )
        return reference

    def georeference(
        self,
        target_pixel_coordinates: tuple[int, int],
        platform_state: PlatformState,
        camera_metadata: CameraMetadata,
        altitude_offset = 0
    ):
        """
        Georeference a pixel coordinate into latitude/longitude.

        This method unpacks platform state and camera metadata into the
        arguments expected by the configured backend, and returns the
        resulting GPS coordinates.

        Parameters
        ----------
        target_pixel_coordinates : tuple of int
            Pixel coordinates :math:`(x, y)` of the target in image space.
        platform_state : PlatformState
            Platform (drone) state containing altitude, latitude, longitude,
            pitch, yaw, and roll (in that order).
        camera_metadata : CameraMetadata
            Camera metadata containing sensor dimensions, image resolution,
            and focal length.
        altitude_offset : float, optional
            Offset to subtract from platform altitude before computing
            ground footprint, by default 0.

        Returns
        -------
        tuple of float
            Target latitude and longitude in degrees.
        """
        altitude, latitude, longitude, pitch, yaw, roll = astuple(platform_state)
        sensor_width, sensor_height, image_width, image_height, focal_length = astuple(
            camera_metadata
        )
        return self.backend(
            target_pixel_coordinates,
            latitude,
            longitude,
            altitude,
            altitude_offset,
            yaw,
            sensor_width,
            sensor_height,
            image_width,
            image_height,
            focal_length,
        )


def georeference_utm(
    target_pixel_coordinates,
    drone_latitude,
    drone_longitude,
    drone_altitude,
    altitude_offset,
    drone_yaw,
    sensor_w,
    sensor_h,
    pix_width,
    pix_height,
    focal_length,
):
    """
    Georeference using a UTM projection.

    This backend:

    1. Computes camera field-of-view (FOV) from sensor size and focal length:

       .. math::

          \\text{FOV}_x = 2 \\arctan\\left( \\frac{w}{2 f} \\right), \\quad
          \\text{FOV}_y = 2 \\arctan\\left( \\frac{h}{2 f} \\right).

    2. Computes the ground footprint width/height at altitude:

       .. math::

          W = 2 h \\tan\\left( \\frac{\\text{FOV}_x}{2} \\right), \\quad
          H = 2 h \\tan\\left( \\frac{\\text{FOV}_y}{2} \\right).

    3. Converts drone lat/lon to UTM, applies pixel-based offsets scaled
       to :math:`W, H` and rotated by yaw, and converts back to WGS84
       coordinates.

    Parameters
    ----------
    target_pixel_coordinates : tuple of int
        Target pixel coordinates :math:`(x, y)` in image space.
    drone_latitude : float
        Drone latitude in degrees.
    drone_longitude : float
        Drone longitude in degrees.
    drone_altitude : float
        Drone altitude above ground/sea level (units consistent with offset).
    altitude_offset : float
        Altitude offset to subtract before computing footprint.
    drone_yaw : float
        Drone yaw (heading) in degrees.
    sensor_w : float
        Sensor width (same units as :paramref:`focal_length`).
    sensor_h : float
        Sensor height (same units as :paramref:`focal_length`).
    pix_width : int
        Image width in pixels.
    pix_height : int
        Image height in pixels.
    focal_length : float
        Camera focal length (same units as :paramref:`sensor_w` and
        :paramref:`sensor_h`).

    Returns
    -------
    tuple of float
        Target latitude and longitude in degrees.
    """
    # Constants for image resolution and camera field of view
    pixel_resolution = (pix_width, pix_height)  # Image pixel dimensions
    horizontal_fov = 2 * math.degrees(math.atan(sensor_w / (2 * focal_length)))
    vertical_fov = 2 * math.degrees(math.atan(sensor_h / (2 * focal_length)))

    altitude = drone_altitude - altitude_offset

    # Calculate the real-world dimensions of the image at the target altitude
    image_width = 2 * altitude * math.tan(math.radians(horizontal_fov / 2))
    image_height = 2 * altitude * math.tan(math.radians(vertical_fov / 2))

    # Calculate the UTM zone based on the drone's initial longitude
    utm_zone = int((drone_longitude + 180) // 6) + 1
    hemisphere_code = (
        326 if drone_latitude >= 0 else 327
    )  # 326 for Northern Hemisphere, 327 for Southern
    crs_projected = (
        f"EPSG:{hemisphere_code}{utm_zone:02d}"  # Complete EPSG code for UTM zone
    )

    # Initialize pyproj transformers for coordinate conversions
    transformer = Transformer.from_crs("EPSG:4326", crs_projected, always_xy=True)
    inv_transformer = Transformer.from_crs(crs_projected, "EPSG:4326", always_xy=True)

    # Convert the drone's initial GPS coordinates to UTM
    drone_x, drone_y = transformer.transform(drone_longitude, drone_latitude)

    # Target pixel offset from image center
    target_pixel_x, target_pixel_y = target_pixel_coordinates
    image_center_x, image_center_y = pixel_resolution[0] / 2, pixel_resolution[1] / 2
    delta_x, delta_y = target_pixel_x - image_center_x, target_pixel_y - image_center_y
    delta_y *= 1

    # Adjust for drone's yaw (orientation)
    drone_yaw_rad = math.radians(drone_yaw)
    corrected_delta_x = delta_x * math.cos(drone_yaw_rad) - delta_y * math.sin(
        drone_yaw_rad
    )
    corrected_delta_y = delta_x * math.sin(drone_yaw_rad) + delta_y * math.cos(
        drone_yaw_rad
    )

    # Convert pixel offsets to meters
    x_meters = corrected_delta_x * image_width / pixel_resolution[0]
    y_meters = corrected_delta_y * image_height / pixel_resolution[1]

    # Calculate the target position in UTM coordinates by adding the offsets
    target_x = drone_x + x_meters
    target_y = drone_y + y_meters

    # Convert the final target position back to GPS coordinates
    target_longitude, target_latitude = inv_transformer.transform(target_x, target_y)

    return target_latitude, target_longitude


def georeference_enu(
    target_pixel_coordinates,
    drone_latitude,
    drone_longitude,
    drone_altitude,
    altitude_offset,
    drone_yaw,
    sensor_w,
    sensor_h,
    pix_width,
    pix_height,
    focal_length,
):
    
    """
    Georeference using a local ENU (East–North–Up) frame.

    This backend:

    - Computes FOV and footprint size as in :func:`georeference_utm`.
    - Converts pixel offsets (relative to image center) into meters.
    - Rotates those offsets by yaw into ENU directions.
    - Uses :func:`pymap3d.enu2geodetic` to convert ENU offsets to
      latitude/longitude.

    Parameters
    ----------
    target_pixel_coordinates : tuple of int
        Target pixel coordinates :math:`(x, y)` in image space.
    drone_latitude : float
        Drone latitude in degrees.
    drone_longitude : float
        Drone longitude in degrees.
    drone_altitude : float
        Drone altitude above reference.
    altitude_offset : float
        Altitude offset to subtract before computing footprint.
    drone_yaw : float
        Drone yaw (heading) in degrees.
    sensor_w : float
        Sensor width (same units as :paramref:`focal_length`).
    sensor_h : float
        Sensor height (same units as :paramref:`focal_length`).
    pix_width : int
        Image width in pixels.
    pix_height : int
        Image height in pixels.
    focal_length : float
        Camera focal length.

    Returns
    -------
    tuple of float
        Target latitude and longitude in degrees.
    """
    # Adjust altitude if necessary
    altitude = drone_altitude - altitude_offset

    # Field of view
    horizontal_fov = 2 * math.degrees(math.atan(sensor_w / (2 * focal_length)))
    vertical_fov = 2 * math.degrees(math.atan(sensor_h / (2 * focal_length)))

    # Ground footprint dimensions at altitude
    image_width = 2 * altitude * math.tan(math.radians(horizontal_fov / 2))
    image_height = 2 * altitude * math.tan(math.radians(vertical_fov / 2))

    # Image center and pixel offset
    image_center_x, image_center_y = pix_width / 2, pix_height / 2
    target_pixel_x, target_pixel_y = target_pixel_coordinates

    delta_x = target_pixel_x - image_center_x
    delta_y = target_pixel_y - image_center_y
    delta_y *= 1  # Flip y to match ENU

    # Rotate according to yaw (convert to radians)
    yaw_rad = math.radians(drone_yaw)
    corrected_dx = delta_x * math.cos(yaw_rad) - delta_y * math.sin(yaw_rad)
    corrected_dy = delta_x * math.sin(yaw_rad) + delta_y * math.cos(yaw_rad)

    # Convert from pixel offset to real-world distance in meters
    east_offset = corrected_dx * image_width / pix_width
    north_offset = corrected_dy * image_height / pix_height
    up_offset = 0  # Nadir view, so no change in vertical

    # Convert local ENU offset back to GPS
    target_lat, target_lon, _ = pm.enu2geodetic(
        east_offset,
        north_offset,
        up_offset,
        drone_latitude,
        drone_longitude,
        drone_altitude,
    )

    return target_lat, target_lon


def georeference_aeqd(
    target_pixel_coordinates,
    drone_latitude,
    drone_longitude,
    drone_altitude,
    altitude_offset,
    drone_yaw,
    sensor_w,
    sensor_h,
    pix_width,
    pix_height,
    focal_length,
):
    """
    Georeference using a local Azimuthal Equidistant projection.

    This backend constructs an azimuthal equidistant (AEQD) projection
    centered on the drone position, performs all offsets in that local
    metric space, and converts back to WGS84 coordinates.

    Parameters
    ----------
    target_pixel_coordinates : tuple of int
        Target pixel coordinates :math:`(x, y)` in image space.
    drone_latitude : float
        Drone latitude in degrees.
    drone_longitude : float
        Drone longitude in degrees.
    drone_altitude : float
        Drone altitude above reference.
    altitude_offset : float
        Altitude offset to subtract before computing footprint.
    drone_yaw : float
        Drone yaw (heading) in degrees.
    sensor_w : float
        Sensor width.
    sensor_h : float
        Sensor height.
    pix_width : int
        Image width in pixels.
    pix_height : int
        Image height in pixels.
    focal_length : float
        Camera focal length.

    Returns
    -------
    tuple of float
        Target latitude and longitude in degrees.
    """
    # Constants for image resolution and camera field of view
    pixel_resolution = (pix_width, pix_height)  # Image pixel dimensions
    horiz_fov = 2 * math.degrees(math.atan(sensor_w / (2 * focal_length)))
    vert_fov = 2 * math.degrees(math.atan(sensor_h / (2 * focal_length)))
    horizontal_fov = horiz_fov  # Horizontal field of view in degrees
    vertical_fov = vert_fov  # Vertical field of view in degrees

    altitude = drone_altitude - altitude_offset

    # Calculate the real-world dimensions of the image at the target altitude
    image_width = 2 * altitude * math.tan(math.radians(horizontal_fov / 2))
    image_height = 2 * altitude * math.tan(math.radians(vertical_fov / 2))

    # --- Custom Projection Block ---
    # Define an Azimuthal Equidistant projection centered on the drone coordinates.
    proj_string = f"+proj=aeqd +lat_0={drone_latitude} +lon_0={drone_longitude} +ellps=WGS84 +units=m +no_defs"
    transformer = Transformer.from_crs("EPSG:4326", proj_string, always_xy=True)
    inv_transformer = Transformer.from_crs(proj_string, "EPSG:4326", always_xy=True)
    # Convert the drone's GPS coordinates to the custom projection coordinates.
    drone_x, drone_y = transformer.transform(drone_longitude, drone_latitude)
    # --- End Custom Projection Block ---

    # Target pixel offset from image center
    target_pixel_x, target_pixel_y = target_pixel_coordinates
    image_center_x, image_center_y = pixel_resolution[0] / 2, pixel_resolution[1] / 2
    delta_x, delta_y = target_pixel_x - image_center_x, target_pixel_y - image_center_y
    delta_y *= 1

    # Adjust for drone's yaw (orientation)
    drone_yaw_rad = math.radians(drone_yaw)
    corrected_delta_x = delta_x * math.cos(drone_yaw_rad) - delta_y * math.sin(
        drone_yaw_rad
    )
    corrected_delta_y = delta_x * math.sin(drone_yaw_rad) + delta_y * math.cos(
        drone_yaw_rad
    )

    # Convert pixel offsets to meters
    x_meters = corrected_delta_x * image_width / pixel_resolution[0]
    y_meters = corrected_delta_y * image_height / pixel_resolution[1]

    # Calculate the target position in custom projection coordinates by adding the offsets
    target_x = drone_x + x_meters
    target_y = drone_y + y_meters

    # Convert the final target position back to GPS coordinates
    target_longitude, target_latitude = inv_transformer.transform(target_x, target_y)

    return target_latitude, target_longitude


def georeference_manual(
    target_pixel_coordinates,
    drone_latitude,
    drone_longitude,
    drone_altitude,
    altitude_offset,
    drone_yaw,
    sensor_w,
    sensor_h,
    pix_width,
    pix_height,
    focal_length,
):
    """
    Georeference using a simple manual flat-earth approximation.

    This backend uses a constant meters-per-degree approximation to convert
    camera-plane offsets to latitude and longitude. It is less accurate at
    large distances or high latitudes, but is simple and lightweight.

    Specifically:

    .. math::

       \\Delta \\varphi \\approx \\frac{y_{\\text{meters}}}{R_\\varphi}, \\quad
       \\Delta \\lambda \\approx \\frac{x_{\\text{meters}}}{R_\\lambda \\cos \\varphi},

    where :math:`R_\\varphi \\approx R_\\lambda \\approx 111319.944` meters
    per degree near the equator.

    Parameters
    ----------
    target_pixel_coordinates : tuple of int
        Target pixel coordinates :math:`(x, y)` in image space.
    drone_latitude : float
        Drone latitude in degrees.
    drone_longitude : float
        Drone longitude in degrees.
    drone_altitude : float
        Drone altitude above reference.
    altitude_offset : float
        Altitude offset to subtract before computing footprint.
    drone_yaw : float
        Drone yaw (heading) in degrees.
    sensor_w : float
        Sensor width.
    sensor_h : float
        Sensor height.
    pix_width : int
        Image width in pixels.
    pix_height : int
        Image height in pixels.
    focal_length : float
        Camera focal length.

    Returns
    -------
    tuple of float
        Target latitude and longitude in degrees.
    """
    # Constants
    pixel_resolution = (pix_width, pix_height)

    # Camera field of view = 2*arctan(sensor_size/(2*focal_length))
    horizontal_fov = 2 * math.degrees(
        math.atan(sensor_w / (2 * focal_length))
    )  # degrees
    vertical_fov = 2 * math.degrees(math.atan(sensor_h / (2 * focal_length)))  # degrees

    altitude = drone_altitude - altitude_offset

    # Image real-world dimensions
    image_width = 2 * altitude * math.tan(math.radians(horizontal_fov / 2))
    image_height = 2 * altitude * math.tan(math.radians(vertical_fov / 2))

    # Drone orientation
    drone_yaw_rad = math.radians(drone_yaw)

    # Target pixel coordinates
    target_pixel_x, target_pixel_y = target_pixel_coordinates

    # Image center coordinates
    image_center_x = pixel_resolution[0] / 2
    image_center_y = pixel_resolution[1] / 2

    # Calculate distance from image center to target pixel
    delta_x = target_pixel_x - image_center_x
    delta_y = target_pixel_y - image_center_y
    delta_y *= 1

    # Calculate distance from image center to target pixel after correction
    corrected_delta_x = delta_x * math.cos(drone_yaw_rad) - delta_y * math.sin(
        drone_yaw_rad
    )
    corrected_delta_y = delta_x * math.sin(drone_yaw_rad) + delta_y * math.cos(
        drone_yaw_rad
    )

    # Calculate new target pixel coordinates after adjustment
    corrected_target_pixel_x = image_center_x + corrected_delta_x
    corrected_target_pixel_y = image_center_y + corrected_delta_y

    # Calculate target coordinates in meters (assuming linear relationship)
    x_meters = (
        (corrected_target_pixel_x - image_center_x) * image_width / pixel_resolution[0]
    )
    y_meters = (
        (corrected_target_pixel_y - image_center_y) * image_height / pixel_resolution[1]
    )

    # Convert drone-centric coordinates to global coordinates
    target_latitude = drone_latitude + (y_meters / 111319.944)
    target_longitude = drone_longitude + (
        x_meters / (111319.944 * math.cos(math.radians(drone_latitude)))
    )

    return target_latitude, target_longitude


# Return Distance Between Two GPS points in meters
def haversine(lat1, lon1, lat2, lon2):
    """
    Compute great-circle distance between two GPS points using the haversine formula.

    The haversine distance on a sphere of radius :math:`R` is:

    .. math::

       d = 2 R \\arctan2\\left(
           \\sqrt{a},
           \\sqrt{1 - a}
       \\right),

    where

    .. math::

       a = \\sin^2\\left( \\frac{\\Delta\\varphi}{2} \\right)
         + \\cos \\varphi_1 \\cos \\varphi_2 \\sin^2\\left( \\frac{\\Delta\\lambda}{2} \\right),

    and :math:`\\Delta\\varphi` and :math:`\\Delta\\lambda` are latitude and
    longitude differences in radians. This implementation uses
    :math:`R = 6371` km and returns distance in meters.

    Parameters
    ----------
    lat1 : float
        Latitude of the first point in degrees.
    lon1 : float
        Longitude of the first point in degrees.
    lat2 : float
        Latitude of the second point in degrees.
    lon2 : float
        Longitude of the second point in degrees.

    Returns
    -------
    float
        Great-circle distance between the two points in meters.
    """
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    radius = 6371  # Radius of earth in kilometers. Use 3956 for miles
    distance = radius * c * 1000  # Convert to meters

    return distance