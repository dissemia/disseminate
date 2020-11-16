"""
A TargetBuilder for txt files.
"""
from .target_builder import TargetBuilder


class TxtBuilder(TargetBuilder):
    """A builder for txt files."""

    available = True
    priority = 1000
    infilepath_ext = '.dm'
    outfilepath_ext = '.txt'
