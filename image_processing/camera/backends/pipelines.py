"""GStreamer pipeline construction: encoder/decoder selection and transports.

Builds the H.264 encode chain for the remote device (hardware ``qtic2venc``
on the RB5 or software ``x264enc``), the receive-side decode chain (detected
per machine so the same code runs on a Jetson, macOS, or generic Linux), and
the transport elements for UDP/RTP, SRT, and RTSP.

Elements are joined with `` ! `` into launch strings compatible with
``gst-launch-1.0`` and ``cv2.VideoCapture(..., CAP_GSTREAMER)``.
"""

import logging
import shutil
import subprocess
from functools import lru_cache

LOGGER = logging.getLogger(__name__)

#: Preferred H.264 decoder chains, first available wins. The Jetson decoder
#: outputs NVMM memory, so it needs nvvidconv before videoconvert.
_DECODER_CHAINS = (
    ("nvv4l2decoder", "nvv4l2decoder disable-dpb=true ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert"),
    ("vtdec", "vtdec ! videoconvert"),
    ("avdec_h264", "avdec_h264 ! videoconvert"),
    ("openh264dec", "openh264dec ! videoconvert"),
)

#: Fallback when element availability cannot be determined: decodebin
#: autoplugs whatever decoder the machine has at pipeline start.
_DECODER_FALLBACK = "decodebin ! videoconvert"


def _elementExists(element: str) -> bool:
    """Return True if a GStreamer element is available on this machine."""
    try:
        import gi
        gi.require_version("Gst", "1.0")
        from gi.repository import Gst
        if not Gst.is_initialized():
            Gst.init(None)
        return Gst.ElementFactory.find(element) is not None
    except (ImportError, ValueError):
        pass

    if shutil.which("gst-inspect-1.0"):
        result = subprocess.run(
            ["gst-inspect-1.0", "--exists", element],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    raise RuntimeError("No way to query GStreamer elements (no gi, no gst-inspect-1.0)")


@lru_cache(maxsize=1)
def detectH264DecoderChain() -> str:
    """
    Return the best H.264 decode chain available on this machine.

    Prefers the platform hardware decoder (NVDEC on Jetson, VideoToolbox on
    macOS), then software decoders. Falls back to ``decodebin`` when element
    availability cannot be queried at all.
    """
    try:
        for element, chain in _DECODER_CHAINS:
            if _elementExists(element):
                LOGGER.info("Using H.264 decoder: %s", element)
                return chain
    except RuntimeError:
        LOGGER.warning("Cannot query GStreamer elements; falling back to decodebin")
    return _DECODER_FALLBACK


def h264EncoderChain(encoder: str = "hardware", bitrate_kbps: int = 6000, key_int_frames: int = 30) -> str:
    """
    Return the H.264 encode chain for the remote (RB5) device.

    Parameters
    ----------
    encoder : str
        ``"hardware"`` for the RB5's C2 hardware encoder (``qtic2venc``) or
        ``"software"`` for ``x264enc``. Verify the hardware element exists on
        the device with ``gst-inspect-1.0 qtic2venc``; if it does not, use
        ``"software"``.
    bitrate_kbps : int
        Target bitrate in kilobits per second.
    key_int_frames : int
        Maximum keyframe interval in frames.
    """
    if encoder == "hardware":
        # qtic2venc takes bits/sec; x264enc takes kbit/sec.
        return f"qtic2venc target-bitrate={bitrate_kbps * 1000}"
    if encoder == "software":
        return (
            f"x264enc tune=zerolatency speed-preset=superfast "
            f"bitrate={bitrate_kbps} key-int-max={key_int_frames} bframes=0 byte-stream=true"
        )
    raise ValueError(f"Unknown encoder '{encoder}'. Choose 'hardware' or 'software'.")


# ---------------------------------------------------------------------------
# Transmit (device-side) transports. All templates keep gst-launch-1.0 -e so
# the recording branch finalizes its MP4 on SIGINT.
# ---------------------------------------------------------------------------

def txTransportChain(transport: str = "udp") -> str:
    """
    Return the transmit-side transport elements after ``h264parse``.

    ``$client``/``$port`` remain as template placeholders, substituted by
    ``GStreamerCamera`` when the pipeline is installed.

    Parameters
    ----------
    transport : str
        ``"udp"`` — raw RTP over UDP (lowest latency, no loss recovery).
        ``"srt"`` — SRT in listener mode (retransmission with a bounded
        latency budget; the ground station connects to the device).
    """
    if transport == "udp":
        return (
            "video/x-h264,stream-format=byte-stream,alignment=au ! "
            "rtph264pay pt=96 mtu=1200 config-interval=1 ! "
            "udpsink host=$client port=$port sync=false async=false"
        )
    if transport == "srt":
        return (
            "mpegtsmux alignment=7 ! "
            'srtsink uri="srt://0.0.0.0:$port?mode=listener" latency=125 sync=false async=false'
        )
    raise ValueError(f"Unknown TX transport '{transport}'. Choose 'udp' or 'srt'.")


#: Default latency budget per transport (ms). UDP/RTP can run a very tight
#: jitter buffer; SRT needs headroom for retransmission round trips.
_DEFAULT_LATENCY_MS = {"udp": 13, "srt": 125, "rtsp": 50}


def rxPipeline(
    transport: str = "udp",
    latency_ms: int | None = None,
    decoder_chain: str | None = None,
    rtsp_mount: str = "cam",
) -> str:
    """
    Return the full receive-side pipeline for ``cv2``/appsink capture.

    ``$port`` and ``$host`` remain as template placeholders. The decode chain
    is auto-detected for this machine unless ``decoder_chain`` is given.

    Parameters
    ----------
    transport : str
        ``"udp"`` (RTP over UDP), ``"srt"`` (caller mode, connects to the
        device), or ``"rtsp"`` (connects to an ``RTSPCameraServer``).
    latency_ms : int, optional
        Jitter-buffer / transport latency budget in milliseconds. Defaults
        per transport: 13 for UDP, 125 for SRT, 50 for RTSP.
    decoder_chain : str, optional
        Override the detected H.264 decode chain.
    rtsp_mount : str, optional
        Mount point used when ``transport="rtsp"``.
    """
    if transport not in _DEFAULT_LATENCY_MS:
        raise ValueError(f"Unknown RX transport '{transport}'. Choose 'udp', 'srt', or 'rtsp'.")
    if latency_ms is None:
        latency_ms = _DEFAULT_LATENCY_MS[transport]
    decoder = decoder_chain or detectH264DecoderChain()
    sink = "appsink name=sink drop=true max-buffers=1 sync=false"
    convert_out = f"video/x-raw,format=BGR ! {sink}"

    if transport == "udp":
        return " ! ".join((
            "udpsrc port=$port "
            "caps=application/x-rtp,media=video,encoding-name=H264,payload=96,clock-rate=90000",
            f"rtpjitterbuffer latency={latency_ms} drop-on-late=true",
            "rtph264depay",
            "h264parse",
            decoder,
            convert_out,
        ))
    if transport == "srt":
        return " ! ".join((
            f'srtsrc uri="srt://$host:$port?mode=caller" latency={latency_ms}',
            "tsdemux",
            "h264parse",
            decoder,
            convert_out,
        ))
    return " ! ".join((
        f"rtspsrc location=rtsp://$host:$port/{rtsp_mount} latency={latency_ms}",
        "rtph264depay",
        "h264parse",
        decoder,
        convert_out,
    ))
