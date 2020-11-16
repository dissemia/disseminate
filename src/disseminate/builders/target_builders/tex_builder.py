"""
A TargetBuilder for tex files.
"""
from .target_builder import TargetBuilder


class TexBuilder(TargetBuilder):
    """A builder for tex files."""

    available = True
    priority = 1000
    infilepath_ext = '.dm'
    outfilepath_ext = '.tex'
