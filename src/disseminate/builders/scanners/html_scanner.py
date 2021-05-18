"""
A scanner for html files.
"""
import regex

from .scanner import Scanner


#: regex for processing <link> tags in html headers
#: matches: '<link rel="stylesheet" href="/media/css/bootstrap.min.css">'
#: matches: '<link href="{{ "/media/css/default.css" | rewrite_path }}">'
_re_html_link = regex.compile(r'<link\s+(?:[^>]*?\s+)?'
                              r'href=\s*[\"\'\s\{]+'
                              r'(.*?)'
                              r'[\"\']')

#: regex for processing <img> tags in html templates
#: matches: '<img src="/media/icons/menu_inactive.svg">'
#: matches: '<img src="{{ "/media/icons/menu_inactive.svg" | rewrite_path }}">'
_re_html_img = regex.compile(r'<img\s+(?:[^>]*?\s+)?'
                             r'src=\s*[\"\'\s\{]+'
                             r'(.*?)'
                             r'[\"\']')


class HtmlScanner(Scanner):
    """A scanner for html files."""

    extensions = ('.html', '.htm', '.xhtml')

    @staticmethod
    def scan_function(content):
        """Scan additional file dependencies from the content of an html
        file."""
        filepaths = []

        # Find the matches
        for re_func in (_re_html_link, _re_html_img):
            for match in re_func.finditer(content):
                # Retrieve the link
                link = match.groups()[0]

                # Skip protocols; we're looking for actual files
                if '://' in link:
                    continue

                filepaths.append(link)
        return filepaths
