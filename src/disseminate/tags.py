"""
Core classes and functions for tags.
"""
from html import escape

from lxml.builder import E
from lxml import etree

from . import settings
from .attributes import set_attribute, kwargs_attributes


class TagError(Exception): pass


class TagFactory(object):
    """Generates the appropriate tag for a given tag type."""

    allowed_tags = None
    tag_types = None

    def __init__(self, allowed_tags=None):
        self.allowed_tags = allowed_tags

        # Initialize the tag types dict
        self.tag_types = {c.__name__.lower():c for c in Tag.__subclasses__()}

    def tag(self, tag_type, tag_content, tag_attributes):
        """Return the approriate tag, give a tag_type and tag_content"""
        # Just return the content if it's an unallowed tag type
        if (isinstance(self.allowed_tags, list)
           and tag_type not in self.allowed_tags):
            return tag_content

        # Try to find the appropriate subclass
        small_tag_type = tag_type.lower()
        if small_tag_type in self.tag_types:
            cls = self.tag_types[small_tag_type]
        else:
            cls = Tag
        return cls(tag_type, tag_content, tag_attributes)


def convert_html(element, root_tag=settings.html_root_tag, pretty_print=settings.html_pretty):
    """Converts an element to html."""

    if isinstance(element, Tag):
        if isinstance(element.tag_content, list):
            return E(element.tag_type,
                     *[convert_html(i) for i in element.tag_content])
        else:
            # Only include content is the content is not None or the empty
            # string
            content = (element.tag_content.strip()
                       if isinstance(element.tag_content, str)
                       else element.tag_content)
            content = [content, ] if content else []

            # Prepare the attributes
            kwargs = (kwargs_attributes(element.tag_attributes)
                      if element.tag_attributes
                      else dict())
            return E(element.tag_type,
                     *content,
                     **kwargs)

    elif isinstance(element, list):
        return etree.tostring(E(root_tag, *[convert_html(i) for i in element]),
                              pretty_print=pretty_print).decode("utf-8")
    else:
        return element


class Tag(object):

    tag_type = None
    tag_content = None
    tag_attributes = None

    html_required_attributes = None

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
            msg = ("Cannot access sub-tree for tag {} because "
                   "tag contents are not a list")
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


class Script(Tag):

    def html(self):
        """Escape the output of script tags."""
        return escape(super(Script, self).html())


class Img(Tag):
    """The img tag for inserting images."""

    def __init__(self, tag_type, tag_content, tag_attributes):
        super(Img, self).__init__(tag_type, tag_content, tag_attributes)

        # Place the image location in the src attribute
        if self.tag_attributes is None:
            self.tag_attributes = []

        contents = self.tag_content.strip()
        self.tag_content = None

        if contents:
            self.tag_attributes = set_attribute(self.tag_attributes,
                                                ('src', contents),
                                                method='r')
        print(self.tag_attributes)

