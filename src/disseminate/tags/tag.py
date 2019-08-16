"""
Core classes and functions for tags.
"""
from .exceptions import TagError
from .processors import ProcessTag
from ..formats import tex_env, tex_cmd, html_tag
from ..attributes import Attributes
from .utils import format_content, replace_context, copy_tag
from ..utils.string import titlelize, convert_camelcase
from ..utils.classes import weakattr


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
        The context with values for the document. The tag holds a weak reference
        to the context, as it doesn't own the context.

    Attributes
    ----------
    aliases : Tuple[str]
        A tuple of strings for other names a tag goes by
    html_name : str
        If specified, use this name for the html tag. Otherwise, use name.
    tex_cmd : str
        If specified, use this name to render the tex command.
    tex_env : str
        If specified, use this name to render the tex environment.
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

    html_name = None
    tex_env = None
    tex_cmd = None

    active = False

    process_content = True
    process_typography = True

    include_paragraphs = True
    paragraph_role = None

    def __init__(self, name, content, attributes, context):
        self.name = name
        self.attributes = Attributes(attributes)
        self.content = content
        self.context = context

        # Process the content
        self.process()

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

    @property
    def mtime(self):
        """The last modification time of this tag's (and subtag) document and
        for the documents of all labels referenced by this tag."""
        # Get the latest mtime for this label and all sub-labels
        flattened_list = self.flatten(filter_tags=True)

        mtimes = [tag.context.get('mtime', None)
                  for tag in flattened_list if hasattr(tag, 'context')]
        mtimes += [self.context.get('mtime', None)]

        # Remove None values from mtimes
        mtimes = list(filter(bool, mtimes))

        # The mtime is the latest mtime of all the tags and labels
        return max(mtimes)

    def process(self, names=None):
        """Process the tag's contents."""
        # Retrieve the ProcessTag subclasses and process the tag
        processors = self.processors(names)
        for processor in processors:
            processor(tag=self)

    def processors(self, names=None):
        """Retrieve a (filtered) list of tag processors.

        Parameters
        ----------
        names : Optional[Union[str, List[str], Tuple[str]]
            If specified, only return tag processors matching these name(s)
        """
        # wrap names into a list, if needed
        names = [names] if isinstance(names, str) else None

        # Get all of the tag processors, convert their class names to lower
        # case with underscores (ex: ProcessContent bcomes 'process_content'
        if names is not None:
            # Filter based on the specified names
            return [processor
                    for processor in ProcessTag.processors(tag_base_cls=Tag)
                    if convert_camelcase(processor.__class__.__name__) in names]
        else:
            # Filter based on the class's attributes. By default, return
            # all processors unless an class attribute is set to False for the
            # processor. ex: if the class or instance has a 'process_context'
            # attribute set to False, then the ProcessContent processor will
            # not be included.
            return [processor
                    for processor in ProcessTag.processors(tag_base_cls=Tag)
                    if getattr(self,
                               convert_camelcase(processor.__class__.__name__),
                               True)]

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

    def default_fmt(self, content=None):
        """Convert the tag to a text string.

        Strips the tag information and simply return the content of the tag.

        Parameters
        ----------
        content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
            <.Tag>`]]]
            Specify an alternative content from the tag's content. It can
            either be a string, a tag or a list of strings, tags and lists.

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

    def tex_fmt(self, content=None, mathmode=False, level=1):
        """Format the tag in LaTeX format.

        Parameters
        ----------
        content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
            <.Tag>`]]]
            Specify an alternative content from the tag's content. It can
            either be a string, a tag or a list of strings, tags and lists.
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
        content = content if content is not None else self.content

        # Collect the content elements
        content = format_content(content=content, format_func='tex_fmt',
                                 level=level + 1, mathmode=mathmode)
        content = ''.join(content) if isinstance(content, list) else content

        if self.tex_cmd:
            return tex_cmd(cmd=self.tex_cmd, attributes=self.attributes,
                           formatted_content=content)
        elif self.tex_env:
            return tex_env(env=self.tex_env, attributes=self.attributes,
                           formatted_content=content)
        else:
            return content

    @property
    def html(self):
        return self.html_fmt()

    def html_fmt(self, content=None, level=1):
        """Convert the tag to an html string or html element.

        Parameters
        ----------
        content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
            <.Tag>`]]]
            Specify an alternative content from the tag's content. It can
            either be a string, a tag or a list of strings, tags and lists.
        level : Optional[int]
            The level of the tag.

        Returns
        -------
        html : str or html element
            A string in HTML format or an HTML element (:obj:`lxml.builder.E`).
        """
        name = (self.html_name if self.html_name is not None else
                self.name.lower())

        content = content if content is not None else self.content

        # Collect the content elements
        content = format_content(content=content, format_func='html_fmt',
                                 level=level + 1)

        # Format the html tag
        return html_tag(name=name, level=level, attributes=self.attributes,
                        formatted_content=content)
