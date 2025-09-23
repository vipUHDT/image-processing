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
    def setConnection(self, client: str, host: str, username: str, password: str) -> None:
        ...

    @abstractmethod
    def connect(self) -> None:
        ...

class Camera(ABC):
    def __init__(self, name: str):
        self.name = name
        self.backend = None
        self.resolution = None
        self.gstreamer_pipeline = None
        self.client : None | str = None
        self.host : None | str = None
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

        
    
    def setConnection(self, client, host , username, password):
        self.client, self.host, self.username, self.password = client, host, username, password
        if self.backend:
            self.backend.setConnection(client, host, username, password)

    def connect(self):
        if self.backend and self.remote_addr and self.username and self.password:
            self.backend.setConnection(self.remote_addr, self.username, self.password)  

    
    def initialize(self):
        if (self.backend):
            self.backend.initialize()
   
    @abstractmethod
    def captureFrame(self):
        ...

def constructGstreamerPipeline(pipeline: tuple) -> str:
    return ' ! '.join(pipeline)