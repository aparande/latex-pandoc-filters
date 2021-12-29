import regex
from typing import Any, NamedTuple

from pandocfilters import Math

from ..pandoc_state import PandocState
from .pandoc_filter import PandocFilter

class SingleArgCommand(NamedTuple):
  latex: str
  left: str
  right: str

class SingleArgCmdFilter(PandocFilter):
  """
  Convert single argument LaTeX commands which can have nested commands
  """
  def __init__(self, config, state:PandocState):
    super().__init__(config, state)
    self.cmds = [SingleArgCommand(**conf) for conf in config]

  def convert(self, code, level=0):
    out = ""
    marker = 0
    braces_exp = regex.compile("\{([^}{]*+(?:(?R)[^}{]*)*+)\}")
    
    for match in braces_exp.finditer(code):
      (start, end) = match.span()

      found = False
      for cmd in self.cmds:
        start_pos = start - len(cmd.latex)
        if start_pos >= marker and code[start_pos:start] == cmd.latex:
          out += code[marker:start_pos] + cmd.left + \
          self.convert(match.group(1), level + 1) + cmd.right
          found = True
          break

      if not found:
        out += code[marker:start+1] + self.convert(code[start+1:end-1]) + code[end-1]

      marker = end
    out += code[marker:]
    return out

  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == 'Math':
      [mathType, value] = value
      value = self.convert(value)
      return Math(mathType, value)
