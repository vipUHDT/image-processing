"""General-purpose tools: hashing, homography, metadata, GPS, mission planning, and video."""

from datetime import datetime

from .gps import GPSConnectionError, UbloxGPSController
from .hash import hashFile
from .homography import cropRGBToMatchIR, mapPixelCoordinates, resizeIRToMatchRGB
from .metadata import embedMetadata, extractMetadata
from .mission_planning import (
    calculate_total_distance,
    export_map,
    export_search_area_waypoints,
    generate_mission_from_params,
    haversine_distance,
    plan_mission,
    save_to_mission_planner_file,
    sort_coordinates,
)
from .temperature import imageToTemperature, pixelToTemperature, temperature_to_pixel
from .video import extractFrames, extractSynchronizedFrames

__all__ = [
    "GPSConnectionError",
    "UbloxGPSController",
    "calculate_total_distance",
    "cropRGBToMatchIR",
    "embedMetadata",
    "export_map",
    "export_search_area_waypoints",
    "extractFrames",
    "extractMetadata",
    "extractSynchronizedFrames",
    "generate_mission_from_params",
    "hashFile",
    "haversine_distance",
    "imageToTemperature",
    "mapPixelCoordinates",
    "pixelToTemperature",
    "plan_mission",
    "resizeIRToMatchRGB",
    "save_to_mission_planner_file",
    "sort_coordinates",
    "temperature_to_pixel",
    "timestamp",
]


def timestamp(format: str = "%d_%m_%Y_%H_%M_%S") -> str:
    """
    Generate a timestamp string based on the current time.

    Parameters
    ----------
    format : str, optional
        The desired timestamp format string following `datetime.strftime`
        directives. Default is "%d_%m_%Y_%H_%M_%S".

    Returns
    -------
    str
        The formatted timestamp string.
    """
    return datetime.now().strftime(format)
