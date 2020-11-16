"""
A TargetBuilder for xhtml files.
"""
from .html_builder import HtmlBuilder


class XHtmlBuilder(HtmlBuilder):
    """A builder for xhtml files."""

    available = True
    priority = 1000
    infilepath_ext = '.dm'
    outfilepath_ext = '.xhtml'
