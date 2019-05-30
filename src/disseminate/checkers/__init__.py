"""
Checkers are used to verify the installation and configuration of external
software dependencies.
"""
from .types import (All, Any, Optional,
                    SoftwareDependency, SoftwareDependencyList)
from .checker import Checker
from .pdf import PdfChecker
from .exceptions import MissingHandler
