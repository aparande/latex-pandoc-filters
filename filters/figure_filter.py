import sys
from abc import ABC, abstractmethod
from typing import Any, NamedTuple

import re
from pandocfilters import Para, Image, Str

from ..utils import convert_to_image
from ..pandoc_state import PandocState
from .pandoc_filter import PandocFilter

class FigureEnv(NamedTuple):
  name: str

class FigureFilter(PandocFilter):
  def __init__(self, config, state: PandocState):
    super().__init__(config, state)
    self.image_dir = config['dir']
    self.image_tag = config['tag']
    self.header_file = config['header']
    self.cache_prefix = config['cache_prefix']

    self.state.labels["fig"] = []
    self.state.envs["fig"] = FigureEnv("Figure")

    self.state.labels["table"] = []
    self.state.envs["table"] = FigureEnv("Table")

  def convert_algorithm(self, fmt, code):
    figure_code = "\n".join(code.split("\n")[1:-1])
    filename, filetype = convert_to_image(fmt, figure_code, header_file =
        self.header_file, dir_prefix=self.cache_prefix)

    return Para([Image(['', [], []], [], [f"{self.image_dir}/{filename}.{filetype}", ""])])

  def convert_figure(self, fmt, code):
    meta_regex = re.compile("(\\\\caption\{(.*?)\})|(\\\\label\{(.*?)\})")
    figure_code = meta_regex.sub("", code)
    figure_code = re.sub("\\\\centering", "", figure_code)
    figure_code = re.sub("(\[H\])|(\[!h\])", "", figure_code)
    figure_code = re.sub("(\\\\begin\{figure\})|(\\\\begin\{table\})", "\\\\begin{minipage}[c]{1.5\\\\linewidth}", figure_code)
    figure_code = re.sub("(figure)|(table)", "minipage", figure_code)
    figure_code = "\n".join(figure_code.split("\n")[1:-1])
    filename, filetype = convert_to_image(fmt, figure_code,
        header_file=self.header_file, dir_prefix=self.cache_prefix)
 
    caption, label = "", None
    for match in meta_regex.finditer(code):
      if match.group(2) is not None:
        caption = match.group(2)
      elif match.group(4) is not None:
        label = match.group(4).split(":")

    if label is not None:
      if label[0] == "fig":
        self.state.labels["fig"].append(label[1])
        sys.stderr.write(f"Found figure {label[1]}\n")
        caption = f"Figure {len(self.state.labels['fig'])}: {caption}"
      elif label[0] == "table":
        self.state.labels["table"].append(label[1])
        sys.stderr.write(f"Found table {label[1]}\n")
        caption = f"Table {len(self.state.labels['table'])}: {caption}"

    return Para([Image(['', [], []], [Str(caption)], [f"{self.image_dir}/{filename}.{filetype}", ""])])

  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == 'RawBlock':
      [fmt, code] = value
      if fmt == "latex" and re.match("\\\\begin{" + self.image_tag + "}", code):
        if "algorithm" in code:
          return self.convert_algorithm(fmt, code)
        else:
          return self.convert_figure(fmt, code)
