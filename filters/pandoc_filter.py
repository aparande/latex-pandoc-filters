from abc import ABC, abstractmethod
from typing import Any

from ..pandoc_state import PandocState

class PandocFilter(ABC):
  def __init__(self, config=None, state: PandocState=None):
    self.state = state

  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    # Return None to leave the tree unchanged
    return None

