"""
Tags for headings.
"""
from .tag import Tag
from .label import LabelTag, LabelAnchor, generate_label_id, create_label
from .utils import content_to_str
from ..formats import tex_cmd


toc_levels = ('title', 'part', 'chapter', 'section', 'subsection',
              'subsubsection')


class Heading(Tag):
    """A heading tag.

    .. note::
        If the content isn't specified and an entry exists in the context with
        the tag's name, then this tag's content will be replaced with the
        contents from the context.

    Tag Attributes
    --------------
    - nolabel: If specified, a label entry will not be created for this heading.
    """
    html_name = None
    tex_cmd = None

    active = True
    include_paragraphs = False

    label_id = None
    label_tag = None
    label_anchor = None

    id_mappings = {'title': 'title',
                   'part': 'part',
                   'chapter': 'ch',
                   'section': 'sec',
                   'subsection': 'subsec',
                   'subsubsection': 'subsubsec',
                    }

    def __init__(self, name, content, attributes, context):

        # If no content is specified, see if it's specified in the context
        if (isinstance(content, str) and content.strip() == '' and
           name in context):
            content = content_to_str(context[name])

        # Call the parent class's constructor
        super().__init__(name, content, attributes, context)

        # Determine whether a label should be given. By default, each heading
        # has a label
        if 'nolabel' not in self.attributes:
            cls_name = self.__class__.__name__.lower()
            kind = ('heading', cls_name)

            # Prepare the attributes for the Label tag.
            attrs = self.attributes.filter('id', 'short')
            attrs['class'] = 'heading'

            # Create the label. First,
            if 'id' in self.attributes:
                # Get the label_id from the attributes, if specified.
                label_id = self.attributes['id']
            else:
                # No label id specified. Generate a label_id and prepend the
                # label type, if an id is not explicitly specified.
                # ex: 'title' -> 'ch:title'
                label_id = generate_label_id(tag=self)
                label_id = ":".join((Heading.id_mappings[cls_name], label_id))

            label_id = create_label(tag=self, kind=kind, label_id=label_id)

            # Add the label identifier to this tag's attributes. This will be
            # this tag's anchor for targets like html
            self.label_id = label_id
            self.attributes['id'] = label_id

            self.label_tag = LabelTag(name='label', attributes=attrs,
                                      content=label_id, context=context)
            self.label_anchor = LabelAnchor(name='label_anchor',
                                            attributes=attrs, content=label_id,
                                            context=context)

    def default_fmt(self, content=None):
        # Prepare the content with the label. References for the default format
        # are not supported
        content = ''
        if self.label_tag is not None:
            content += self.label_tag.default_fmt()
        content += content_to_str(self.content)

        return super().default_fmt(content=content)

    def tex_fmt(self, content=None, mathmode=False, level=1):
        cls_name = self.__class__.__name__.lower()
        content = ''

        # Prepare the tag contents to include the label tag.
        # ex: 'My Title' becomes 'Chap 1. My Title'
        if self.label_tag is not None:
            content += self.label_tag.tex_fmt(mathmode=mathmode,
                                              level=level + 1)
        content += self.content

        # Format the heading tag. ex: \chapter{Chapter 1. My First Chapter}
        content = tex_cmd(cls_name, attributes=self.attributes,
                          formatted_content=content)

        # Get the label for this heading to get its number, if available
        if self.label_id is not None and self.label_anchor is not None:
            assert self.context.is_valid('label_manager')

            label_manager = self.context['label_manager']
            label = label_manager.get_label(id=self.label_id)

            number = label.global_order[-1] if label.global_order else None
            attrs = ' '.join((cls_name, str(number)))

            content = (tex_cmd('setcounter', attributes=attrs) + '\n' +
                       content + ' ' +
                       self.label_anchor.tex_fmt(mathmode=mathmode,
                                                 level=level + 1))

        return content

    def html_fmt(self, content=None, level=1):
        # Prepare the tag contents to include the label tag.
        # ex: 'My Title' becomes 'Chap 1. My Title'
        content = []
        if self.label_tag is not None:
            content.append(self.label_tag)

        if isinstance(self.content, list):
            content += self.content
        else:
            content.append(self.content)

        return super().html_fmt(content=content, level=level)


class Title(Heading):
    aliases = ("h1",)
    html_name = "h1"
    tex_cmd = "title"
    active = True
    include_paragraphs = False


class Part(Heading):
    html_name = "h1"
    tex_cmd = "part"
    active = True
    include_paragraphs = False


class Chapter(Heading):
    aliases = ("h2",)
    html_name = "h2"
    tex_cmd = "chapter"
    active = True
    include_paragraphs = False


class Section(Heading):
    """A section heading tag."""
    aliases = ("h3", )
    html_name = "h3"
    tex_cmd = "section"
    active = True
    include_paragraphs = False


class SubSection(Heading):
    """A subsection heading tag."""
    aliases = ("h4",)
    html_name = "h4"
    tex_cmd = "subsection"
    active = True
    include_paragraphs = False


class SubSubSection(Heading):
    """A subsubsection heading tag."""
    aliases = ("h5",)
    html_name = "h5"
    tex_cmd = "subsubsection"
    active = True
    include_paragraphs = False


class Para(Tag):
    """A paragraph heading tag."""
    aliases = ("h6",)

    html_name = "paragraph-heading"
    tex_cmd = "paragraph"
    active = True
    include_paragraphs = False

    label_heading = False
