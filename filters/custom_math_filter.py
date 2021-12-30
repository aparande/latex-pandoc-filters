import re
import sys
from typing import Any, List, NamedTuple, Dict

from pandocfilters import Math

from ..pandoc_state import PandocState
from .pandoc_filter import PandocFilter

class CustomMathExpr(NamedTuple):
  reg_exp: str
  sub_exp: str

class EquationEnv(NamedTuple):
  name: str
  label_prefix: str

class CustomMathFilter(PandocFilter):
  """
  Convert custom math expressions using regular expression substitution
  """
  def __init__(self, config, state:PandocState):
    super().__init__(config, state)
    self.exprs = [CustomMathExpr(**expr) for
        expr in config['exprs']]

    self.eqn_env = EquationEnv(**config['eqn_env'])
    self.state.labels[self.eqn_env.label_prefix] = []
    self.state.envs[self.eqn_env.label_prefix] = self.eqn_env

  def convert_math(self, code):
    for expr in self.exprs:
      code = re.sub(expr.reg_exp, expr.sub_exp, code)

    code = re.sub("\\\\eqnnumber", " ", code)

    label_exp = re.compile("(\\\\label\{" + self.eqn_env.label_prefix + ":)(.*?)(\})")
    out = ""
    marker = 0
    for match in label_exp.finditer(code):
        sys.stderr.write(f"Found equation {match.group(2)}\n")
        self.state.labels[self.eqn_env.label_prefix].append(match.group(2))
        eqn_number = len(self.state.labels[self.eqn_env.label_prefix])

        (start, end) = match.span()
        out += code[marker:start] + f"\\qquad ({eqn_number})"
        marker = end
    out += code[marker:]
    return out.replace("\n", " ")

  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == 'Math':
      [mathType, value] = value
      value = self.convert_math(value)
      return Math(mathType, value)

