"""
A handler to pygmentize a source page
"""
from pathlib import Path

from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter

from .server import ServerHandler


class PygmentizeHandler(ServerHandler):
    """A handler to pygmentize source files"""

    def get(self, path):
        # Get the appropriate lexer
        lexer = get_lexer_for_filename(path, stripall=True)

        # Setup the formatter
        formatter = HtmlFormatter(linenos=True, cssclass="source", full=True)

        # Source file
        code = Path(path).read_text()

        self.write(highlight(code, lexer, formatter))
