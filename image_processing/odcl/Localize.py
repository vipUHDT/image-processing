"""Georeferencing of image pixel coordinates to GPS positions.

Each backend converts a pixel location in a nadir-pointing camera image to a
latitude/longitude using the platform's position, altitude, and yaw plus the
camera's intrinsics; they differ in the map projection used for the local
offset math (UTM, local ENU, azimuthal equidistant, or a flat-earth
approximation).

Conventions
-----------
- The camera points straight down (nadir) and is mounted so the top of the
  image faces the aircraft's heading direction.
- Pixel ``x`` increases to the right, pixel ``y`` increases downward.
- ``yaw`` is the compass heading in degrees, clockwise from true north.
"""

import math
from dataclasses import astuple
from functools import lru_cache

import pymap3d as pm
from pyproj import Transformer

from image_processing import PlatformState
from image_processing.camera import CameraMetadata


class Georeference_Engine:
    """
    Dispatches georeferencing to a selected projection backend.

    Parameters
    ----------
    backend : str
        One of ``"utm"``, ``"enu"``, ``"aeqd"``, or ``"manual"``.
    altitude_offset : float, optional
        Ground elevation subtracted from the platform altitude to get
        height above ground level.
    """

    def __init__(self, backend, altitude_offset=0):
        self.camera_metadata = None
        self.backend = self.getBackends(backend)
        self.altitude_offset = altitude_offset

    def getBackends(self, backend):
        """Return the georeferencing function registered under ``backend``."""
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
        altitude_offset=None,
    ):
        """
        Convert a pixel coordinate to ``(latitude, longitude)``.

        Parameters
        ----------
        target_pixel_coordinates : tuple[int, int]
            ``(x, y)`` pixel position of the target in the image.
        platform_state : PlatformState
            Platform position and attitude at capture time.
        camera_metadata : CameraMetadata
            Camera intrinsics (sensor size, resolution, focal length).
        altitude_offset : float, optional
            Ground elevation subtracted from the platform altitude.
            Defaults to the offset the engine was constructed with.
        """
        if altitude_offset is None:
            altitude_offset = self.altitude_offset
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


def _pixel_to_east_north(
    target_pixel_coordinates,
    drone_altitude,
    altitude_offset,
    drone_yaw,
    sensor_w,
    sensor_h,
    pix_width,
    pix_height,
    focal_length,
) -> tuple[float, float]:
    """
    Convert a pixel position to the target's (east, north) offset in meters
    from the point directly below the platform.

    The pixel offset from the image center is first scaled to meters on the
    ground (using the footprint implied by the pinhole model at the platform's
    height above ground), then rotated by the compass heading. Scaling must
    happen before rotation because the per-axis meters-per-pixel factors
    differ.
    """
    altitude = drone_altitude - altitude_offset

    # Ground footprint of the image at this height above ground. The
    # trigonometry reduces to footprint = altitude * sensor / focal_length.
    ground_width = altitude * sensor_w / focal_length
    ground_height = altitude * sensor_h / focal_length

    target_pixel_x, target_pixel_y = target_pixel_coordinates
    delta_x = target_pixel_x - pix_width / 2
    delta_y = target_pixel_y - pix_height / 2

    # Camera frame in meters: +right of heading, +forward along heading.
    # Pixel y grows downward, i.e. opposite the heading direction.
    right_m = delta_x * ground_width / pix_width
    forward_m = -delta_y * ground_height / pix_height

    # Rotate camera frame into ENU. Yaw is clockwise from north, so
    # heading 0 maps forward->north, heading 90 maps forward->east.
    yaw_rad = math.radians(drone_yaw)
    east = right_m * math.cos(yaw_rad) + forward_m * math.sin(yaw_rad)
    north = forward_m * math.cos(yaw_rad) - right_m * math.sin(yaw_rad)

    return east, north


@lru_cache(maxsize=32)
def _projection_transformers(crs_projected: str) -> tuple[Transformer, Transformer]:
    """Return cached (to-projected, to-geodetic) transformers for a CRS."""
    return (
        Transformer.from_crs("EPSG:4326", crs_projected, always_xy=True),
        Transformer.from_crs(crs_projected, "EPSG:4326", always_xy=True),
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
    """Georeference a pixel by offsetting the platform position in UTM coordinates."""
    east, north = _pixel_to_east_north(
        target_pixel_coordinates,
        drone_altitude,
        altitude_offset,
        drone_yaw,
        sensor_w,
        sensor_h,
        pix_width,
        pix_height,
        focal_length,
    )

    # UTM zone from the drone's longitude; 326xx north, 327xx south.
    utm_zone = int((drone_longitude + 180) // 6) + 1
    hemisphere_code = 326 if drone_latitude >= 0 else 327
    crs_projected = f"EPSG:{hemisphere_code}{utm_zone:02d}"

    transformer, inv_transformer = _projection_transformers(crs_projected)

    drone_x, drone_y = transformer.transform(drone_longitude, drone_latitude)
    target_longitude, target_latitude = inv_transformer.transform(
        drone_x + east, drone_y + north
    )

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
    """Georeference a pixel using a local East-North-Up frame centered on the platform."""
    east, north = _pixel_to_east_north(
        target_pixel_coordinates,
        drone_altitude,
        altitude_offset,
        drone_yaw,
        sensor_w,
        sensor_h,
        pix_width,
        pix_height,
        focal_length,
    )

    target_lat, target_lon, _ = pm.enu2geodetic(
        east,
        north,
        0,  # nadir view, no vertical offset
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
    """Georeference a pixel using an azimuthal equidistant projection centered on the platform."""
    east, north = _pixel_to_east_north(
        target_pixel_coordinates,
        drone_altitude,
        altitude_offset,
        drone_yaw,
        sensor_w,
        sensor_h,
        pix_width,
        pix_height,
        focal_length,
    )

    # Azimuthal equidistant projection centered on the drone: the drone sits
    # at (0, 0), so the target is simply the ENU offset in projected space.
    proj_string = (
        f"+proj=aeqd +lat_0={drone_latitude} +lon_0={drone_longitude} "
        "+ellps=WGS84 +units=m +no_defs"
    )
    _, inv_transformer = _projection_transformers(proj_string)
    target_longitude, target_latitude = inv_transformer.transform(east, north)

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
    """Georeference a pixel using a flat-earth (meters-per-degree) approximation."""
    east, north = _pixel_to_east_north(
        target_pixel_coordinates,
        drone_altitude,
        altitude_offset,
        drone_yaw,
        sensor_w,
        sensor_h,
        pix_width,
        pix_height,
        focal_length,
    )

    meters_per_degree = 111319.944
    target_latitude = drone_latitude + north / meters_per_degree
    target_longitude = drone_longitude + east / (
        meters_per_degree * math.cos(math.radians(drone_latitude))
    )

    return target_latitude, target_longitude


def haversine(lat1, lon1, lat2, lon2):
    """Return the great-circle distance in meters between two GPS points."""
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
