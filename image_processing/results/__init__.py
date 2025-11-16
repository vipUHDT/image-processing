"""
Base result types for model outputs.

This module defines :class:`ModelResult`, an abstract base class that
stores common metadata about a model used to generate a result, such as
its name and a hash or version identifier. Task-specific result types
(e.g., detection results, classification summaries) can subclass this
base to attach additional fields while preserving a consistent metadata
interface.
"""

from abc import ABC, abstractmethod
from typing import Optional

class ModelResult(ABC):
    def __init__(self, model_name: Optional[str] = None, model_hash: Optional[str] = None):
        self.model_name = model_name
        self.model_hash = model_hash
