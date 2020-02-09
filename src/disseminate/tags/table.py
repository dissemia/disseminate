"""
Tags for tables
"""
from .tag import Tag
from ..formats.html import html_tag


class Table(Tag):
    """A tag for a table"""

    def html_fmt(self, content=None, attributes=None, level=1):
        # Collect the contents of this table and prepare in a list
        content = content if content is not None else self.flatten()
        content = [content] if not isinstance(content, list) else content

        # Render the html for the content
        content_html = []
        for item in content:
            if item == self:
                # The flatten method will also return the self tag. To avoid
                # recursion, do not process this tag.
                continue
            elif hasattr(item, 'html_table'):
                # Process the data in the table
                content_html += item.html_table(level=level+1)
            elif hasattr(item, 'html_fmt'):
                # Process other tags like captions
                content_html.append(item.html_fmt(level=level + 1))
            else:
                content_html.append(item)

        # Return the formatted table
        return html_tag('table', formatted_content=content_html, level=level)
