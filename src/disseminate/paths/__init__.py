"""
Path objects (pathlib.Path) that can keep track of subpaths for a project and
targets.
"""

from .paths import SourcePath, TargetPath
from . import utils

__all__ = ('SourcePath', 'TargetPath', 'utils')
