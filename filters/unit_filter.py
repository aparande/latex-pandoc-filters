import re
from typing import Any, Dict

from pandocfilters import Math
from ..pandoc_state import PandocState
from .pandoc_filter import PandocFilter

class UnitFilter(PandocFilter):
  def __init__(self, config, state: PandocState):
    super().__init__(config, state)
    self.unit_map = config['unit_map']

  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == 'Math':
      [mathType, code] = value

      si_exp = re.compile("(\\\\SI)(\[.*?\])?\{(.*?)\}\{(.*?)\}")
      for match in si_exp.finditer(code):
        num = match.group(3)
        unit = "".join(list(map(lambda x: self.unit_map.get(x, ''), match.group(4).split("\\"))))
        (start, end) = match.span()
        code = code[:start] + num +"\\text{" + unit + "}" + code[end:]

      return Math(mathType, code)
