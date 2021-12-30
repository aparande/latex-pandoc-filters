"""
Error classes
"""

class LabelNotFoundError(Exception):
  """
  Exception raised when a label is not found in the document.
  """
  def __init__(self, label):
    super().__init__(f"Could not find {label} in document")
