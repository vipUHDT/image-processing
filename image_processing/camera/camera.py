"""Abstract camera interfaces and shared camera metadata types."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

LOGGER = logging.getLogger(__name__)


class CameraBackend(ABC):
    """Interface for camera backends that manage device connection and setup."""

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    def initialize(self) -> None:
        """Prepare the backend for capture (e.g., connect to the device)."""
        ...

    @abstractmethod
    def setConnection(self, client: str, host: str, username: str, password: str) -> None:
        """Store the connection parameters for the remote device."""
        ...

    @abstractmethod
    def connect(self) -> None:
        """Establish the connection to the device."""
        ...


@dataclass
class CameraMetadata:
    """Physical sensor and image parameters used for georeferencing.

    Attributes
    ----------
    sensor_width, sensor_height : float
        Sensor dimensions in millimeters.
    image_width, image_height : int
        Image resolution in pixels.
    focal_length : float
        Lens focal length in millimeters.
    """

    sensor_width: float
    sensor_height: float
    image_width: int
    image_height: int
    focal_length: float


class Camera(ABC):
    """
    Base class for cameras exposing a common backend/connection interface.

    Parameters
    ----------
    name : str
        Human-readable camera identifier.
    metadata : CameraMetadata, optional
        Sensor parameters used for georeferencing.
    """

    def __init__(self, name: str, metadata: Optional[CameraMetadata] = None):
        self.name = name
        self.backend = None
        self.resolution = None
        self.gstreamer_pipeline = None
        self.client: None | str = None
        self.host: None | str = None
        self.username: None | str = None
        self.password: None | str = None
        self.metadata: Optional[CameraMetadata] = metadata

    def setBackend(self, backend: str) -> None:
        """Select a camera backend by name. Raises ``ValueError`` for unknown names."""
        from image_processing.camera.backends import listBackends
        instance = self.getBackend(backend)
        if instance is None:
            error_msg = (
                f"{backend} is not a valid backend. Backend must be one of {listBackends()}"
            )
            self.backend = None
            LOGGER.error(error_msg)
            raise ValueError(error_msg)
        self.backend = instance

    def getBackend(self, backend: str):
        """Return the backend instance registered under ``backend``, or None."""
        from image_processing.camera.backends import getBackend
        return getBackend(backend)

    def setConnection(self, client: str, host: str, username: str, password: str) -> None:
        """Store connection parameters and forward them to the backend if set."""
        self.client, self.host, self.username, self.password = client, host, username, password
        if self.backend:
            self.backend.setConnection(client, host, username, password)

    def connect(self) -> None:
        """Connect the backend using the stored connection parameters."""
        if self.backend and self.host and self.username and self.password:
            self.backend.setConnection(self.client, self.host, self.username, self.password)
            self.backend.connect()

    def initialize(self) -> None:
        """Initialize the backend if one is configured."""
        if self.backend:
            self.backend.initialize()

    @abstractmethod
    def captureFrame(self):
        """Capture and return a single frame from the camera."""
        ...


def constructGstreamerPipeline(pipeline: tuple) -> str:
    """Join pipeline elements into a GStreamer launch string separated by ``!``."""
    return " ! ".join(pipeline)
