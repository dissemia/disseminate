"""
Wrappers and utilities for formatting text and tags into different formats
"""

from .tex import tex_env, tex_cmd, TexFormatError
from .html import html_tag, html_entity, HtmlFormatError
