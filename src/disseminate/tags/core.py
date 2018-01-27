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

    def tag(self, tag_name, tag_content, tag_attributes,
                  local_context, global_context):
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

        return cls(name=tag_name, content=tag_content,
                   attributes=tag_attributes,
                   local_context=local_context, global_context=global_context)


class Tag(object):
    """A tag to format text in the markup document.

    .. note:: Tags are created asynchroneously, so the creation of a tag
              should not depend on the local_context or global_context. These
              will only be partially populated at creation time. Only the
              target specific methods (html, tex, ...) should return new tags
              that depend on these contexts.

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
    html
        If specified, using this function to generate the html element
        (:obj:`lxml.builder.E`) instead of the default.
    """

    name = None
    content = None
    attributes = None
    local_context = None

    process_ast = None # takes target, returns a tag or list of tags.
    html = None
    tex = None

    html_required_attributes = None

    def __init__(self, name, content, attributes,
                 local_context, global_context):
        self.name = name
        self.attributes = attributes
        if isinstance(content, list) and len(content) == 1:
            self.content = content[0]
        else:
            self.content = content
        self.local_context = local_context
        self.global_context = global_context

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



class Script(Tag):

    def html(self):
        """Escape the output of script tags."""
        return escape(super(Script, self).html())

