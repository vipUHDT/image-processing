"""
ODCL (Onboard Detection, Classification, and Localization) package.

This package aggregates object detection, object classification, and
geospatial localization components. The :class:`ODCL` class provided here
is currently a placeholder for a higher-level pipeline controller.

Typical ODCL workflow components:
    - Detection (image -> pixel-level detections)
    - Classification (detection class assignments)
    - Localization (convert pixel coordinates -> GPS)
"""

from .Classification import *
from .Localize import *


class ODCL():
    def __init__(self):
        self.pipeline = []
        