"""Object Detection, Classification, and Localization (ODCL) pipeline components."""

from .Localize import (
    Georeference_Engine,
    georeference_aeqd,
    georeference_enu,
    georeference_manual,
    georeference_utm,
    haversine,
)

__all__ = [
    "Georeference_Engine",
    "ODCL",
    "georeference_aeqd",
    "georeference_enu",
    "georeference_manual",
    "georeference_utm",
    "haversine",
]


class ODCL:
    """Container for an ODCL processing pipeline."""

    def __init__(self):
        self.pipeline = []
