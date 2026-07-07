# camera/backends

Backends that move frames from the camera hardware to the ground station:
pipeline construction ([`pipelines.py`](pipelines.py)), local capture
([`gstreamer.py`](gstreamer.py), [`appsink.py`](appsink.py)), remote process
control over SSH ([`remote.py`](remote.py)), and the on-device RTSP server
([`rtsp.py`](rtsp.py)). See [`../README.md`](../README.md) for how these fit
into the camera package.

## What must be installed on the RB5 (device side)

The RB5 runs the transmit side: camera source → H.264 encode → network
transport (+ on-device MP4 recording for UDP/SRT). Requirements depend on
which `encoder=` / `transport=` options you use.

### Always required (baseline, matches the original UDP + software setup)

| Requirement | Provides | Verify on the device |
|---|---|---|
| GStreamer 1.x core tools | `gst-launch-1.0`, `gst-inspect-1.0` | `gst-launch-1.0 --version` |
| gst-plugins-base | `videoconvert`, caps negotiation | `gst-inspect-1.0 videoconvert` |
| gst-plugins-good | `v4l2src`, `rtph264pay`, `udpsink`, `mp4mux`, `tee`, `queue` | `gst-inspect-1.0 v4l2src rtph264pay mp4mux` |
| gst-plugins-bad | `h264parse` | `gst-inspect-1.0 h264parse` |
| Qualcomm camera plugin | `qtiqmmfsrc` (OV64B source) | `gst-inspect-1.0 qtiqmmfsrc` |
| OpenSSH server with SFTP | remote launch + video download | already in use |
| procps / util-linux | `pgrep`, `pkill`, `setsid`, `nohup` | `which pgrep setsid` |
| `flights/` directory in the SSH user's home | MP4 recording target | `mkdir -p ~/flights` |

On a Debian-family image:

```bash
sudo apt install gstreamer1.0-tools gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad
```

(`qtiqmmfsrc` ships with Qualcomm's board support package, not apt. On a
Yocto/LE image the recipes are `gstreamer1.0`, `gstreamer1.0-plugins-base`,
`gstreamer1.0-plugins-good`, `gstreamer1.0-plugins-bad`.)

### Per-option requirements

| Option | Element used | RB5 package | Verify |
|---|---|---|---|
| `encoder="hardware"` (default) | `qtic2venc` (Qualcomm C2 HW encoder) | ships with the Qualcomm BSP / `gstreamer1.0-qti-oss` builds — **not** apt | `gst-inspect-1.0 qtic2venc` |
| `encoder="software"` | `x264enc` | `gstreamer1.0-plugins-ugly` (+ `libx264`) | `gst-inspect-1.0 x264enc` |
| `transport="udp"` (default) | `rtph264pay`, `udpsink` | covered by baseline | — |
| `transport="srt"` | `srtsink`, `mpegtsmux` | `gstreamer1.0-plugins-bad` built with `libsrt` (`libsrt1.5-gstreamer` on newer Debian) | `gst-inspect-1.0 srtsink` |
| `transport="rtsp"` | `GstRtspServer` via Python | `python3-gi`, `gir1.2-gst-rtsp-server-1.0` (pulls `libgstrtspserver-1.0-0`), `python3` | `python3 -c "import gi; gi.require_version('GstRtspServer','1.0'); from gi.repository import GstRtspServer; print('ok')"` |

If `gst-inspect-1.0 qtic2venc` fails, the hardware-encoder chain will not
start; construct the controller with `encoder="software"` (the
`initializeStream` log also points this out when the TX process never
appears).

### One-shot device check

Run over SSH to see what the device supports:

```bash
for e in qtiqmmfsrc v4l2src qtic2venc x264enc h264parse rtph264pay udpsink mp4mux srtsink mpegtsmux; do
    gst-inspect-1.0 --exists $e && echo "OK      $e" || echo "MISSING $e"
done
python3 -c "import gi; gi.require_version('GstRtspServer','1.0'); print('OK      GstRtspServer')" \
    2>/dev/null || echo "MISSING GstRtspServer (python3-gi + gir1.2-gst-rtsp-server-1.0)"
```

## Ground station (receive side)

- **OpenCV built with GStreamer** (`cv2.getBuildInformation()` must show
  `GStreamer: YES`) — required for the `BufferlessVideoCapture` fallback.
- **PyGObject** (`python3-gi` + `gir1.2-gstreamer-1.0` + `gir1.2-gst-app-1.0`,
  or `pip install PyGObject` with GStreamer dev headers) — optional but
  recommended: enables `GstAppSinkCapture`, which attaches per-frame PTS
  timestamps that `Hadron640R.captureSynchronized` pairs on. Without it,
  pairing falls back to frame arrival times.
- An H.264 decoder: `pipelines.detectH264DecoderChain()` picks
  `nvv4l2decoder` (Jetson), `vtdec` (macOS), or `avdec_h264`
  (`gstreamer1.0-libav`) automatically, falling back to `decodebin`.
- For `transport="srt"`: `srtsrc` + `tsdemux` (gst-plugins-bad with libsrt).
- For `transport="rtsp"`: `rtspsrc` (gst-plugins-good).

## Not yet hardware-tested

The hardware-encoder (`qtic2venc`), SRT, and RTSP paths were built against
GStreamer documentation and have **not** been run against RB5 hardware.
Bench-test with the one-shot check above before relying on them in the
field. `encoder="software"` + `transport="udp"` reproduces the original,
flight-proven pipelines.
