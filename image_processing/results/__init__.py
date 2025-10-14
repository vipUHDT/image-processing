from abc import ABC, abstractmethod
from typing import Optional

class ModelResult(ABC):
    def __init__(self, model_name: Optional[str] = None, model_hash: Optional[str] = None):
        self.model_name = model_name
        self.model_hash = model_hash
