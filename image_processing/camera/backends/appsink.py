"""Native GStreamer appsink capture with per-frame timestamps.

``cv2.VideoCapture`` discards buffer timestamps, which makes it impossible to
pair frames from two live cameras (e.g., EO and IR) by capture time. This
module pulls samples straight from an ``appsink`` via PyGObject instead, so
each frame carries its pipeline PTS and a monotonic clock time comparable
across pipelines on the same machine.

Requires PyGObject and the GStreamer GI bindings (``python3-gi`` +
``gir1.2-gstreamer-1.0`` on Debian-family systems). ``GST_PYTHON_AVAILABLE``
reports whether they are importable; when they are not, callers fall back to
``BufferlessVideoCapture``.
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

LOGGER = logging.getLogger(__name__)

try:
    import gi
    gi.require_version("Gst", "1.0")
    gi.require_version("GstApp", "1.0")
    from gi.repository import Gst, GstApp  # noqa: F401 - GstApp registers appsink API
    if not Gst.is_initialized():
        Gst.init(None)
    GST_PYTHON_AVAILABLE = True
except (ImportError, ValueError):
    Gst = None
    GST_PYTHON_AVAILABLE = False


@dataclass
class TimestampedFrame:
    """A decoded frame plus when it was captured.

    Attributes
    ----------
    frame : np.ndarray
        BGR image.
    clock_time : float
        Monotonic-clock time of the frame in seconds. Comparable across
        capture objects on the same machine, which is what synchronized
        EO/IR pairing needs.
    pts : float, optional
        The buffer's pipeline PTS in seconds, when known (native appsink
        capture only).
    """

    frame: np.ndarray
    clock_time: float
    pts: Optional[float] = None


class GstAppSinkCapture:
    """
    Pull BGR frames with timestamps from a GStreamer pipeline's appsink.

    The pipeline string must end in an ``appsink`` named ``sink`` negotiating
    ``video/x-raw,format=BGR`` (as produced by ``pipelines.rxPipeline``).
    ``max-buffers=1 drop=true`` on the sink keeps only the newest frame, so
    reads never return stale video.

    Parameters
    ----------
    pipeline_str : str
        ``gst-launch``-style pipeline description.

    Raises
    ------
    RuntimeError
        If GStreamer python bindings are unavailable or the pipeline fails
        to reach the PLAYING state.
    """

    def __init__(self, pipeline_str: str):
        if not GST_PYTHON_AVAILABLE:
            raise RuntimeError(
                "GStreamer python bindings (PyGObject) are not available; "
                "use BufferlessVideoCapture instead"
            )
        self.pipeline = Gst.parse_launch(pipeline_str)
        self.appsink = self.pipeline.get_by_name("sink")
        if self.appsink is None:
            raise RuntimeError("Pipeline has no appsink named 'sink'")

        self._opened = False
        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            self.pipeline.set_state(Gst.State.NULL)
            raise RuntimeError("Failed to start GStreamer pipeline")
        self._opened = True

    def read_timestamped(self, timeout: float | None = 1.0) -> TimestampedFrame:
        """
        Pull the newest frame with its timestamps.

        Raises ``TimeoutError`` if no frame arrives within ``timeout``
        seconds and ``RuntimeError`` when the stream has ended.
        """
        timeout_ns = Gst.CLOCK_TIME_NONE if timeout is None else int(timeout * Gst.SECOND)
        sample = self.appsink.try_pull_sample(timeout_ns)
        if sample is None:
            if self.appsink.get_property("eos"):
                raise RuntimeError("Video stream ended")
            raise TimeoutError("Timed out waiting for frame")

        buffer = sample.get_buffer()
        caps = sample.get_caps().get_structure(0)
        width = caps.get_value("width")
        height = caps.get_value("height")

        ok, map_info = buffer.map(Gst.MapFlags.READ)
        if not ok:
            raise RuntimeError("Failed to map GStreamer buffer")
        try:
            data = np.frombuffer(map_info.data, dtype=np.uint8)
            expected = height * width * 3
            if data.size == expected:
                frame = data.reshape((height, width, 3)).copy()
            else:
                # Rows are padded to an alignment boundary; slice the stride off.
                stride = data.size // height
                if stride * height != data.size or stride < width * 3:
                    raise RuntimeError(
                        f"Unexpected buffer size {data.size} for {width}x{height} BGR frame"
                    )
                frame = data.reshape((height, stride))[:, : width * 3].reshape((height, width, 3)).copy()
        finally:
            buffer.unmap(map_info)

        # PTS of a live source is pipeline running time at capture, so
        # base_time + PTS is on the shared monotonic system clock and is
        # comparable across pipelines.
        if buffer.pts != Gst.CLOCK_TIME_NONE:
            pts = buffer.pts / Gst.SECOND
            clock_time = (self.pipeline.get_base_time() + buffer.pts) / Gst.SECOND
        else:
            pts = None
            clock_time = time.monotonic()

        return TimestampedFrame(frame=frame, clock_time=clock_time, pts=pts)

    def read(self, timeout: float | None = 1.0) -> np.ndarray:
        """Pull the newest frame. Same errors as ``read_timestamped``."""
        return self.read_timestamped(timeout).frame

    def isOpened(self) -> bool:
        """Return True while the pipeline is running."""
        return self._opened

    def release(self) -> None:
        """Stop the pipeline and free its resources."""
        if self._opened:
            self._opened = False
            self.pipeline.set_state(Gst.State.NULL)
