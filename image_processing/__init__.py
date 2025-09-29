import logging
from logging import NullHandler
from dataclasses import dataclass
from typing import Optional

@dataclass 
class PlatformState:
    altitude: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pitch: Optional[float] = None
    yaw: Optional[float] = None
    roll: Optional[float] = None