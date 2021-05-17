"""
Software checkers for external dependencies.

Checkers are used to verify the installation and configuration of external
software dependencies.
"""
from .types import (All, Any, Optional,
                    SoftwareDependency, SoftwareDependencyList)
from .checker import Checker
from .python import PythonChecker
from .external import ImageExtChecker
from .pdf import PdfChecker
from .exceptions import MissingHandler

__all__ = ('All', 'Any', 'Optional', 'SoftwareDependency',
           'SoftwareDependencyList', 'Checker', 'PythonChecker',
           'ImageExtChecker', 'PdfChecker', 'MissingHandler')
