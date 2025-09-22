from typing import Optional
from abc import ABC, abstractmethod
import logging
LOGGER = logging.getLogger(__name__)

class CameraBackend(ABC):
    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def setConnection(self, remote_addr: str, username: str, password: str) -> None:
        ...

    @abstractmethod
    def connect(self) -> None:
        ...

class Camera(ABC):
    def __init__(self, name: str, backend: str):
        self.name = name
        self.backend : Optional[CameraBackend] = self.getBackend(backend)
        self.resolution = None
        self.gstreamer_pipeline = None
        self.src_addr : None | str = None
        self.remote_addr : None | str = None
        self.username : None | str = None
        self.password : None | str = None

    def setBackend(self, backend):
        backends = ["rb5"]
        if backend not in backends:
            error_msg = f"{backend} is not a valid backend. Backend must be {backends}"
            self.backend = None
            LOGGER.error(error_msg)
            raise ValueError(error_msg)
        else:
            self.backend = self.getBackend(backend)

    def getBackend(self, backend):
        from image_processing.camera.backends import getBackend
        self.backend = getBackend(backend)

        
    
    def setConnection(self, src_addr, remote_addr, username, password):
        self.src_addr, self.remote_addr, self.username, self.password = src_addr, remote_addr, username, password
        if self.backend:
            self.backend.setConnection(remote_addr, username, password)

    def connect(self):
        if self.backend and self.remote_addr and self.username and self.password:
            self.backend.setConnection(self.remote_addr, self.username, self.password)  

    
    def initialize(self):
        if (self.backend):
            self.backend.initialize()
    
    def capture_frame(self):
        return 0

