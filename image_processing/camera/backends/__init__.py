"""
Backend factory and public exports for camera backend implementations.

This module exposes the available backend classes (e.g., remote and
GStreamer-based backends) and provides :func:`getBackend`, a simple factory
function for retrieving backend instances by name. Backends defined here are
used by higher-level camera controllers to abstract away connection and
transport details.
"""

from .remote import RemoteCamera
from .gstreamer import *
from image_processing.camera import CameraBackend

from typing import Type

def getBackend(backend: str) -> CameraBackend | None:
    """Return an initialized backend instance by backend name.

    Parameters
    ----------
    backend : str
        Name of the backend to create. Currently supported:
        - ``"rb5"`` → :class:`RemoteCamera`

    Returns
    -------
    CameraBackend or None
        A backend instance if the name is recognized, otherwise ``None``.

    Notes
    -----
    Backends are instantiated immediately, not lazily. If authentication or
    connection details are required, they must be provided via the backend's
    own configuration methods.
    """
    backends = {
        'rb5': RemoteCamera()
    }
    return backends.get(backend, None)