"""Georeferencing of image pixel coordinates to GPS positions.

Each backend converts a pixel location in a nadir-pointing camera image to a
latitude/longitude using the platform's position, altitude, and yaw plus the
camera's intrinsics; they differ in the map projection used for the local
offset math (UTM, local ENU, azimuthal equidistant, or a flat-earth
approximation).
"""

import math
from dataclasses import astuple

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
        altitude_offset = 0
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
    """Georeference a pixel by offsetting the platform position in UTM coordinates."""
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
    """Georeference a pixel using a local East-North-Up frame centered on the platform."""
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
    """Georeference a pixel using an azimuthal equidistant projection centered on the platform."""
    # Constants for image resolution and camera field of view
    pixel_resolution = (pix_width, pix_height)  # Image pixel dimensions
    horizontal_fov = 2 * math.degrees(math.atan(sensor_w / (2 * focal_length)))
    vertical_fov = 2 * math.degrees(math.atan(sensor_h / (2 * focal_length)))

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
    """Georeference a pixel using a flat-earth (meters-per-degree) approximation."""
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