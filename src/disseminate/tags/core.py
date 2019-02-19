"""
Core classes and functions for tags.
"""
from lxml.builder import E
from lxml import etree
from markupsafe import Markup

from .exceptions import TagError
from ..attributes import (parse_attributes, set_attribute,
                          kwargs_attributes, format_tex_attributes,
                          filter_attributes, get_attribute_value,
                          remove_attribute)
from .utils import set_html_tag_attributes
from ..utils.string import titlelize
from ..utils.classes import all_subclasses
from ..utils.string import StringTemplate
from .. import ast
from .. import settings



class TagFactory(object):
    """Generates the appropriate tag for a given tag type.
    """

    tag_types = None

    def __init__(self):
        # Lazy initialization of the class. The tags can be cached because
        # the source code is assumed static once the program has started.
        if TagFactory.tag_types is None:
            # Initialize the tag types dict.
            TagFactory.tag_types = dict()
            for scls in all_subclasses(Tag):
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
                    TagFactory.tag_types[name] = scls

    def tag(self, tag_name, tag_content, tag_attributes, context):
        """Return the approriate tag, give a tag_type and tag_content"""

        # Try to find the appropriate subclass
        small_tag_type = tag_name.lower()
        if small_tag_type in self.tag_types:
            cls = self.tag_types[small_tag_type]
        else:
            cls = Tag

        tag = cls(name=tag_name, content=tag_content, attributes=tag_attributes,
                  context=context)
        return tag


class Tag(object):
    """A tag to format text in the markup document.

    .. note:: Tags are created asynchroneously, so the creation of a tag
              should not depend on the `context`. These will only be partially
              populated at creation time. The target specific methods
              (html, tex, ...), by contrast, may depend on the context
              attributes populated by other tags.

    Parameters
    ----------
    name : str
        The name of the tag as used in the disseminate source. (ex: 'body')
    content : None or str or list
        The contents of the tag. It can either be None, a string, or a list
        of tags and strings. (i.e. a sub-ast)
    attributes : tuple of tuples or strings
        The attributes of the tag. These are distinct from the Tag class
        attributes; they're the customization attributes specified by the user
        to change the appearance of a rendered tag.
    context : dict
        The context with values for the document.

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
    label_id : str or None
        If specified, this is the id for a label that is used by this tag.
        (See :meth:`set_label` for creating a label at the same time)
    """

    name = None
    content = None
    attributes = None
    context = None

    aliases = None
    html_name = None
    tex_name = None

    active = False
    include_paragraphs = False
    line_number = None

    label_id = None

    def __init__(self, name, content, attributes, context):
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

        self.context = context

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
        short_attr = self.get_attribute('short')
        return short_attr if short_attr is not None else self.title

    @property
    def mtime(self):
        """The last modification time of this tag's (and subtag) document and
        for the documents of all labels reference by this tag."""
        # All tags and sub-tags have the same mtime, which is stored in the
        # context
        mtimes = [self.context.get('mtime', None)]

        # Get the labels and their mtimes. Some of the tags may reference other
        # documents with later mtimes, so this will fetch those mtimes.
        if 'label_manager' in self.context:
            label_manager = self.context['label_manager']

            # Get all the labels referenced by this tag (and sub-tags) and find
            # their mtimes.
            flattened_list = self.flatten(filter_tags=True)
            label_ids = {t.label_id for t in flattened_list
                         if hasattr(t, 'label_id') if t.label_id is not None}

            labels = [l for l in label_manager.labels if l.id in label_ids]
            mtimes += [l.mtime for l in labels]

        # Remove None values from mtimes
        mtimes = list(filter(bool, mtimes))

        # The mtime is the latest mtime of all the tags and labels
        return max(mtimes)

    def get_attribute(self, name, target=None, clear=False):
        """Retrieve an attribute from the tag and optionally clear it from
        the list of attributes.

        Parameters
        ----------
        name : str
            The attribute's name.
        target : str, optional
            The (optional) target for target-specific attributes.
        clear : bool, optional
            If True, the attribute will be removed from the attribute listing
            for the tag. By default, the attribute is not cleared.

        Returns
        -------
        attribute_value : str or None
            The value of the attribute, if the attribute was found, or None,
            if the attribute was not found.
        """
        value = get_attribute_value(attrs=self.attributes, attribute_name=name,
                                    target=target)
        if clear:
            self.attributes = remove_attribute(attrs=self.attributes,
                                               attribute_name=name)
        return value

    @property
    def label(self):
        if self.label_id is not None and 'label_manager' in self.context:
            label_manager = self.context['label_manager']
            return label_manager.get_label(id=self.label_id)
        return None

    def set_label(self, id, kind, title=None):
        """Create and set a label for the tag.

        If a reference to an existing label is desired, rather than creating
        a label, set the 'label_id' attribute.

        Parameters
        ----------
        id : str or None
            The (unique) identifier of the label. ex: 'nmr_introduction'.
            If None is given, the label cannot be referenced; it is used for
            counting only.
        kind : tuple or None
            The kind of the label is a tuple that identified the kind of a label
            from least specific to most specific. ex: ('figure',), ('chapter',),
            ('equation',), ('heading', 'h1',)

            This function is used to add a reference to a label by the tag.
        title : str, optional
            The (optional) title string for the content label.
        """
        assert id is not None

        document = (self.context['document']() if 'document' in self.context
                    else None)
        title = self.title if title is None else title

        if 'label_manager' in self.context and document is not None:
            label_manager = self.context['label_manager']

            # Create the label
            label_manager.add_content_label(id=id, kind=kind, title=title,
                                            context=self.context)
            self.label_id = id

    def get_label_tag(self, target=None):
        """Create a new formatted tag for the label associated with this tag.

        Parameters
        ----------
        target : str, optional
            The optional target for the label's format string.

        Returns
        -------
        label_tag : :obj:`disseminate.tags.Tag`
            The formatted tag for this tag's label.
        """
        # Get the tag's label
        label = self.label

        # Get the format string for the label, either from this tag's
        # attributes, this tag's context or the default context.
        label_fmt = self._get_label_fmt_str(target=target)

        # Convert the label_fmt string to a string template
        label_tmplt = StringTemplate(label_fmt)

        # A label format string has been found. Now format it.
        label_string = label_tmplt.substitute(label=label)

        # Format any tags
        label_tag = ast.process_ast(label_string, context=self.context)
        label_tag.name = 'label'  # convert tag name from 'root' to 'label'
        return label_tag

    def _get_label_fmt_str(self, tag_name=None, target=None):
        """Get the format string for this tag's label from the tag's attributes,
        the tag's context, or the default context (in that order).

        Parameters
        ----------
        tag_name : str, optional
            The name of the tag to use in retrieving the label format string.
            If not specified, then this tag's class name will be used.
        target : str, optional
            The optional target for the label's format string.

        Returns
        -------
        format_string : str
            The corresponding format string for the label. This is a string
            with replaceable fields that are formatted with the 'format'
            function.
        """
        # First, see if a label format was specified in the tag directly
        label_fmt = (self.get_attribute('fmt', target=target) or
                     self.get_attribute('fmt', target=None))

        if label_fmt is not None:
            return label_fmt

        # If not, get the label format string from the context. This is done
        # by searching the 'label_fmts' dict in the context for a key that
        # matches this tag's type (ex: 'caption') and the kinds of the label,
        # (ex: ('figure') as well as possibly the target type (ex: .html). The
        label = self.label

        if label is not None:
            # Search the label format string (label_fmt) in decreasing order
            # of specificity for the key. ex:
            # From major: 'caption', intermediate: 'figure', target: 'html'
            #    1. caption_figure_html
            #    2. caption_figure
            #    3. caption_html
            #    4. caption
            major = (tag_name if tag_name is not None else
                     self.__class__.__name__.lower())
            intermediate = [kind for kind in label.kind if kind != major]

            return self.context.label_fmt(major=major,
                                          intermediate=intermediate,
                                          target=target)

        return ''

    def flatten(self, tag=None, filter_tags=True):
        """Generate a flat list with this tag and all sub-tags and elements.

        Parameters
        ----------
        tag : :obj:`Tag`, optional
            If specified, flatten the given tag, instead of this tag.
        filter_tags : bool, optional
            If True, only return a list of tag objects. Otherwise, include all
            content items, including strings and lists.

        Returns
        -------
        flattened_list : list of tags or list of tags or str or list
            The flattened list.
        """
        tag = tag if tag is not None else self
        flattened_list = [tag]

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

            # Process tag's sub-items, if present
            if hasattr(item, 'content') and isinstance(item.content, list):
                # Process lists recursively
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
        content : list or str or Tag, optional
            If specified, render the given content. Otherwise, use this tag's
            content.

        Returns
        -------
        text_string : str
            A text string with the tags stripped.
        """
        content = content if content is not None else self.content
        if isinstance(content, list):
            items = [i.default_fmt() if hasattr(i, 'default_fmt') else i
                            for i in content]
            items = filter(bool, items)
            return "".join(items)
        elif isinstance(content, Tag):
            return content.default_fmt()
        else:
            # strings and other types of content
            return content

    @property
    def tex(self):
        return self.tex_fmt()

    def tex_fmt(self, level=1, mathmode=False, content=None):
        """Format the tag in latex format.

        Parameters
        ----------
        level : int, optional
            The level of the tag.
        mathmode : bool, optional
            If True, the tag will be rendered in math mode. Otherwise (default)
            latex text mode is assumed.
        content : list or str or Tag, optional
            If specified, render the given content. Otherwise, use this tag's
            content.

        Returns
        -------
        tex_string : str
            The formatted tex string.
        """
        content = content if content is not None else self.content
        # Collect the content elements
        if isinstance(content, list):
            elements = ''.join([i.tex_fmt(level + 1, mathmode)
                                if hasattr(i, 'tex_fmt') else i
                                for i in content])
        elif isinstance(content, str):
            elements = content
        elif isinstance(content, Tag):
            elements = content.tex_fmt(level+1)
        else:
            msg = "Tag element '{}' of type '{}' cannot be rendered."
            raise(TagError(msg.format(content, type(content))))

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
            return "\\" + name + attrs_str + '{' + elements + '}'
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

    @property
    def html(self):
        return self.html_fmt()

    def html_fmt(self, level=1, content=None):
        """Convert the tag to an html string or html element.

        Parameters
        ----------
        level : int, optional
            The level of the tag.
        content : list or str or Tag, optional
            If specified, render the given content. Otherwise, use this tag's
            content.

        Returns
        -------
        html : str or html element
            A string in HTML format or an HTML element (:obj:`lxml.builder.E`).
        """
        content = content if content is not None else self.content
        # Collect the content elements
        if isinstance(content, list):
            elements = [i.html_fmt(level + 1) if hasattr(i, 'html_fmt') else i
                        for i in content]
        elif isinstance(content, str):
            elements = content
        elif isinstance(content, Tag):
            elements = [content.html_fmt(level+1)]
        else:
            msg = "Tag element '{}' of type '{}' cannot be rendered."
            raise (TagError(msg.format(content, type(content))))

        # Construct the tag name
        name = (self.html_name if self.html_name is not None else
                self.name.lower())

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
            # Create the html tag
            e = E(name, *elements) if elements else E(name)

            # Set the attributes for the tag, in order.
            kwargs = kwargs_attributes(attrs)
            set_html_tag_attributes(html_tag=e, attrs_dict=kwargs)
        else:
            # Create a span element if it not an allowed element
            # Add the tag type to the class attribute
            attrs = set_attribute(attrs, ('class', name), 'a')

            # Create the html tag
            e = E('span', *elements) if len(elements) else E('span')

            # Set the attributes for the tag, in order.
            kwargs = kwargs_attributes(attrs)
            set_html_tag_attributes(html_tag=e, attrs_dict=kwargs)

        # Render the root tag if this is the first level
        if level == 1:
            s = (etree.tostring(e, pretty_print=settings.html_pretty)
                      .decode("utf-8"))
            return Markup(s)  # Mark string as safe, since it's escaped by lxml
        else:
            return e
