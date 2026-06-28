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
    owns the GStreamer TX/RX pipelines, receives the RTP stream locally through OpenCV,
    and serves the latest frame with a one-slot, thread-backed buffer so callers always
    read the freshest frame.
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

cam = Hadron640R()
cam.setConnection(client_ip, host_ip, username, password)
cam.initialize()                 # opens SSH/SFTP, starts remote + local pipelines
rgb_img, ir_img = cam.capture()  # synchronized EO/IR frames
cam.terminate()
```
