"""
A scanner for html files.
"""
import regex

from .scanner import Scanner


#: regex for processing <link> tags in html headers
_re_html_link = regex.compile(r'<link\s+(?:[^>]*?\s+)?'
                              r'href=(["\'])(.*?)'
                              r'\1')


class HtmlScanner(Scanner):
    """A scanner for html files."""

    extensions = ('.html', '.htm')

    @staticmethod
    def scan_function(content):
        """Scan additional file dependencies from the content of an html
        file."""
        filepaths = []

        # Find the matches
        for match in _re_html_link.finditer(content):
            # Retrieve the link
            link = match.groups()[1]

            # Skip protocols; we're looking for actual files
            if '://' in link:
                continue

            filepaths.append(link)
        return filepaths

