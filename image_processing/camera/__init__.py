"""
The `image_processing.camera` package provides classes and utilities
for handling camera input, streaming, and configuration.

It includes:
- `backends` for different camera sources (e.g., GStreamer, remote).
- `controllers` for specific sensors like the Hadron 640R.
- `camera` core definitions and metadata structures.
"""

from .camera import Camera, CameraBackend, CameraMetadata, constructGstreamerPipeline