from .RB5 import RB5Backend
from image_processing.camera import CameraBackend

from typing import Type

def getBackend(backend: str) -> CameraBackend | None:
    backends = {
        'rb5': RB5Backend()
    }
    return backends.get(backend, None)