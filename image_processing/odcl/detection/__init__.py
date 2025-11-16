"""
Detection module for the ODCL

This subpackage provides:

- Low-level detection data structures (:class:`Detection`,
  :class:`DetectionModelResult`)
- The high-level detection manager (:class:`DetectionManager`) that
  manages queued inference, threading, duplicate suppression, and
  georeferencing integration
- SAHI-based model configuration utilities (:class:`SahiConfig`,
  :class:`ModelConfig`, and :class:`SahiDetectionModel`)

The public API is defined in :data:`__all__` for clarity and for proper
export during Sphinx documentation generation.
"""

from .Detection import *
from .DetectionManager import *
from .SahiConfig import *