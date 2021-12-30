from typing import Any

from pandocfilters import Str, Math
from ..pandoc_state import PandocState
from .pandoc_filter import PandocFilter

class DisplayMathFilter(PandocFilter):
  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == 'Math':
        [mathType, value] = value
        if mathType['t'] == "InlineMath":
            mathType['t'] = "DisplayMath"
            return Math(mathType, value)
        else:
            return [Str("\n\n"), Math(mathType, value), Str("\n\n")]


