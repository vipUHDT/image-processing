"""GStreamer-based video streaming from remote cameras."""

import logging
import queue
import threading
import time
from string import Template
from typing import TypeAlias

import cv2

from image_processing.camera import Camera
from image_processing.camera.backends.appsink import (
    GST_PYTHON_AVAILABLE,
    GstAppSinkCapture,
    TimestampedFrame,
)
from image_processing.camera.backends.remote import RemoteCamera
from image_processing.connection import SFTPController

LOGGER = logging.getLogger(__name__)

# (client, host, username, password)
GStreamerRemoteConnection: TypeAlias = tuple[str, str, str, str]


class GStreamerCamera:
    """
    Receive video from a remote camera over a GStreamer RTP stream.

    The camera device runs a TX pipeline on the remote host (started over
    SSH) while this class opens the matching RX pipeline locally through
    OpenCV's GStreamer capture backend.

    Parameters
    ----------
    name : str
        Human-readable camera identifier.
    remote_connection : tuple, optional
        ``(client, host, username, password)`` used to lazily construct the
        SSH and SFTP controllers in ``initialize``.
    prefer_native_appsink : bool, optional
        Use ``GstAppSinkCapture`` (per-frame PTS timestamps) when PyGObject
        is available, otherwise fall back to ``BufferlessVideoCapture``
        through OpenCV. Default True.
    """

    def __init__(self, name: str,
                 remote_connection: GStreamerRemoteConnection | None = None,
                 prefer_native_appsink: bool = True):
        self.name = name
        self.tx_pipeline = None
        self.rx_pipeline = None
        self.pid = None
        self.remote_connection: GStreamerRemoteConnection | None = remote_connection
        self.remote: RemoteCamera | None = None
        self.connected = False
        self.capture: BufferlessVideoCapture | GstAppSinkCapture | None = None
        self.port = None
        self.sftp = None
        self.prefer_native_appsink = prefer_native_appsink

    def setConnection(self, client, host, username, password):
        """Create the SSH and SFTP controllers for the remote device."""
        self.remote = RemoteCamera(client, host, username, password)
        self.sftp = SFTPController(host, username, password)

    def setPort(self, port):
        """Set the UDP port used by the RTP stream."""
        self.port = port

    def connect(self):
        """Open the SSH and SFTP connections to the remote device."""
        if self.remote:
            self.remote.connect()
        if self.sftp:
            self.sftp.connect()

    def initialize(self):
        """
        Connect to the remote device, constructing the controllers from
        ``remote_connection`` if ``setConnection`` was not called first.

        Returns
        -------
        str or None
            ``"Invalid connection"`` if no connection information is
            available, otherwise None.
        """
        if not self.remote and self.remote_connection:
            client, host, username, password = self.remote_connection
            self.setConnection(client, host, username, password)

        if not self.remote:
            return "Invalid connection"

        self.connect()
        self.connected = True
        return None

    def _substitute(self, pipeline: Template | str) -> str:
        """Fill ``$client``/``$host``/``$port`` placeholders from the connection."""
        if not isinstance(pipeline, Template):
            return pipeline
        return pipeline.safe_substitute(
            client=self.remote.client if self.remote else "",
            host=self.remote.host if self.remote else "",
            port=self.port,
        )

    def setTXPipeline(self, pipeline: Template | str):
        """Set the remote (transmit) pipeline, substituting placeholders in templates."""
        if self.remote:
            self.tx_pipeline = self._substitute(pipeline)

    def setRXPipeline(self, pipeline):
        """Set the local (receive) pipeline, substituting placeholders in templates."""
        if self.remote:
            self.rx_pipeline = self._substitute(pipeline)
        else:
            self.rx_pipeline = pipeline

    def startRXPipeline(self):
        """
        Open the local capture on the RX pipeline.

        Uses the native appsink capture (per-frame timestamps) when PyGObject
        is available and ``prefer_native_appsink`` is set; otherwise falls
        back to OpenCV's GStreamer backend. Raises ``RuntimeError`` if the
        stream cannot be opened.
        """
        if not self.rx_pipeline:
            raise RuntimeError("RX pipeline not set")

        LOGGER.debug("[%s] RX pipeline: %s", self.name, self.rx_pipeline)

        if self.prefer_native_appsink and GST_PYTHON_AVAILABLE:
            self.capture = GstAppSinkCapture(self.rx_pipeline)
        else:
            self.capture = BufferlessVideoCapture(
                self.rx_pipeline,
                api_preference=cv2.CAP_GSTREAMER
            )

        if not self.capture.isOpened():
            self.capture = None
            raise RuntimeError("Failed to open video stream")

    def waitForFirstFrame(self, timeout: float = 15.0, poll_interval: float = 0.5) -> bool:
        """
        Block until the stream delivers a frame, up to ``timeout`` seconds.

        Replaces fixed startup sleeps: returns True as soon as a frame
        arrives, False on timeout.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.captureFrame(timeout=poll_interval) is not None:
                return True
        LOGGER.warning("[%s] No frame within %.1fs of starting stream", self.name, timeout)
        return False

    def closeRXPipeline(self):
        """Release the local capture if open."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def captureFrame(self, timeout: float | None = 1.0):
        """Return the most recent frame, or None on timeout or end of stream."""
        result = self.captureFrameTimestamped(timeout=timeout)
        return result.frame if result else None

    def captureFrameTimestamped(self, timeout: float | None = 1.0) -> TimestampedFrame | None:
        """
        Return the most recent frame with its capture timestamps, or None.

        With the native appsink capture, ``clock_time`` is derived from the
        buffer PTS on the shared monotonic clock; with the OpenCV fallback it
        is the frame's arrival time at the reader thread. Either way it is
        comparable across cameras on this machine, which is what
        ``Hadron640R.captureSynchronized`` pairs on.
        """
        if self.capture is None:
            raise RuntimeError("RX pipeline not started")

        try:
            return self.capture.read_timestamped(timeout=timeout)
        except (queue.Empty, TimeoutError):
            LOGGER.warning("[%s] Timeout waiting for frame", self.name)
            return None
        except RuntimeError:
            LOGGER.error("[%s] Video stream ended", self.name)
            return None


    def initializeStream(self, process_ids, pipeline=None):
        """
        Start the TX pipeline on the remote device and record its process ID.

        Parameters
        ----------
        process_ids : list[str]
            GStreamer process IDs that existed before this stream was
            started, so the new process can be identified.
        pipeline : str, optional
            Pipeline to launch; defaults to the pipeline set with
            ``setTXPipeline``.
        """
        pipeline = pipeline or self.tx_pipeline
        if self.remote and pipeline:
            LOGGER.debug("[%s] TX pipeline: %s", self.name, pipeline)
            self.remote.initializeStream(pipeline)
            # Poll for the new process instead of assuming it is up instantly.
            deadline = time.monotonic() + 5.0
            self.pid = None
            while self.pid is None and time.monotonic() < deadline:
                self.pid = self.getGstreamerProcessID(process_ids)
                if self.pid is None:
                    time.sleep(0.25)
            if self.pid is None:
                LOGGER.error(
                    "[%s] TX pipeline did not start on the remote device. If using "
                    "the hardware encoder, verify it exists there "
                    "(gst-inspect-1.0 qtic2venc) or fall back to encoder='software'.",
                    self.name,
                )

    def getGstreamerProcessID(self, process_ids: list[str]):
        """Return the remote GStreamer PID not present in ``process_ids``, or None."""
        if self.remote:
            cmd_output = self.remote.getProcessID("gst")
            if len(cmd_output) > 0:
                for output in cmd_output:
                    if output.replace("\n", "").replace("\r", "") in process_ids:
                        continue
                    return output.replace("\n", "").replace("\r", "")
            else:
                return None

    def terminate(self):
        """Stop the remote TX pipeline and clean up its log files."""
        if self.pid and self.remote:
            self.remote.terminateProcessID(self.pid)
            self.remote.cleanLogFiles()
            self.pid = None
            self.connected = False
            
    def downloadRemoteVideo(self, remote_video_path: str, local_video_path):
        """Download a recorded video from the remote device over SFTP."""
        if isinstance(self.sftp, SFTPController):
            self.sftp.downloadFile(remote_video_path, local_video_path)
        else:
            LOGGER.warning("No SFTP controller present for %s", self.name)


class GStreamerManager:
    """Registry of cameras keyed by label or camera name."""

    def __init__(self):
        self.cameras: dict[str, Camera] = {}

    def addCamera(self, camera: Camera, label: str | None = None) -> None:
        """Register a camera under ``label``, or its own name when no label is given."""
        self.cameras[label or camera.name] = camera


class BufferlessVideoCapture:
    """
    ``cv2.VideoCapture`` wrapper that always returns the latest frame.

    A background thread continuously drains the capture into a one-slot
    queue so readers never receive stale buffered frames — important for
    live RTP streams.
    """

    def __init__(self, src, api_preference=cv2.CAP_ANY):
        self.cap = cv2.VideoCapture(src, api_preference)
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open video source")

        self.q: queue.Queue = queue.Queue(maxsize=1)
        self._stopped = False

        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()

    def _reader(self):
        consecutive_failures = 0
        max_failures = 10

        while not self._stopped:
            ret, frame = self.cap.read()
            if not ret:
                consecutive_failures += 1
                LOGGER.warning("VideoCapture read() failed (%d/%d)",
                               consecutive_failures, max_failures)
                if consecutive_failures >= max_failures:
                    break
                time.sleep(0.01)
                continue

            consecutive_failures = 0

            item = TimestampedFrame(frame=frame, clock_time=time.monotonic())
            try:
                if self.q.full():
                    self.q.get_nowait()
                self.q.put_nowait(item)
            except queue.Full:
                pass

        self._stopped = True
        try:
            if not self.q.full():
                self.q.put_nowait(None)
        except queue.Full:
            pass

    def read_timestamped(self, timeout=None) -> TimestampedFrame:
        """
        Return the newest frame with its arrival time (``clock_time``;
        ``pts`` is None for this backend), or raise:
          - queue.Empty if timeout is reached
          - RuntimeError if the stream has ended (EOS)
        """
        item = self.q.get(timeout=timeout)
        if item is None:
            raise RuntimeError("Video stream ended")
        return item

    def read(self, timeout=None):
        """
        Returns a frame (numpy array), or raises:
          - queue.Empty if timeout is reached
          - RuntimeError if the stream has ended (EOS)
        """
        return self.read_timestamped(timeout=timeout).frame

    def isOpened(self):
        return self.cap.isOpened()

    def release(self):
        # Stop and join the reader before releasing: cv2.VideoCapture is not
        # thread-safe, and releasing while the reader is inside cap.read()
        # can crash the process.
        self._stopped = True
        if self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self.cap.isOpened():
            self.cap.release()

        # Leave only the EOS sentinel behind so a read() after release()
        # raises RuntimeError instead of blocking.
        with self.q.mutex:
            self.q.queue.clear()
        try:
            self.q.put_nowait(None)
        except queue.Full:
            pass


