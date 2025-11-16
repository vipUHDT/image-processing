"""
Core shared data structures and initialization helpers for the
``image_processing`` package.

This module provides lightweight data containers used throughout the
camera, ODCL (object detection, classification, localization), and data
management subsystems:

- :class:`PlatformState` — Represents the telemetry and attitude state
  of the sensing platform (e.g., UAV, rover, robot) at the moment an
  image is acquired.
- :class:`QueuedImage` — Couples a captured image with the associated
  platform state for downstream processing (e.g., detection, geolocation).

Logging is configured using a ``NullHandler`` to avoid forcing default
logging behavior on user applications.
"""

import logging
from logging import NullHandler
from dataclasses import dataclass
from typing import Optional
import cv2

@dataclass 
class PlatformState:
    """
    Platform telemetry and attitude state associated with an image capture
    event or detection cycle.

    This structure is intended to be populated from onboard sensors
    (e.g., GNSS, IMU) or log data, and used by geolocation functions to
    project pixel detections into Earth-referenced coordinates.

    Parameters
    ----------
    altitude : float, optional
        Platform altitude above ground level in meters.
    latitude : float, optional
        Geographic latitude (positive north) in decimal degrees.
    longitude : float, optional
        Geographic longitude (positive east) in decimal degrees.
    pitch : float, optional
        Platform pitch angle in degrees (positive nose-up).
    yaw : float, optional
        Platform yaw/heading angle in degrees (0° = North, +CW).
    roll : float, optional
        Platform roll angle in degrees (positive right-wing-down).
    """
    altitude: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pitch: Optional[float] = None
    yaw: Optional[float] = None
    roll: Optional[float] = None

@dataclass
class QueuedImage:
    """
    Container for an image paired with the corresponding platform state,
    used for asynchronous or batched image processing pipelines.

    Parameters
    ----------
    image : cv2.typing.MatLike
        The captured image frame (BGR or grayscale), typically originating
        from a live stream or logged dataset.
    platform_state : PlatformState
        The telemetry and attitude state at the time of image acquisition.

    Notes
    -----
    Instances of this type are typically passed into worker queues inside
    :class:`~image_processing.odcl.detection.DetectionManager`.
    """
    image: cv2.typing.MatLike
    platform_state: PlatformState
