"""Homography-based EO/IR alignment helpers for the fusion pipeline.

Re-exports the shared implementations from :mod:`image_processing.tools.homography`
so the fusion pipeline and the general tools package use one definition.
"""

from image_processing.tools.homography import cropRGBToMatchIR, mapPixelCoordinates

__all__ = ["cropRGBToMatchIR", "mapPixelCoordinates"]
