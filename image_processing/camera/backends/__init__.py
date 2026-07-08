"""Camera backend implementations and backend registry."""

from image_processing.camera import CameraBackend

from .appsink import GST_PYTHON_AVAILABLE, GstAppSinkCapture, TimestampedFrame
from .gstreamer import BufferlessVideoCapture, GStreamerCamera, GStreamerManager
from .pipelines import detectH264DecoderChain, h264EncoderChain, rxPipeline, txTransportChain
from .remote import RemoteCamera
from .rtsp import RTSPCameraServer

__all__ = [
    "BufferlessVideoCapture",
    "GST_PYTHON_AVAILABLE",
    "GstAppSinkCapture",
    "GStreamerCamera",
    "GStreamerManager",
    "RTSPCameraServer",
    "RemoteCamera",
    "TimestampedFrame",
    "detectH264DecoderChain",
    "getBackend",
    "h264EncoderChain",
    "listBackends",
    "rxPipeline",
    "txTransportChain",
]

# Registry of instantiable-by-name backends. Keep this as the single source
# of truth for valid backend names; ``Camera.setBackend`` validates against it.
_BACKENDS = {
    "rb5": RemoteCamera,
}


def getBackend(backend: str) -> CameraBackend | None:
    """Return a new backend instance registered under ``backend``, or None."""
    backend_cls = _BACKENDS.get(backend)
    return backend_cls() if backend_cls else None


def listBackends() -> list[str]:
    """Return the names of all registered backends."""
    return list(_BACKENDS)
