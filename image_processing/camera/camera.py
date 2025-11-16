"""
Core camera abstractions.

This module defines the abstract Camera interface, the CameraBackend
contract for backend providers, and the CameraMetadata container for
storing intrinsic camera parameters. These classes are intended to be
extended or used by hardware-specific camera implementations.
"""

from typing import Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
LOGGER = logging.getLogger(__name__)

class CameraBackend(ABC):
    """
    Abstract base class for camera backends.

    Concrete implementations wrap specific camera hardware or
    streaming sources (e.g., RB5, remote cameras) and provide a
    unified interface for initialization and connection handling.
    """

    @abstractmethod
    def __init__(self):
        """Initialize the backend-specific resources.

        Implementations may set up local state, allocate handles,
        or perform any configuration that does not require a remote
        connection.
        """
        ...

    @abstractmethod
    def initialize(self) -> None:
        """Perform backend initialization before capturing frames.

        This method is intended for tasks such as opening device
        handles, starting pipelines, or validating configuration
        prior to streaming.
        """
        ...

    @abstractmethod
    def setConnection(self, client: str, host: str, username: str, password: str) -> None:
        """Configure connection parameters for the backend.

        Parameters
        ----------
        client : str
            Identifier or role of the current client (e.g., local host name
            or logical client type).
        host : str
            Hostname or IP address of the remote device or service.
        username : str
            Username used for authentication with the remote endpoint.
        password : str
            Password or token used for authentication with the remote endpoint.
        """
        ...

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection using the configured parameters.

        Implementations should use the connection parameters provided via
        :meth:`setConnection` to open network sessions, SSH tunnels, or any
        other transport needed for frame acquisition.
        """
        ...

@dataclass
class CameraMetadata:
    """
    Structured container for intrinsic camera properties.

    Parameters
    ----------
    sensor_width : float
        Physical width of the image sensor in mm.
    sensor_height : float
        Physical height of the image sensor in mm.
    image_width : int
        Horizontal resolution of captured images in pixels.
    image_height : int
        Vertical resolution of captured images in pixels.
    focal_length : int
        Focal length of the lens, expressed in millimeters or equivalent units.
    """
    sensor_width: float
    sensor_height: float
    image_width: int
    image_height: int
    focal_length: int

class Camera(ABC):
    """
    Abstract representation of a camera device.

    This class manages common properties such as the camera name,
    associated backend, connection credentials, and optional
    metadata. Concrete subclasses must implement :meth:`captureFrame`
    to define how a frame is acquired.

    Parameters
    ----------
    name : str
        Logical name or identifier for the camera instance.
    metadata : CameraMetadata, optional
        Intrinsic parameters and resolution for the camera, if known.
    """

    def __init__(self, name: str, metadata: Optional[CameraMetadata] = None):
        self.name = name
        self.backend = None
        self.resolution = None
        self.gstreamer_pipeline = None
        self.client : None | str = None
        self.host : None | str = None
        self.username : None | str = None
        self.password : None | str = None
        self.metadata: Optional[CameraMetadata] = metadata

    def setBackend(self, backend):
        """Select and configure the camera backend by name.

        The backend string is validated against a list of supported
        backend identifiers and, if valid, the corresponding backend
        instance is created.

        Parameters
        ----------
        backend : str
            Name of the backend to use (e.g., ``"rb5"``).

        Raises
        ------
        ValueError
            If the requested backend is not in the list of supported
            backends.
        """
        backends = ["rb5"]
        if backend not in backends:
            error_msg = f"{backend} is not a valid backend. Backend must be {backends}"
            self.backend = None
            LOGGER.error(error_msg)
            raise ValueError(error_msg)
        else:
            self.backend = self.getBackend(backend)

    def getBackend(self, backend):
        """Instantiate and return a backend by name.

        This helper imports the backend factory from
        ``image_processing.camera.backends`` and constructs a backend
        instance corresponding to the given identifier.

        Parameters
        ----------
        backend : str
            Name of the backend to retrieve.

        Returns
        -------
        CameraBackend
            The instantiated backend associated with the given name.
        """
        from image_processing.camera.backends import getBackend
        self.backend = getBackend(backend)

        
    
    def setConnection(self, client, host , username, password):
        """Set connection parameters and propagate them to the backend.

        Parameters
        ----------
        client : str
            Identifier or role of the current client (e.g., local host name).
        host : str
            Hostname or IP address of the remote device or service.
        username : str
            Username used for authentication with the remote endpoint.
        password : str
            Password or token used for authentication with the remote endpoint.
        """
        self.client, self.host, self.username, self.password = client, host, username, password
        if self.backend:
            self.backend.setConnection(client, host, username, password)

    def connect(self):
        """Establish a connection through the configured backend.

        This method uses the connection credentials stored on the
        camera instance to instruct the backend to establish a session
        (e.g., network connection) required for frame acquisition.
        """
        if self.backend and self.remote_addr and self.username and self.password:
            self.backend.setConnection(self.remote_addr, self.username, self.password)  

    
    def initialize(self):
        """Initialize the backend prior to frame capture.

        If a backend is configured, this method forwards the call to
        :meth:`CameraBackend.initialize` so that all required resources
        are ready before capturing frames.
        """
        if (self.backend):
            self.backend.initialize()
   
    @abstractmethod
    def captureFrame(self):
        """Capture a single frame from the camera.

        Concrete subclasses must implement this method to define how
        a frame is acquired from the underlying backend.

        Returns
        -------
        Any
            The captured frame object. The exact type depends on the
            backend and implementation (e.g., NumPy array, raw bytes).
        """
        ...

def constructGstreamerPipeline(pipeline: tuple) -> str:
    """Construct a GStreamer pipeline string from a tuple of elements.

    The elements in the input tuple are joined with the ``" ! "`` separator
    to form a valid GStreamer pipeline description.

    Parameters
    ----------
    pipeline : tuple of str
        Ordered sequence of GStreamer elements (e.g., caps, sources,
        converters, sinks).

    Returns
    -------
    str
        GStreamer pipeline string suitable for use with GStreamer-based
        APIs.
    """
    return ' ! '.join(pipeline)