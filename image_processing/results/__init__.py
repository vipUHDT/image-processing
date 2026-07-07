"""Base types for model inference results."""

from abc import ABC
from typing import Optional


class ModelResult(ABC):
    """
    Base class for results produced by an inference model.

    Parameters
    ----------
    model_name : str, optional
        Name or path of the model that produced the result.
    model_hash : str, optional
        Hash of the model weights, for provenance.
    """

    def __init__(self, model_name: Optional[str] = None, model_hash: Optional[str] = None):
        self.model_name = model_name
        self.model_hash = model_hash
