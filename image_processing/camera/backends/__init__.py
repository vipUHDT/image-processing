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
    "rxPipeline",
    "txTransportChain",
]


def getBackend(backend: str) -> CameraBackend | None:
    """Return a new backend instance registered under ``backend``, or None."""
    backends = {
        "rb5": RemoteCamera(),
    }
    return backends.get(backend)
