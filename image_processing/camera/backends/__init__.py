from .remote import RemoteCamera
from .gstreamer import *
from image_processing.camera import CameraBackend

from typing import Type

def getBackend(backend: str) -> CameraBackend | None:
    backends = {
        'rb5': RemoteCamera()
    }
    return backends.get(backend, None)