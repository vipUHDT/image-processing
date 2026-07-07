# camera

The camera package is the image-acquisition layer of `image_processing`. It defines a
common camera abstraction, the backends that actually move frames off of physical
hardware, and the concrete camera controllers that wire everything together for a
specific sensor.

## What this directory does

- **`camera.py`** — Defines the core abstractions every camera shares:
  - `Camera` (ABC) — the interface a caller programs against (`setBackend`,
    `setConnection`, `initialize`, `captureFrame`).
  - `CameraBackend` (ABC) — the contract a transport/backend must implement.
  - `CameraMetadata` — a dataclass describing the physical sensor (sensor width/height,
    image width/height, focal length). This is the same metadata consumed by the
    georeferencing math in [`odcl`](../odcl/README.md).
  - `constructGstreamerPipeline` — a small helper that joins pipeline stages with ` ! `.
- **`backends/`** — Implementations of `CameraBackend`:
  - `remote.py` (`RemoteCamera`) — drives a camera that lives on a remote board (the RB5)
    over SSH: launches/terminates the remote GStreamer process, looks up PIDs, and cleans
    up log files.
  - `gstreamer.py` (`GStreamerCamera`, `GStreamerManager`, `BufferlessVideoCapture`) —
    owns the GStreamer TX/RX pipelines, receives the stream locally, and serves the
    latest frame. Uses the native appsink capture when PyGObject is available, else a
    one-slot, thread-backed OpenCV buffer so callers always read the freshest frame.
  - `pipelines.py` — builds the pipeline strings: hardware (`qtic2venc`) vs software
    (`x264enc`) encoding on the device, UDP/SRT/RTSP transports, and per-machine H.264
    decoder detection (Jetson NVDEC → macOS VideoToolbox → software → `decodebin`).
  - `appsink.py` (`GstAppSinkCapture`, `TimestampedFrame`) — pulls frames directly from
    an appsink with their buffer PTS, so frames from different cameras can be paired by
    capture time. Requires `python3-gi` + GStreamer GI bindings.
  - `rtsp.py` (`RTSPCameraServer`) — generates, uploads (SFTP), and runs (SSH) a
    `gst-rtsp-server` script on the device that serves all cameras as RTSP mounts,
    replacing the per-camera `gst-launch` + `pgrep` process management. Requires
    `python3-gi` + `gir1.2-gst-rtsp-server-1.0` on the device.
  - `__init__.py` exposes `getBackend(name)` for backend lookup by string (e.g. `"rb5"`).
- **`controllers/`** — Concrete, ready-to-use camera definitions:
  - `Hadron640R.py` — controller for the FLIR Hadron 640R, which exposes two sensors,
    the `OV64B` (EO/visible) and `Boson640` (IR). It builds both TX (encode + send on the
    board) and RX (receive + decode locally) GStreamer pipelines, starts the remote
    streams, and exposes `capture()` returning a synchronized `(rgb_img, infrared_img)`
    pair.

## How it connects to the rest of the package

- **→ [`connection`](../connection/README.md):** backends use `SSH_Controller` to run
  commands on the remote board and `SFTPController` to download recorded video files.
- **→ [`odcl`](../odcl/README.md):** `CameraMetadata` defined here is required by
  `Georeference_Engine` to convert pixel detections into GPS coordinates.
- **→ [`data`](../data/README.md):** frames returned by `captureFrame()` / `capture()`
  are the `np.ndarray` images persisted by `DataManager.append_rgb` / `append_ir`.
- **→ [`tools`]:** controllers use `tools.timestamp` to name recorded remote video files.

## Typical flow

```python
from image_processing.camera.controllers.Hadron640R import Hadron640R

cam = Hadron640R()               # encoder="hardware", transport="udp" by default
cam.setConnection(client_ip, host_ip, username, password)
cam.initialize()                 # opens SSH/SFTP, starts remote + local pipelines
rgb_img, ir_img = cam.capture()  # latest frame from each camera (unpaired)

# Timestamp-paired capture — use this for EO/IR fusion:
eo, ir, skew = cam.captureSynchronized(tolerance_s=0.034)
if eo is not None:
    fuse(eo.frame, ir.frame)     # skew tells you the residual pairing error (s)

cam.terminate()
```

### Choosing encoder and transport

```python
Hadron640R(encoder="hardware", transport="udp")   # default: RB5 HW encode, RTP/UDP
Hadron640R(encoder="software", transport="udp")   # original x264enc behavior
Hadron640R(transport="srt")                       # loss recovery on flaky links
Hadron640R(transport="rtsp")                      # one managed server on the device
```

- `encoder="hardware"` uses the RB5's C2 encoder (`qtic2venc`) — verify it exists on
  the device with `gst-inspect-1.0 qtic2venc`, otherwise pass `encoder="software"`.
- `transport="rtsp"` requires `python3-gi` and `gir1.2-gst-rtsp-server-1.0` on the
  device, and does not record on-device MP4s (UDP/SRT keep the recording tee).
- For per-frame PTS timestamps on the ground station, install PyGObject locally
  (`GST_PYTHON_AVAILABLE` reports whether it was found). Without it,
  `captureSynchronized` still works using frame arrival times.
- The hardware-encoder, SRT, and RTSP paths have not been exercised against RB5
  hardware yet — bench-test before flying.
