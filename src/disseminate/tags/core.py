"""
Core classes and functions for tags.
"""
from lxml.builder import E
from lxml import etree

from disseminate.attributes import (parse_attributes, set_attribute,
                                    kwargs_attributes, format_tex_attributes,
                                    filter_attributes)
from . import settings


class TagError(Exception):
    """An error was encountered while interpreting a tag."""
    pass


def _all_subclasses(cls):
    """Retrieve all subclasses, sub-subclasses and so on for a class"""
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in _all_subclasses(s)]


class TagFactory(object):
    """Generates the appropriate tag for a given tag type.
    """

    tag_types = None

    def __init__(self, allowed_tags=None):
        # Initialize the tag types dict.
        self.tag_types = dict()
        for scls in  _all_subclasses(Tag):
            # Tag must be active
            if not scls.active:
                continue

            # Collect the name and aliases (alternative names) for the tag
            aliases = (list(scls.aliases) if scls.aliases is not None else
                       list())
            names = [scls.__name__.lower(),] + aliases

            for name in names:
                # duplicate or overwritten tag names are not allowed
                assert name not in self.tag_types
                self.tag_types[name] = scls

    def tag(self, tag_name, tag_content, tag_attributes,
                  local_context, global_context):
        """Return the approriate tag, give a tag_type and tag_content"""

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
              should not depend on the `local_context` of other tags or
              `global_context`. These will only be partially populated at
              creation time. The target specific methods (html, tex, ...), by
              contrast, may depend on local_context and global_context
              attributes populated by other tags.

    Parameters
    ----------
    name : str
        The name of the tag as used in the disseminate source. (ex: 'body')
    content : None or str or list
        The contents of the tag. It can either be None, a string, or a list
        of tags and strings. (i.e. a sub-ast)
    attributes : tuple of tuples or strings
        The attributes of the tag.
    local_context : dict
        The context with values for the current document. The values in this
        dict do not depend on values from other documents. (local)
    global_context : dict
        The context with values for all documents in a project. The
        `global_context` is constructed with the `src_filepath` as a key and
        the `local_context` as a value.

    Attributes
    ----------
    aliases : list of str
        A list of strs for other names a tag goes by
    html_name : str
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    tex_name : str
        If specified, use this name when rendering the tag to tex. Otherwise,
        use name.
    active : bool
        If True, the Tag can be used by the TagFactory.
    include_paragraphs : bool
        If True, then the contents of this tag can include paragraphs.
        See :func:`disseminate.ast.process_paragraphs`.
    line_number : int or None
        The corresponding starting line number in the source file for the
        tag. This is useful for error messages and it is set when the AST is
        processed.
    """

    name = None
    content = None
    attributes = None
    local_context = None
    global_context = None

    aliases = None
    html_name = None
    tex_name = None

    active = False
    include_paragraphs = False
    line_number = None

    def __init__(self, name, content, attributes, local_context,
                 global_context):
        self.name = name

        # Parse the attributes
        if isinstance(attributes, str):
            self.attributes = parse_attributes(attributes)
        elif isinstance(attributes, list) or isinstance(attributes, tuple):
            self.attributes = attributes
        else:
            self.attributes = tuple()

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

    def default(self):
        """Convert the tag to a text string.

        Strips the tag information and simply return the content of the tag.

        Returns
        -------
        text_string : str
            A text string with the tags stripped.
        """
        if isinstance(self.content, list):
            items = [i.default() if hasattr(i, 'default') else i
                            for i in self.content]
            items = filter(bool, items)
            return "".join(items)
        else:
            return self.content

    def tex(self, level=1):
        # Collect the content elements
        if isinstance(self.content, list):
            elements = ''.join([i.tex(level + 1) if hasattr(i, 'tex') else i
                                for i in self.content])
        elif isinstance(self.content, str):
            elements = self.content
        elif isinstance(self.content, Tag):
            elements = self.content.tex(level+1)
        else:
            msg = "Tag element '{}' of type '{}' cannot be rendered."
            raise(TagError(msg.format(self.content, type(self.content))))

        # Construct the tag name
        if level > 1:
            name = (self.tex_name if self.tex_name is not None else
                    self.name.lower())
        else:
            name = ''

        # Filter and prepare the attributes
        attrs = self.attributes if self.attributes else []
        if self.name in settings.tex_valid_attributes:
            valid_attrs = settings.tex_valid_attributes[self.name]
            attrs = filter_attributes(attrs=attrs,
                                      attribute_names=valid_attrs,
                                      target='.tex')
        else:
            attrs = filter_attributes(attrs=attrs,
                                      target='.tex')
        attrs_str = format_tex_attributes(attrs)

        # Format the tag. It's either a macro or environment
        if name in settings.tex_macros:
            # ex: \section{First}
            return ("\\" + name + attrs_str + '{' + elements + '}')
        elif name in settings.tex_commands:
            # ex: \item
            return "\\" + name + ' ' + elements + "\n"
        elif name in settings.tex_environments:
            # ex: \begin{align}
            return ("\n\\begin" + attrs_str + "{" + name + "}\n" +
                    elements +
                    "\\end{" + name + "}\n")
        else:
            return elements

    def html(self, level=1):
        """Convert the tag to an html string or html element.

        Returns
        -------
        html : str or html element
            A string in HTML format or an HTML element (:obj:`lxml.builder.E`).
        """
        # Collect the content elements
        if isinstance(self.content, list):
            elements = [i.html(level + 1) if hasattr(i, 'html') else i
                        for i in self.content]
        elif isinstance(self.content, str):
            elements = self.content
        elif isinstance(self.content, Tag):
            elements = [self.content.html(level+1)]
        else:
            msg = "Tag element '{}' of type '{}' cannot be rendered."
            raise (TagError(msg.format(self.content, type(self.content))))

        # Construct the tag name
        if level > 1:
            name = (self.html_name if self.html_name is not None else
                    self.name.lower())

        else:
            name = settings.html_root_tag

        # Filter and prepare the attributes
        attrs = self.attributes if self.attributes else []

        if name in settings.html_valid_attributes:
            valid_attrs = settings.html_valid_attributes[name]
            attrs = filter_attributes(attrs=attrs,
                                      attribute_names=valid_attrs,
                                      target='.html')
        else:
            attrs = filter_attributes(attrs=attrs,
                                      target='.html')

        if name in settings.html_valid_tags:
            kwargs = kwargs_attributes(attrs)
            e = (E(name, *elements, **kwargs) if elements else
                 E(name, **kwargs))
        else:
            # Create a span element if it not an allowed element
            # Add the tag type to the class attribute
            attrs = set_attribute(attrs, ('class', name), 'a')

            kwargs = kwargs_attributes(attrs)
            e = (E('span', *elements, **kwargs) if len(elements) else
                 E('span', **kwargs))

        # Render the root tag if this is the first level
        if level == 1:
            return (etree
                    .tostring(e, pretty_print=settings.html_pretty)
                    .decode("utf-8"))
        else:
            return e
