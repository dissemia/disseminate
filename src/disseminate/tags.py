"""
Core classes and functions for tags.
"""
from html import escape

from lxml.builder import E


class TagError(Exception): pass


class TagFactory(object):
    pass


def convert_html(element):
    """Converts an element to html."""

    if isinstance(element, Tag):
        if isinstance(element.tag_content, list):
            return E(element.tag_type,
                     *[convert_html(i) for i in element.tag_content])
        else:
            return E(element.tag_type,
                     element.type_content)
    else:
        return element


class Tag(object):

    tag_type = None
    tag_content = None
    tag_attributes = None

    def __init__(self, tag_type, tag_content, tag_attributes):
        self.tag_type = tag_type
        self.tag_attributes = tag_attributes
        if isinstance(tag_content, list) and len(tag_content) == 1:
            self.tag_content = tag_content[0]
        else:
            self.tag_content = tag_content

    def __repr__(self):
        return "{type}{{{content}}}".format(type=self.tag_type,
                                            content=self.tag_content)

    def __getitem__(self, item):
        """Index accession."""
        if not isinstance(self.tag_content, list):
            msg = "Cannot access sub-tree for tag {} because tag contents are not a list"
            raise TagError(msg.format(self.__repr__()))
        return self.tag_content[item]

    def latex(self):
        pass

    def latex_requirements(self):
        return None

    def html(self):
        """The html string for the tag, if the output target is html."""
        return convert_html(self)

    def default(self):
        """The default string for the tag, if no other format matches."""
        return self.tag_content


class Script(object):

    def html(self):
        """Escape the output of script tags."""
        return escape(super(Script, self).html())