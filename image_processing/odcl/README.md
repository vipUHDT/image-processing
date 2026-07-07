# odcl

`odcl` (Object Detection, Classification, and Localization) is the perception layer of
`image_processing`. It takes a captured frame plus the drone's state and produces
geolocated detections: *what* was found, *how confident* the model is, and *where on the
ground* it is.

## What this directory does

- **`Localize.py`** — georeferencing math that maps a target's pixel location to GPS.
  - `Georeference_Engine` — selects a backend by name and exposes `georeference(...)`,
    which takes target pixel coordinates, a `PlatformState`, and `CameraMetadata`.
  - `georeference_utm`, `georeference_enu`, `georeference_aeqd`, `georeference_manual` —
    interchangeable projection strategies that convert a pixel offset (corrected for the
    camera FOV, altitude, and drone yaw) into a latitude/longitude.
  - `haversine(...)` — great-circle distance in meters, used for duplicate detection.
- **`Classification.py`** — placeholder for the classification stage (currently empty).
- **`__init__.py`** — re-exports the above and defines a small `ODCL` pipeline scaffold.
- **`detection/`** — the object-detection stage, built on
  [SAHI](https://github.com/obss/sahi):
  - `SahiConfig.py` — `ModelConfig` (model type/path/device/confidence) plus `SahiConfig`
    (slicing + post-processing/NMS options) and `SahiDetectionModel`, a thin wrapper over
    `AutoDetectionModel.from_pretrained`.
  - `Detection.py` — `Detector` runs (optionally sliced) inference and parses raw model
    output into `Detection` objects (class, confidence, bounding box, center pixel,
    cropped image), aggregated into a `DetectionModelResult`.
  - `DetectionManager.py` — orchestrates the full pipeline. It accepts `QueuedImage`s,
    runs detection across a thread pool, georeferences each detection, drops GPS
    duplicates (via `haversine` + a distance threshold), optionally fires a `gps_callback`,
    and exposes filtering by classification/confidence.

## How it connects to the rest of the package

- **→ root package:** consumes `PlatformState` and `QueuedImage` (defined in
  [`image_processing/__init__.py`](../__init__.py)) as the per-frame input.
- **→ [`camera`](../camera/README.md):** `Georeference_Engine.georeference` requires the
  `CameraMetadata` describing the sensor that produced the frame; without correct sensor
  width/height and focal length the projection is wrong.
- **→ [`results`]:** `DetectionModelResult` extends `results.ModelResult`, and detection
  results flow through `results` for downstream handling.
- **→ [`tools`]:** uses `tools.hash.hashFile` to fingerprint the model weights.
- **→ [`data`](../data/README.md):** detections produced here are the records persisted
  through `DataManager`'s detection key/value store.

## Typical flow

```python
manager = DetectionManager(detection_model_config, camera_metadata)
manager.setGeoreferenceEngine("enu", altitude_offset=0)

manager.queueImage(QueuedImage(image=frame, platform_state=state))
manager.processQueuedImages()   # detect + georeference on worker threads
manager.update()                # drain detection/result queues
detections = manager.getAllDetections()
```
