"""
Exceptions for target builders
"""
from ..exceptions import BuildError


class TargetBuilderNotFound(BuildError):
    """Error raised when a target builder was requested but not found."""
