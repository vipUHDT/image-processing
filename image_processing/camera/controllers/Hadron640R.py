"""Controller for the Teledyne FLIR Hadron 640R dual EO/IR camera on a remote host.

Streams both cameras from the remote device (Qualcomm RB5) to the ground
station. Supports:

- hardware (``qtic2venc``) or software (``x264enc``) H.264 encoding on the
  device (``encoder=``),
- RTP/UDP, SRT, or RTSP transport (``transport=``),
- timestamp-paired EO/IR capture (``captureSynchronized``) for fusion.

The RTP/UDP + software-encoder combination reproduces the original
behavior; the hardware encoder and SRT/RTSP paths have not been exercised
against RB5 hardware yet — validate on the bench before a flight.
"""

import logging
from string import Template
from time import sleep

from image_processing.camera import Camera
from image_processing.camera.backends import GStreamerCamera, GStreamerManager, RemoteCamera
from image_processing.camera.backends.appsink import TimestampedFrame
from image_processing.camera.backends.pipelines import (
    h264EncoderChain,
    rxPipeline,
    txTransportChain,
)
from image_processing.camera.backends.rtsp import RTSPCameraServer
from image_processing.connection.ssh import SSH_Controller
from image_processing.tools import timestamp

LOGGER = logging.getLogger(__name__)

RTSP_PORT = 8554


def _buildTXPipeline(source_chain: str, encoder_chain: str, transport: str, record_path: str) -> str:
    """
    Build the device-side launch command: source -> encode -> tee to the
    network transport and an on-device MP4 recording. ``$client``/``$port``
    remain as placeholders. ``-e`` makes SIGINT finalize the MP4.
    """
    tx = txTransportChain(transport)
    return (
        f"gst-launch-1.0 -e {source_chain} ! {encoder_chain} ! h264parse ! "
        "tee name=t "
        "t. ! queue max-size-buffers=0 max-size-time=50000000 max-size-bytes=0 leaky=downstream ! "
        f"{tx} "
        "t. ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! "
        "h264parse ! video/x-h264,stream-format=avc,alignment=au ! "
        f"mp4mux faststart=true ! filesink location={record_path} sync=false async=false"
    )


class Hadron640R:
    """
    Orchestrates the Hadron 640R's EO (OV64B) and IR (BOSON640) cameras.

    Call ``setConnection`` before ``initialize``. ``capture`` returns the
    latest frame from each camera; ``captureSynchronized`` pairs frames by
    capture timestamp, which is what EO/IR fusion should consume.

    Parameters
    ----------
    encoder : str, optional
        ``"hardware"`` (RB5 ``qtic2venc``, default) or ``"software"``
        (``x264enc``). Fall back to software if the device image lacks the
        hardware element.
    transport : str, optional
        ``"udp"`` (RTP over UDP, default — original behavior), ``"srt"``
        (loss recovery with a bounded latency budget), or ``"rtsp"``
        (single managed server process on the device; no on-device MP4
        recording in this mode).
    """

    def __init__(self, encoder: str = "hardware", transport: str = "udp"):
        self.backendManager = GStreamerManager()
        self.ports = {"BOSON640": 5000, "OV64B": 6000}
        self.processes = []
        self.encoder = encoder
        self.transport = transport
        self.rtsp_server: RTSPCameraServer | None = None
        self.client = None
        self.host = None
        self.username = None
        self.password = None

    def getProcessIds(self):
        """Return the GStreamer process IDs currently running on the remote device."""
        process_ids = []
        if all((self.client, self.host, self.username, self.password)):
            hadron = RemoteCamera(self.client, self.host, self.username, self.password)
            hadron.connect()
            raw_process_ids = hadron.getProcessID("gst")
            process_ids = [
                process_id.replace("\n", "").replace("\r", "")
                for process_id in raw_process_ids
            ]
        return process_ids

    def setConnection(self, client, host, username, password):
        """Store the stream destination (``client``) and remote SSH connection details."""
        self.client = client
        self.host = host
        self.username = username
        self.password = password

    def _killStalePipelines(self):
        """Terminate leftover GStreamer/RTSP processes from previous runs."""
        ssh = SSH_Controller(self.host, self.username, self.password)
        ssh.connect()
        ssh.run_cmd("pkill gst")
        ssh.run_cmd("pkill -f uhdt_rtsp_server")
        ssh.disconnect()

    def initialize(self):
        """Kill stale remote pipelines, then start and open both camera streams."""
        eo = OV64B(encoder=self.encoder, transport=self.transport)
        ir = Boson640(encoder=self.encoder, transport=self.transport)
        self.backendManager.addCamera(eo)
        self.backendManager.addCamera(ir)
        cameras = [eo, ir]

        self._killStalePipelines()

        for cam in cameras:
            cam.setConnection(self.client, self.host, self.username, self.password)

        if self.transport == "rtsp":
            self._initializeRTSP(eo, ir)
        else:
            self._initializeStreamed(cameras)

        # SRT/RTSP receivers connect to the device at open, which can fail if
        # the device side is still coming up — retry the open a few times.
        for cam in cameras:
            for attempt in range(3):
                try:
                    cam.startRXPipeline()
                    break
                except RuntimeError:
                    if attempt == 2:
                        raise
                    LOGGER.warning("%s RX open failed; retrying", cam.name)
                    sleep(2)
        for cam in cameras:
            if not cam.backend.waitForFirstFrame(timeout=20.0):
                LOGGER.error("%s produced no frames during startup", cam.name)

    def _initializeStreamed(self, cameras):
        """UDP/SRT path: launch one TX pipeline per camera over SSH."""
        for cam in cameras:
            cam.setPort(self.ports[cam.name])
            cam.setTXPipeline()
            cam.setRXPipeline()
            cam.initialize()
        # Start streams one at a time so each new PID is identifiable.
        for cam in cameras:
            cam.initializeStream(self.getProcessIds())

    def _initializeRTSP(self, eo: "OV64B", ir: "Boson640"):
        """RTSP path: one managed server process serves both cameras."""
        self.rtsp_server = RTSPCameraServer(
            self.host, self.username, self.password, port=RTSP_PORT
        )
        self.rtsp_server.addStream("eo", eo.rtspLaunchChain())
        self.rtsp_server.addStream("ir", ir.rtspLaunchChain())
        self.rtsp_server.deploy()
        self.rtsp_server.start()
        for cam in (eo, ir):
            cam.setPort(RTSP_PORT)
            cam.setRXPipeline()

    def capture(self):
        """Capture one frame from each camera; returns ``(rgb_img, infrared_img)``."""
        rgb_img = self.backendManager.cameras["OV64B"].backend.captureFrame()
        infrared_img = self.backendManager.cameras["BOSON640"].backend.captureFrame()
        return rgb_img, infrared_img

    def captureSynchronized(
        self,
        tolerance_s: float = 0.034,
        max_attempts: int = 10,
        timeout: float = 1.0,
    ) -> tuple[TimestampedFrame | None, TimestampedFrame | None, float | None]:
        """
        Capture an EO/IR frame pair aligned by capture timestamp.

        Reads a frame from each camera, then keeps re-reading from whichever
        stream is older until the pair's timestamps agree within
        ``tolerance_s`` or ``max_attempts`` is exhausted. This removes the
        skew of sequential ``capture()`` calls, which matters for fusion of
        moving scenes.

        Parameters
        ----------
        tolerance_s : float, optional
            Maximum allowed timestamp skew in seconds (default ~one frame
            period at 30 fps).
        max_attempts : int, optional
            Maximum re-reads before returning the closest pair found.
        timeout : float, optional
            Per-read timeout in seconds.

        Returns
        -------
        tuple
            ``(eo_frame, ir_frame, skew_s)`` as ``TimestampedFrame`` objects
            plus the residual EO-minus-IR skew in seconds, or
            ``(None, None, None)`` when either stream produced no frame.
        """
        eo_cam = self.backendManager.cameras["OV64B"].backend
        ir_cam = self.backendManager.cameras["BOSON640"].backend

        eo = eo_cam.captureFrameTimestamped(timeout=timeout)
        ir = ir_cam.captureFrameTimestamped(timeout=timeout)
        if eo is None or ir is None:
            return None, None, None

        for _ in range(max_attempts):
            skew = eo.clock_time - ir.clock_time
            if abs(skew) <= tolerance_s:
                break
            if skew < 0:  # EO frame is older; pull a newer one.
                newer = eo_cam.captureFrameTimestamped(timeout=timeout)
                if newer is None:
                    break
                eo = newer
            else:
                newer = ir_cam.captureFrameTimestamped(timeout=timeout)
                if newer is None:
                    break
                ir = newer

        return eo, ir, eo.clock_time - ir.clock_time

    def terminate(self):
        """Close the local streams and stop the remote pipelines/server."""
        for name in ("OV64B", "BOSON640"):
            self.backendManager.cameras[name].closeRXPipeline()
            self.backendManager.cameras[name].terminate()
        if self.rtsp_server:
            self.rtsp_server.stop()
            self.rtsp_server = None

    def downloadRemoteVideos(self, eo_save_path, ir_save_path):
        """Download both cameras' recorded videos (UDP/SRT transports only)."""
        if self.transport == "rtsp":
            LOGGER.warning("RTSP transport does not record on-device videos")
            return
        self.backendManager.cameras["OV64B"].downloadRemoteVideo(eo_save_path)
        self.backendManager.cameras["BOSON640"].downloadRemoteVideo(ir_save_path)


class Boson640(Camera):
    """FLIR Boson 640 IR camera streamed from the remote host."""

    SOURCE_CHAIN = (
        "v4l2src device=/dev/v4l/by-id/usb-FLIR_Boson_439955-video-index0 io-mode=2 ! "
        "video/x-raw,format=NV12,width=640,height=512,framerate=30/1"
    )
    RTSP_MOUNT = "ir"

    def __init__(self, encoder: str = "hardware", transport: str = "udp"):
        super().__init__("BOSON640")
        self.backend = GStreamerCamera(self.name)
        self.remote_video_path = f"flights/{timestamp()}-IR.mp4"
        self.encoder_chain = h264EncoderChain(encoder, bitrate_kbps=2500, key_int_frames=60)
        self.transport = transport
        self.RX_TEMPLATE = Template(rxPipeline(transport, rtsp_mount=self.RTSP_MOUNT))
        self.TX_TEMPLATE = Template(
            _buildTXPipeline(self.SOURCE_CHAIN, self.encoder_chain, transport, self.remote_video_path)
        ) if transport != "rtsp" else None

    def rtspLaunchChain(self) -> str:
        """Return this camera's launch chain for an ``RTSPCameraServer`` mount."""
        return f"{self.SOURCE_CHAIN} ! {self.encoder_chain} ! h264parse ! rtph264pay name=pay0 pt=96"

    def setPort(self, port):
        self.backend.setPort(port)

    def setTXPipeline(self, pipeline: Template | str | None = None):
        self.backend.setTXPipeline(pipeline or self.TX_TEMPLATE)

    def setRXPipeline(self, pipeline: Template | str | None = None):
        self.backend.setRXPipeline(pipeline or self.RX_TEMPLATE)

    def startRXPipeline(self):
        self.backend.startRXPipeline()

    def captureFrame(self):
        return self.backend.captureFrame()

    def closeRXPipeline(self):
        self.backend.closeRXPipeline()

    def initialize(self):
        self.backend.initialize()

    def initializeStream(self, pids):
        self.backend.initializeStream(pids)

    def terminate(self):
        self.backend.terminate()

    def downloadRemoteVideo(self, save_path: str):
        self.backend.downloadRemoteVideo(self.remote_video_path, save_path)


class OV64B(Camera):
    """OmniVision OV64B EO camera streamed from the remote host."""

    SOURCE_CHAIN = (
        "qtiqmmfsrc name=qmmf camera=0 scene=action af-mode=continuous "
        "white-balance-mode=auto iso-mode=deblur noise-reduction=fast sharpness=1 ! "
        "video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1 ! queue"
    )
    RTSP_MOUNT = "eo"

    def __init__(self, encoder: str = "hardware", transport: str = "udp"):
        super().__init__("OV64B")
        self.backend = GStreamerCamera(self.name)
        self.remote_video_path = f"flights/{timestamp()}-EO.mp4"
        self.encoder_chain = h264EncoderChain(encoder, bitrate_kbps=6000, key_int_frames=30)
        self.transport = transport
        self.RX_TEMPLATE = Template(rxPipeline(transport, rtsp_mount=self.RTSP_MOUNT))
        self.TX_TEMPLATE = Template(
            _buildTXPipeline(self.SOURCE_CHAIN, self.encoder_chain, transport, self.remote_video_path)
        ) if transport != "rtsp" else None

    def rtspLaunchChain(self) -> str:
        """Return this camera's launch chain for an ``RTSPCameraServer`` mount."""
        return f"{self.SOURCE_CHAIN} ! {self.encoder_chain} ! h264parse ! rtph264pay name=pay0 pt=96"

    def setPort(self, port):
        self.backend.setPort(port)

    def setTXPipeline(self, pipeline: Template | str | None = None):
        self.backend.setTXPipeline(pipeline or self.TX_TEMPLATE)

    def setRXPipeline(self, pipeline: Template | str | None = None):
        self.backend.setRXPipeline(pipeline or self.RX_TEMPLATE)

    def startRXPipeline(self):
        self.backend.startRXPipeline()

    def captureFrame(self):
        return self.backend.captureFrame()

    def closeRXPipeline(self):
        self.backend.closeRXPipeline()

    def initialize(self):
        self.backend.initialize()

    def initializeStream(self, pids):
        self.backend.initializeStream(pids)

    def terminate(self):
        self.backend.terminate()

    def downloadRemoteVideo(self, save_path: str):
        self.backend.downloadRemoteVideo(self.remote_video_path, save_path)
