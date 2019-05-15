"""
Renderers are components that convert tag trees (Abstract Syntax Trees, ASTs)
into rendered text strings using either built-in (global) templates or
user-specified (local) templates.
"""

from .base_renderer import BaseRenderer, module_templates_relpath
from .jinja_renderer import JinjaRenderer
