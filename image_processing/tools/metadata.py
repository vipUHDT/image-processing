"""EXIF metadata extraction and embedding via exiftool."""

import subprocess
from typing import Any, Optional

from exiftool import ExifToolHelper


def extractMetadata(file_name: str) -> Optional[tuple[dict[str, Any], float, float, float, float, int, int, float]]:
    """
    Extract GPS position and orientation metadata from an image file.

    Longitude is negated because EXIF stores it as degrees East while this
    package works with Western-hemisphere coordinates. Yaw is parsed from a
    ``yaw:<value>`` token in the file's EXIF comment.

    Parameters
    ----------
    file_name : str
        Path to the image file.

    Returns
    -------
    tuple or None
        ``(metadata, latitude, longitude, altitude, yaw, pix_width,
        pix_height, focal_length)`` where ``metadata`` is the full exiftool
        tag dict, or None if the file has no GPS tags.
    """
    with ExifToolHelper() as et:
        metadata = et.get_metadata(file_name)[0]
        if "EXIF:GPSLatitude" not in metadata or "EXIF:GPSLongitude" not in metadata:
            return None

        latitude = metadata["EXIF:GPSLatitude"]
        longitude = -metadata["EXIF:GPSLongitude"]  # EXIF default is East, but we are in the West
        altitude = metadata["EXIF:GPSAltitude"]
        comment = metadata["File:Comment"]
        yaw = float(
            [component.split(":")[1] for component in comment.split() if component.startswith("yaw:")][0]
        )
        pix_width = metadata["File:ImageWidth"]
        pix_height = metadata["File:ImageHeight"]
        focal_length = metadata["EXIF:FocalLength"]
        return metadata, latitude, longitude, altitude, yaw, pix_width, pix_height, focal_length


def embedMetadata(
    file_name: str,
    latitude: float,
    longitude: float,
    altitude: float,
    pitch: float,
    yaw: float,
    roll: float,
) -> None:
    """
    Embed GPS position and orientation metadata into an image file in place.

    Orientation (pitch/yaw/roll) is stored in the EXIF comment in the format
    read back by ``extractMetadata``.

    Parameters
    ----------
    file_name : str
        Path to the image file to modify.
    latitude, longitude, altitude : float
        GPS position to embed.
    pitch, yaw, roll : float
        Platform orientation in degrees.
    """
    orientation = f"pitch: {pitch} yaw: {yaw} roll: {roll}"
    command = (
        "exiftool",
        "-overwrite_original",
        f"-comment={orientation}",
        f"-exif:gpslatitude={latitude}",
        f"-exif:gpslongitude={longitude}",
        f"-exif:gpsaltitude={altitude}",
        file_name,
    )
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
