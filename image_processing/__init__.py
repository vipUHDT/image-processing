"""UHDT image-processing package: cameras, detection, georeferencing, and tooling."""

from dataclasses import dataclass
from typing import Optional

import cv2


@dataclass
class PlatformState:
    """Position and attitude of the platform (aircraft) at capture time."""

    altitude: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pitch: Optional[float] = None
    yaw: Optional[float] = None
    roll: Optional[float] = None


@dataclass
class QueuedImage:
    """An image paired with the platform state at the moment it was captured."""

    image: cv2.typing.MatLike
    platform_state: PlatformState
