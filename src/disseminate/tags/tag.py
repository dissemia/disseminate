"""
Core classes and functions for tags.
"""
from .exceptions import TagError
from .signals import tag_created
from ..formats import tex_env, tex_cmd, xhtml_tag
from ..attributes import Attributes
from .utils import format_content, replace_context, copy_tag
from ..utils.string import titlelize
from ..utils.classes import weakattr, all_subclasses


class Tag(object):
    """A tag to format text in the markup document.

    Parameters
    ----------
    name : str
        The name of the tag as used in the disseminate source. (ex: 'body')
    content : Union[str, List[Union[str, list, :obj:`Tag \
        <disseminate.tags.tag.Tag>`], :obj:`Tag <disseminate.tags.tag.Tag>`]
        The contents of the tag. It can either be a string, a tag or a list
        of strings, tags and lists.
    attributes : Union[str, :obj:`Attributes \
        <disseminate.attributes.Attributes>`]
        The attributes of the tag. These are distinct from the Tag class
        attributes; they're the customization attributes specified by the user
        to change the appearance of a rendered tag. However, some or all
        attributes may be used as tag attributes, depending on the
        settings.html_valid_attributes, settings.tex_valid_attributes and so
        on.
    context : :obj:`Type[BaseContext] <.BaseContext>`
        The context with values for the document. The tag holds a weak
        reference to the context, as it doesn't own the context.

    Attributes
    ----------
    aliases : Tuple[str]
        A tuple of strings for other names a tag goes by
    hash : Optional[str]
        The hash for the tag's contents before processing. This is useful for
        detecting changes in the string's contents.
    html_name : str
        If specified, use this name for the html tag. Otherwise, use name.
    tex_cmd : str
        If specified, use this name to render the tex command.
    tex_env : str
        If specified, use this name to render the tex environment.
    tex_paragraph_newlines : bool
        If True (default), block tags within paragraphs will be typeset with
        a newline before and after. This is disable, for example, for
        equations.
    active : bool
        If True, the Tag can be used by the TagFactory.
    process_content : bool
        If True, the contents of the tag will be parsed and processed into a
        tag tree (AST) by the ProcessContent processor on creation.
    process_typography : bool
        If True, the strings in contents of the tag will be parsed and
        processed for typography characters by the ProcessTypography processor
        on creation.
    include_paragraphs : bool
        If True, then the contents of this tag can be included in paragraphs.
        See :func:`disseminate.tags.processors.process_paragraphs`.
    paragraph_role : str
        If this tag is directly within a paragraph, the type of paragraph may
        be specified with a string. The following options are possible:

        - None : The paragraph type has not been assigned
        - 'inline' : The tag is within a paragraph that includes a mix
          of strings and tags
        - 'block' : The tag is within its own paragraph.
    """

    name = None
    content = None
    attributes = None
    context = weakattr()

    aliases = None
    hash = None

    html_name = None
    tex_cmd = None
    tex_env = None
    tex_paragraph_newlines = True

    active = False

    process_macros = True
    process_content = True
    process_typography = True
    include_paragraphs = True
    paragraph_role = None

    def __init__(self, name, content, attributes, context):
        self.name = name
        self.attributes = Attributes(attributes)
        self.content = content
        self.context = context

        # Emit the tag creation signal
        tag_created.emit(tag=self, tag_base_cls=Tag, tag_factory=TagFactory)

    def __repr__(self):
        return "{type}{{{content}}}".format(type=self.name,
                                            content=self.content)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.attributes == other.attributes and
                self.content == other.content and
                id(self.context) == id(other.context))

    def __getitem__(self, item):
        """Index accession."""
        if not isinstance(self.content, list):
            msg = ("Cannot access sub-tree for tag {} because "
                   "tag contents are not a list")
            raise TagError(msg.format(self.__repr__()))
        return self.content[item]

    def __len__(self):
        if isinstance(self.content, list) or isinstance(self.content, tuple):
            return len(self.content)
        else:
            return 1

    @property
    def title(self):
        """A title string converted from the content"""
        # Get the string for the content. The parent default function is called
        # to prevent recursion problems from child default methods calling
        # title.
        string = Tag.default_fmt(self)
        return titlelize(string)

    @property
    def short(self):
        """The short title for the tag"""
        short_attr = self.attributes.get('short', None)
        return short_attr if short_attr is not None else self.title

    def copy(self, new_context=None):
        """Create a copy of this tag and all sub-tabs.

        The tag copy is a deep copy of the attributes and content, but the
        context is either kept the same or replaced with the specified
        new_context.

        Parameters
        ----------
        new_context : Optional[:obj:`Type[BaseContext] <.context.BaseContext>`]
            The new context to replace, if specified.
        """
        # Copy the tag
        cp = copy_tag(tag=self)

        # Set the new context
        if new_context is not None:
            replace_context(tag=cp, new_context=new_context)
        return cp

    def flatten(self, tag=None, filter_tags=True):
        """Generate a flat list with this tag and all sub-tags and elements.

        Parameters
        ----------
        tag : Optional[:obj:`Tag <.Tag>`]
            If specified, flatten the given tag, instead of this tag.
        filter_tags : Optional[bool]
            If True, only return a list of tag objects. Otherwise, include all
            content items, including strings and lists.

        Returns
        -------
        flattened_list : List[Union[str, :obj:`Tag <.Tag>`]]
            The flattened list.
        """
        tag = tag if tag is not None else self
        flattened_list = [tag]  # add the given tag to the list

        # Process the tag's contents if present
        if hasattr(tag, 'content'):
            tag = tag.content

        # Convert the AST to a list, if it isn't already
        if not hasattr(tag, '__iter__'):
            tag = [tag]

        # Traverse the items and process each
        for item in tag:
            # Add the item to the ast
            flattened_list.append(item)

            # Process tag's sub tags or lists, if present
            if (hasattr(item, 'content') and
                (isinstance(item.content, list) or
                 isinstance(item.content, Tag))):
                flattened_list += self.flatten(tag=item.content,
                                               filter_tags=filter_tags)

        if filter_tags:
            flattened_list = [t for t in flattened_list if isinstance(t, Tag)]
        return flattened_list

    @property
    def default(self):
        return self.default_fmt()

    @property
    def txt(self):
        return self.default_fmt()

    def default_fmt(self, content=None, attributes=None):
        """Convert the tag to a text string.

        Strips the tag information and simply return the content of the tag.

        Parameters
        ----------
        content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
            <.Tag>`]]]
            Specify an alternative content from the tag's content. It can
            either be a string, a tag or a list of strings, tags and lists.
        attributes : Optional[Union[str, :obj:`Attributes <.Attributes>`]]
            Specify an alternative attributes dict from the tag's attributes.
            It can either be a string or an attributes dict.

        Returns
        -------
        text_string : str
            A text string with the tags stripped.
        """
        content = content if content is not None else self.content
        content = format_content(content=content, format_func='default_fmt')
        return ''.join(content) if isinstance(content, list) else content

    @property
    def tex(self):
        return self.tex_fmt()

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        """Format the tag in LaTeX format.

        Parameters
        ----------
        content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
            <.Tag>`]]]
            Specify an alternative content from the tag's content. It can
            either be a string, a tag or a list of strings, tags and lists.
        attributes : Optional[Union[str, :obj:`Attributes <.Attributes>`]]
            Specify an alternative attributes dict from the tag's attributes.
            It can either be a string or an attributes dict.
        mathmode : Optional[bool]
            If True, the tag will be rendered in math mode. Otherwise (default)
            latex text mode is assumed.
        level : Optional[int]
            The level of the tag.

        Returns
        -------
        tex_string : str
            The formatted tex string.
        """
        # Collect the content elements
        content = content if content is not None else self.content
        content = format_content(content=content, format_func='tex_fmt',
                                 level=level + 1, mathmode=mathmode)
        content = ''.join(content) if isinstance(content, list) else content

        # Set the attributes
        attributes = self.attributes if attributes is None else attributes

        if self.tex_cmd:
            return tex_cmd(cmd=self.tex_cmd, attributes=attributes,
                           formatted_content=content)
        elif self.tex_env:
            return tex_env(env=self.tex_env, attributes=attributes,
                           formatted_content=content)
        else:
            return content

    @property
    def html(self):
        return self.html_fmt()

    def html_fmt(self, content=None, attributes=None, format_func='html_fmt',
                 method='html', level=1):
        """Convert the tag to an html string or html element.

        Parameters
        ----------
        content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
            <.Tag>`]]]
            Specify an alternative content from the tag's content. It can
            either be a string, a tag or a list of strings, tags and lists.
        attributes : Optional[Union[str, :obj:`Attributes <.Attributes>`]]
            Specify an alternative attributes dict from the tag's attributes.
            It can either be a string or an attributes dict.
        format_func : Optional[str]
            The format function to use with by formatted_content when
            formatting sub-tags.
        method : Optional[str]
            The rendering method for the string. ex: 'html' or 'xml'
        level : Optional[int]
            The level of the tag.

        Returns
        -------
        html : str or html element
            A string in HTML format or an HTML element (:obj:`lxml.builder.E`).
        """
        name = (self.html_name if self.html_name is not None else
                self.name.lower())

        # Collect the content elements
        content = content if content is not None else self.content
        content = format_content(content=content, format_func=format_func,
                                 level=level + 1)

        # Set the attributes
        attributes = attributes or self.attributes

        # Format the html tag
        return xhtml_tag(name=name, level=level, attributes=attributes,
                         formatted_content=content, method=method)

    @property
    def xhtml(self):
        return self.xhtml_fmt()

    def xhtml_fmt(self, method='xhtml', format_func='xhtml_fmt', **kwargs):
        """Convert the tag to an xhtml string or html element.

        Returns
        -------
        xhtml : str or xhtml element
            A string in XHTML format or an XHTML element (
            :obj:`lxml.builder.E`).
        """
        return self.html_fmt(method=method, format_func=format_func,
                             **kwargs)


class TagFactory(object):
    """Generates the appropriate tag for a given tag type.

    The tag factory instantiates tags based on loaded modules and
    initialization parameters.

    Parameters
    ----------
    tag_base_cls : :class:`Tag <disseminate.tags.tag.Tag>`
        The base class for Tag objects.
    """

    _tag_classes = None

    @classmethod
    def tag(cls, tag_name, tag_content, tag_attributes, context):
        """Return the approriate tag, given a tag_name and tag_content.

        A tag subclass, rather than the Tag base class, will be returned if

        - A tag subclass with the tag_name (or with an alias) is available.
        - The tag subclass has an 'active' attribute that is True
        - The tag's name isn't listed in the 'inactive_tags' set in the
          context.

        Parameters
        ----------
        tag_name : str
            The name of the tag. ex: 'bold', 'b'
        tag_content : Union[str, list]
            The content of the tag. ex: 'this is bold'
        tag_attributes : str
            The attributes of a tag. ex: 'width=32pt'
        context : :obj:`.document.DocumentContext`
            The document's context.

        Returns
        -------
        tag : :obj:`Tag <disseminate.tags.Tag>`
            An instance of a Tag subclass.
        """
        tag_cls = cls.tag_class(tag_name=tag_name, context=context)

        # Create the tag
        tag = tag_cls(name=tag_name, content=tag_content,
                      attributes=tag_attributes, context=context)
        return tag

    @classmethod
    def tag_class(cls, tag_name, context):
        """Retrieve the tag class for the given tag_name"""
        tag_classes = cls.tag_classes
        tag_name_lower = tag_name.lower()
        tag_cls = tag_classes().get(tag_name_lower, None)

        if (tag_cls is not None and
            getattr(tag_cls, 'active', False) and
           tag_cls.__name__.lower() not in context.get('inactive_tags', ())):
            # First, see if the tag_name matches one of the tag subclasses (or
            # tag aliases) in disseminate
            return tag_cls
        else:
            # If all else fails, just make a generic Tag.
            return Tag

    @classmethod
    def tag_classes(cls):
        """A dict of all the active Tag subclasses."""
        if cls._tag_classes is None:
            tag_classes = dict()

            for scls in all_subclasses(Tag):
                # Collect the name and aliases (alternative names) for the tag
                aliases = (list(scls.aliases) if scls.aliases is not None else
                           list())
                names = [scls.__name__.lower(), ] + aliases

                for name in names:
                    # duplicate or overwritten tag names are not allowed
                    assert name not in tag_classes
                    tag_classes[name] = scls

            cls._tag_classes = tag_classes

        return cls._tag_classes
