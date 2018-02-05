"""
Tags for headings.
"""
from lxml.builder import E

from .core import Tag


class Heading(Tag):
    """A heading tag."""
    html_name = "h2"
    tex_name = "section"

    def html(self, level=1):
        """Return an HTML element"""
        # Collect the content elements
        if isinstance(self.content, list):
            elements = [i.html(level + 1) if hasattr(i, 'html') else i
                        for i in self.content]
        elif isinstance(self.content, str):
            elements = self.content
        else:
            elements = None

        # collect the attributes
        attrs = {}
        return E(self.html_name, *elements, **attrs)

    def tex(self, level=1):
        if isinstance(self.content, list):
            element = ''.join([i.html(level + 1) if hasattr(i, 'html') else i
                               for i in self.content])
        elif isinstance(self.content, str):
            element = self.content
        else:
            element = ''

        return "\\{tex_name}\{{heading}\}".format(tex_name=self.tex_name,
                                                  heading=element)


class Section(Heading):
    """A section heading tag."""
    html_name = "h2"
    tex_name = "section"


class SubSection(Heading):
    """A subsection heading tag."""
    html_name = "h3"
    tex_name = "subsection"


class SubSubSection(Heading):
    """A subsubsection heading tag."""
    html_name = "h4"
    tex_name = "subsubsection"


class Para(Heading):
    """A paragraph heading tag."""
    html_name = "paragraph-heading"
    tex_name = "paragraph"
