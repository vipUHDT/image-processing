"""
Camera controller implementations for the image_processing.camera subsystem.

This subpackage exposes higher-level orchestration classes that manage one or
more camera backends, configure GStreamer pipelines, handle remote connection
setup, and enable synchronized capture workflows for multi-sensor camera
systems (e.g., FLIR Hadron 640R).
"""

from .Hadron640R import *