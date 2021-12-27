from typing import Any

import sys
import re

from pandocfilters import Str, Strong

from .pandoc_filter import PandocFilter

class BoldedFilter(PandocFilter):
  """
  Convert textbf in a Str to a Strong
  """
  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == "Str" and (match := re.search("\\\\textbf\{(.*?)\}", value)):
      (start, end) = match.span()
      bolded = match.group(1)
      sys.stderr.write(f"Found bolded text: {bolded}\n")
      return [Str(value[:start]), Strong([Str(bolded)]), Str(value[end+1:])]
