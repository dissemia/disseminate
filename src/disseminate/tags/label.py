"""
The Label tag to reference captions and other labels.
"""
from .tag import Tag
from .utils import content_to_str
from .exceptions import assert_content_str
from .utils import format_content
from ..attributes import Attributes
from ..formats import xhtml_tag
from ..utils.string import titlelize, slugify
from ..utils.classes import weakattr


def generate_label_id(tag):
    """Generate a label_id string for the given tag.

    Parameters
    ----------
    tag : :obj:`Tag <.Tag>`
        The tag creating the label.

    Returns
    -------
    label_id : str
        The label id string for the tag.
    """
    assert tag.context.is_valid('doc_id')
    context = tag.context
    doc_id = context['doc_id']
    # Retrieve the tag attributes and content, and make sure they're in the
    # needed formats
    content = tag.content

    attributes = tag.attributes
    attributes = (Attributes(attributes) if isinstance(attributes, str)
                  else attributes)

    if 'id' in attributes:
        # If an 'id' was specified, just use that.
        return attributes['id']
    elif 'short' in attributes:
        # Convert the 'short' title to a title for the label and slugify to
        # remove spaces
        title = titlelize(attributes['short'])
        title = '-'.join((doc_id, title))
        return slugify(title)

    # Try to generate the label_id from the contents
    elif isinstance(content, str) and content.strip() == '':
        # The contents of the tag are empty. Make an automatically generated
        # label
        label_count = context.setdefault('label_count', 0) + 1
        context['label_count'] = label_count
        doc_id = slugify(context['doc_id'])

        return "-".join((doc_id, str(label_count)))
    else:
        # Convert the content to a title for the label and slugify to
        # remove spaces
        title = titlelize(content_to_str(content))
        title = '-'.join((doc_id, title))
        return slugify(title)


def create_label(tag, kind, label_id=None):
    """Create a label in the label_manager for the given tag.

    .. note:: This function does not create a :obj:`LabelTag
              <disseminate.tags.label.LabelTag>`. Only a :obj:`Label
              <disseminate.labels.labels.Label>` object through the document's
              :obj:<LabelManager
              <disseminate.labels.label_manager.LabelManager>`

    Parameters
    ----------
    tag : :obj:`Tag <disseminate.tags.tag.Tag>`
        The tag creating the label.
    kind : Tuple[str]
        The kind of label. ex: ('heading', 'section')
    label_id : Optional[str]
        The identifier for the label to create.
        If None is specified, the generate_label_id function will be used.

    Returns
    -------
    label_id : Union[str, None]
        The label_id of the created label, if successful.
        None if a label could not be created.
    """
    content = tag.content
    context = tag.context

    assert 'label_manager' in context, ("A label manager could not be found "
                                        "in the tag's context")

    # Generate the label_id, if needed
    label_id = label_id if label_id is not None else generate_label_id(tag=tag)

    # Get the tag's context and attributes
    attributes = tag.attributes
    attributes = (Attributes(attributes) if isinstance(attributes, str) else
                  attributes)

    # Form a title from the content
    if 'short' in attributes:
        content = attributes['short']
    else:
        content = titlelize(content_to_str(content))

    # Create the content label
    label_manager = context['label_manager']
    label_manager.add_content_label(id=label_id, kind=kind,
                                    title=content, context=context)
    return label_id


class LabelMixin(object):
    """A mixin class for working with LabelTags LabelAnchors.

    This mixing works in coordination with the :class:`Tag
    <disseminate.tags.tag.Tag>` base class. The constructor (__init__) of this
    class should be run after the Tag base class's constructor.
    """

    label_id = None
    label_tag = None
    label_anchor = None

    def __init__(self, *args, **kwargs):
        self.create_label()

    def generate_label_id(self):
        """Generate the label_id to use in creating the label.

        Override this function to customize the generation of the label_id.

        Returns
        -------
        label_id : str
            The generated label_id.
        """
        if 'id' in self.attributes:
            # Get the label_id from the attributes, if specified.
            return self.attributes['id']
        else:
            # No label id specified. Generate a label_id
            return generate_label_id(tag=self)

    def generate_label_kind(self):
        """Generate the kind tuple for the created label.

        Override this function to customize the generation of the label kind.

        Returns
        -------
        kind : Tuple[str]
            A tuple of strings for the kind of label.
            ex: ('heading', 'chapter')
        """
        return tuple()

    def create_label(self):
        """Create the label in the label_manager for this tag."""
        # Create the label. First,
        label_id = self.generate_label_id()
        kind = self.generate_label_kind()
        label_id = create_label(tag=self, kind=kind, label_id=label_id)

        # Add the label identifier to this tag's attributes. This will be
        # this tag's anchor for targets like html
        self.label_id = label_id
        self.attributes['id'] = label_id

        attrs = self.attributes.filter('id', 'class', 'short')
        context = self.context

        self.label_tag = LabelTag(name='label', attributes=attrs,
                                  content=label_id, context=context)
        self.label_anchor = LabelAnchor(name='label_anchor', attributes=attrs,
                                        content=label_id, context=context)


class LabelAnchor(Tag):
    """The label anchor."""

    name = 'label'
    tex_cmd = 'label'
    html_name = 'span'

    def __init__(self, *args, content, **kwargs):
        # Set the label_id from the content
        assert_content_str(content)
        label_id = content.strip()
        self.label_id = label_id

        super().__init__(*args, content=content, **kwargs)

    def html_fmt(self, method='html', level=1, **kwargs):
        # <span id="#label-id" />
        html_id = self.label_id
        return xhtml_tag('span', attributes='id=' + html_id, method=method,
                         level=level)


class LabelTag(Tag):
    """The name portion of a label.

    ex: Chap. 1.2 or Fig. 1.

    Parameters
    ----------
    content : str
        The label_id of an existing label.
    kind : Tuple[str]
        The kind of the label is a tuple that identified the kind of a label
        from least specific to most specific. ex: ('figure',), ('chapter',),
        ('equation',), ('heading', 'h1',)
        See :meth:`LabelManager.format_string
        <disseminate.labels.label_manager.LabelManager.format_string>`
    prepend_id : Optional[str]
        If specified, the label id (identifier) will have this string prepended
        to it.

    (see the :class:`Tag <disseminate.tags.tag.Tag>` base class for details
     on the other parameters)
    """

    # This tag should not be created by the tag factory; it should be created
    # by other tags.
    active = False

    label_id = None
    label_manager = weakattr()

    #: Do not convert typography characters. Conversion of typography
    #: characters might cause issues with matching the label id.
    process_content = False
    process_typography = False

    def __init__(self, name, attributes, content, context, **kwargs):
        # Set the label_id from the content
        assert_content_str(content)
        label_id = content.strip()
        self.label_id = label_id

        # Set the label_manager and get the format key
        if 'label_manager' in context:
            self.label_manager = context['label_manager']

        super().__init__(name=name, attributes=attributes,
                         content=content, context=context, **kwargs)

        # Clean up the attributes.
        # 1. Remove the 'id' attribute, since it will be included by the
        #    LabelAnchor
        if 'id' in self.attributes:
            del self.attributes['id']

    def default_fmt(self, content=None, attributes=None):
        # Get the label tag format
        label_manager = self.label_manager
        label_id = self.label_id
        context = self.context

        if all(i is not None for i in (label_manager, label_id, context)):
            format_str = label_manager.format_string(id=self.label_id)
            processed_tag = Tag(name='label', content=format_str,
                                attributes='', context=context)
            return content_to_str(processed_tag.content)
        else:
            return ''

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        # Get the label tag format
        label_manager = self.label_manager
        label_id = self.label_id
        context = self.context

        if all(i is not None for i in (label_manager, label_id, context)):
            format_str = label_manager.format_string(id=self.label_id,
                                                     target='.tex')

            # Process the tags and format the contents for tex
            processed_tag = Tag(name='label', content=format_str,
                                attributes='', context=context)
            content = format_content(content=processed_tag.content,
                                     format_func='tex_fmt', level=level + 1,
                                     mathmode=mathmode)
            return ''.join(content) if isinstance(content, list) else content
        else:
            return ''

    def html_fmt(self, content=None, attributes=None, format_func='html_fmt',
                 method='html', level=1, **kwargs):
        # Get the label tag format
        label_manager = self.label_manager
        label_id = self.label_id
        context = self.context

        if all(i is not None for i in (label_manager, label_id, context)):
            # Retrieve the format string for the label
            # Use the 'html' format_str for html and xhtml
            format_str = label_manager.format_string(id=self.label_id,
                                                     target='.html')

            # Process the tags and format the contents for html (html_fmt) or
            # xhtml (xhtml_fmt)
            processed_tag = Tag(name='label', content=format_str,
                                attributes='', context=context)
            content = format_content(content=processed_tag.content,
                                     format_func=format_func, level=level + 1)

            attributes = (self.attributes.copy()
                          if attributes is None else attributes)
            attributes['class'] = 'label'
            return xhtml_tag('span', attributes=attributes,
                             formatted_content=content, method=method,
                             level=level)
        else:
            return ''

    def xhtml_fmt(self, format_func='xhtml_fmt', method='xhtml', **kwargs):
        return self.html_fmt(format_func=format_func, method=method, **kwargs)
