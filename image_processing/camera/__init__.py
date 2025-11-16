"""
Camera subsystem initialization and public API exports.

This subpackage defines the core camera abstraction layer used throughout
the image_processing framework. It exposes:

- Generic camera interface and metadata structures
- Abstract backend contract for concrete camera implementations
- GStreamer pipeline construction utility

Concrete backends and controllers are located in the ``backends`` and
``controllers`` submodules respectively.
"""

from .camera import Camera, CameraBackend, CameraMetadata, constructGstreamerPipeline