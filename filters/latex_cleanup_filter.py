import re
from typing import Any

from .pandoc_filter import PandocFilter

class LatexCleanupFilter(PandocFilter):
  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == "RawInline" or key =="RawBlock":
      [fmt, code] = value
      if fmt == "latex":
        return []
