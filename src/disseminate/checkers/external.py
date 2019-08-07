"""
Checkers for external dependencies.
"""

from .checker import Checker
from ..software_dependencies import image_deps


class ImageExtChecker(Checker):
    """Checker for external dependencies for image processing."""

    def __init__(self, image_deps=image_deps):
        super().__init__('image external deps', *image_deps.dependencies)
