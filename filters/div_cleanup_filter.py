from typing import Any

from .pandoc_filter import PandocFilter

class DivCleanupFilter(PandocFilter):
  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == "Div":
      [attrs, elems] = value
      return elems

