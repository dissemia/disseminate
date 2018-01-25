"""
Core classes and functions for tags.
"""
from html import escape

from disseminate.attributes import set_attribute, kwargs_attributes


class TagError(Exception): pass


class TagFactory(object):
    """Generates the appropriate tag for a given tag type.
    """

    allowed_tags = None
    tag_types = None

    def __init__(self, allowed_tags=None):
        self.allowed_tags = allowed_tags

        # Initialize the tag types dict
        self.tag_types = {c.__name__.lower():c for c in Tag.__subclasses__()}

    def tag(self, tag_name, tag_content, tag_attributes):
        """Return the approriate tag, give a tag_type and tag_content"""
        # Just return the content if it's an unallowed tag type
        if (isinstance(self.allowed_tags, list)
           and tag_name not in self.allowed_tags):
            return tag_content

        # Try to find the appropriate subclass
        small_tag_type = tag_name.lower()
        if small_tag_type in self.tag_types:
            cls = self.tag_types[small_tag_type]
        else:
            cls = Tag
        return cls(tag_name, tag_content, tag_attributes)


class Tag(object):
    """A tag to format text in the markup document.

    Attributes
    ----------
    name : str
        The name of the tag. (ex: 'body')
    content : None or str or list
        The contents of the tag. It can either be None, a string, or a list
        of tags and strings. (i.e. a sub-ast)
    attributes : list of tuples
        The attributes of the tag.

    Methods
    -------
    process_ast
        If specified, the tag will be replace by the one (or list of) tags and
        strings returned.
    """

    name = None
    content = None
    attributes = None

    process_ast = None # takes target, returns a tag or list of tags.

    html_required_attributes = None

    def __init__(self, name, content, attributes):
        self.name = name
        self.attributes = attributes
        if isinstance(content, list) and len(content) == 1:
            self.content = content[0]
        else:
            self.content = content

    def __repr__(self):
        return "{type}{{{content}}}".format(type=self.name,
                                            content=self.content)

    def __getitem__(self, item):
        """Index accession."""
        if not isinstance(self.content, list):
            msg = ("Cannot access sub-tree for tag {} because "
                   "tag contents are not a list")
            raise TagError(msg.format(self.__repr__()))
        return self.content[item]

    def context(self):
        """

        Returns
        -------
        global_context, local_context : dict, dict
            A dict that is accessible from the root context (global) and a
            dict that is accessible from a local context.
        """
        pass

    # def latex(self, context=None):
    #     pass
    #
    # def html(self, context=None):
    #     """The html string for the tag, if the output target is html."""
    #     return convert_html(self)
    #
    # def default(self, context=None):
    #     """The default string for the tag, if no other format matches."""
    #     return self.tag_content


class Script(Tag):

    def html(self):
        """Escape the output of script tags."""
        return escape(super(Script, self).html())


class Img(Tag):
    """The img tag for inserting images."""

    def __init__(self, name, content, attributes):
        super(Img, self).__init__(name, content, attributes)

        # Place the image location in the src attribute
        if self.attributes is None:
            self.attributes = []

        contents = self.content.strip()
        self.content = None

        if contents:
            self.attributes = set_attribute(self.attributes,
                                            ('src', contents),
                                            method='r')

