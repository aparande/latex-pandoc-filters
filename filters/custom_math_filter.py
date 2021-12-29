import re
from typing import Any, List, NamedTuple, Dict

from pandocfilters import Math

from ..pandoc_state import PandocState
from .pandoc_filter import PandocFilter

class CustomMathExpr(NamedTuple):
  reg_exp: str
  sub_exp: str

class CustomMathFilter(PandocFilter):
  """
  Convert custom math expressions using regular expression substitution
  """
  def __init__(self, config, state:PandocState):
    self.exprs = [CustomMathExpr(**conf) for
        conf in config]
    super().__init__(config, state)

  def convert_math(self, code):
    for expr in self.exprs:
      code = re.sub(expr.reg_exp, expr.sub_exp, code)

    return code

  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == 'Math':
      [mathType, value] = value
      value = self.convert_math(value)
      return Math(mathType, value)

