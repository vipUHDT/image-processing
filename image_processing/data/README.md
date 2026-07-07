# data

The data package is the persistence layer of `image_processing`. It stores everything a
flight produces — image frames, run-level metadata, and detection results — in a single
[HDF5](https://www.h5py.org/) file so the data can be replayed and analyzed after the
flight.

## What this directory does

- **`data_manager.py`**
  - `ImageDataset` — a dataclass describing one image stream to persist: its `name`
    (e.g. `"rgb"`, `"ir"`), per-frame `shape`, and `dtype`.
  - `DataManager` — opens/creates the HDF5 file and manages its layout:
    - `initialize()` builds the `camera/images` group (one resizable, gzip-compressed,
      chunked dataset per `ImageDataset`) plus key/value string datasets for top-level
      `metadata` and per-camera `detections`.
    - `append_rgb` / `append_ir` / `append_frame` — append a single frame, growing the
      dataset by one and validating the frame shape.
    - `add_metadata` / `get_metadata_value` / `list_metadata` — upsert and read flight
      metadata as string key/value pairs.
    - `add_detection` / `get_detection_value` / `list_detections` — the same pattern for
      detection records.
    - `close()` flushes and closes the file.

Datasets are created with `maxshape=(None, ...)` and per-frame chunking so frames can be
streamed in one at a time during a live flight without knowing the final count up front.

## How it connects to the rest of the package

- **← [`camera`](../camera/README.md):** the `np.ndarray` frames returned by a camera's
  `captureFrame()` / `capture()` are what get written through `append_rgb` / `append_ir`.
  An `ImageDataset` `shape`/`dtype` should match the frames the camera produces.
- **← [`odcl`](../odcl/README.md):** detection output (classification, confidence, GPS
  coordinates, etc.) can be serialized into the `detections` key/value store for later
  inspection.

This package depends on nothing else in `image_processing`; it only consumes plain
NumPy arrays and strings, which keeps storage decoupled from acquisition and inference.
