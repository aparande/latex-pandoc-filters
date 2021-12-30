from typing import Any, NamedTuple

from pandocfilters import stringify
from ..pandoc_state import PandocState
from .pandoc_filter import PandocFilter

class SectionLabelFilter(PandocFilter):
  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == "Header":
      [level, [label, _, _], content] = value
      self.state.sections[label] = stringify(content)


