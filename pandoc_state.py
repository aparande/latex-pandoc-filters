from typing import NamedTuple, Dict, List

class PandocState(NamedTuple):
  """
  Stores the state of latex filters
  """
  labels: Dict[str, List[str]] = {}
  envs: Dict = {}

