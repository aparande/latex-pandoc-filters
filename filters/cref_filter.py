import re
from typing import Any

from pandocfilters import Str
from .pandoc_filter import PandocFilter
from ..errors import LabelNotFoundError

class CrefFilter(PandocFilter):
  """
  Convert Crefs in RawInline blocks to a text representation
  """
  def label_to_text(self, label:str) -> str:
    """
    Convert a label to a text representation given a dictionary mapping the type
    of each label to the full text representation of that type and a list of all
    possible labels.
    """
    ref_type, ref_val = label.split(":")
    label_env = self.state.envs.get(ref_type)
    labels = self.state.labels.get(ref_type, [])

    if ref_val not in labels:
      if label in self.state.sections:
        return self.state.sections[label]
      raise LabelNotFoundError(label)

    label_num = labels.index(ref_val) + 1

    return f"{label_env.name} {label_num}"

  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == "RawInline":
      [fmt, code] = value
      if fmt == "latex" and (match := re.match("\\\\cref\{(.*?)\}", code)):
        refs = match.group(1).split(",")
        return Str(", ".join(map(self.label_to_text, refs)))
