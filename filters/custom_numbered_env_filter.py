import sys
import re

from typing import NamedTuple, List, Any
from pandocfilters import Math, Str, RawInline, Para, Header

from ..pandoc_state import PandocState
from .pandoc_filter import PandocFilter

class CustomNumberedTexEnv(NamedTuple):
  """
  Custom numbered environments are defined by \\newtheorem{tag}{name} in the
  LaTeX header. Their labels are formatted as label_prefix:label_name
  """
  label_prefix: str
  tag: str
  name: str

class CustomNumberedEnvFilter(PandocFilter):
  """
  Convert a custom numbered environment (created with \\newtheorem in LaTeX)
  """
  def __init__(self, config, state:PandocState):
    super().__init__(config, state)

    self.envs = []
    for env in config:
      cnte = CustomNumberedTexEnv(**env)
      self.envs.append(cnte)
      self.state.envs[env['label_prefix']] = cnte
      self.state.labels[env['label_prefix']] = []

  def str_to_para(self, code:str) -> Para:
    """
    Convert string with LaTeX math into Pandoc Paragraph with Display/InlineMath
    """
    # Standardize equations to use $$
    code = code.replace("\\[", "$$")
    code = code.replace("\\]", "$$")
    code = code.replace("\\begin{equation}", "$$")
    code = code.replace("\\end{equation}", "$$")

    # Replace line breaks with asdf marker to preserve line breaks
    code = code.replace("\n", "asdf")
    block = []
    marker = 0

    for match in re.finditer("(\$\$.*?\$\$)|(\\\\cref\{.*?\})|(\$.*?\$)", code):
      (start, end) = match.span()
      if match.group(1) is not None:
        # Convert $$ to DisplayMath
        block.append(Str(code[marker:start].replace("asdf", "\n")))
        math_value = code[start+2:end-2].replace("asdf", " ")

        marker = end
        block.append(Math({"t": "DisplayMath"}, math_value))
      elif match.group(2) is not None:
        # LaTeX crefs are put inside RawInline elements. So any crefs in a string
        # need to be converted into RawInline
        block.append(Str(code[marker:start]))
        ref = code[start:end]
        block.append(RawInline("latex", ref))
        marker = end
      elif match.group(3) is not None:
        # Convert $ to InlineMath
        block.append(Str(code[marker:start].replace("asdf", "\n")))
        math_value = code[start+1:end-1].replace("asdf", " ")
        marker = end
        block.append(Math({"t": "InlineMath"}, math_value))

    block.append(Str(code[marker:].replace("asdf", "\n").strip()))
    return Para(block)


  def custom_numbered_env(self, code:str, env: CustomNumberedTexEnv):
    """
    Process a custom numbered environment 
    """
    found_match = False
    
    # Detect the label of the environment
    # Regular expression for \label{env.label_prefix:...}
    label_exp = re.compile("(\\\\label\{" + env.label_prefix + ":)(.*?)(\})")
    for match in label_exp.finditer(code):
      found_match = True
      sys.stderr.write(f"Found {env.name} {match.group(2)}\n")
      self.state.labels[env.label_prefix].append(match.group(2))
      (start, end) = match.span()
      code = code[:start] + code[end:]

    if not found_match:
      label_len = len(self.state.labels[env.label_prefix])
      self.state.labels[env.label_prefix].append(f"{label_len+1}")

    # Grab the title of the environment
    label_len = len(self.state.labels[env.label_prefix])
    title_exp = re.compile("(\\\\begin\{" + env.tag + "\}\[)(.*?)(\])")
    match = re.search(title_exp, code)
    if match is not None:
      sys.stderr.write(f"{env.name} has title {match.group(2)}\n")
      title = match.group(2).replace("\'", "'")
      code = re.sub(title_exp, "\n", code)
      header = Header(3, [f"{env.tag}-{label_len}", [], []],
          [Str(f"{env.name} {label_len} ({title})")])
    else:
      header = Header(3, [f"{env.tag}-{label_len}", [], []],
          [Str(f"{env.name} {label_len}")])

    # Remove the \begin and \end tags of the block
    lines = map(lambda x: x.strip(), code.split("\n")[1:-1]) 
    output = "\n".join(lines)

    # Convert the body of the environment to a paragraph
    output = self.str_to_para(output)

    return [header, output]

  def __call__(self, key:str, value:Any, fmt:str, meta:Any):
    if key == 'RawBlock':
      fmt, code = value
      if fmt == "latex":
        for env in self.envs:
          if re.match("\\\\begin\{" + env.tag + "\}", code):
            return self.custom_numbered_env(code, env)
