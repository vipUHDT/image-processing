"""
Data management subpackage.

This subpackage provides tools for organizing and storing image data,
metadata, and detection results in an HDF5-based format. The primary
interface exposed here is :class:`DataManager`, which initializes the
HDF5 layout and provides append, query, and key/value storage utilities.
"""
from .data_manager import *