"""
Tags for headings.
"""
from .tag import Tag
from .label import LabelMixin
from .utils import content_to_str
from ..formats import tex_cmd


toc_levels = ('title', 'part', 'chapter', 'section', 'subsection',
              'subsubsection')


class Heading(Tag, LabelMixin):
    """A heading tag.

    .. note::
        If the content isn't specified and an entry exists in the context with
        the tag's name, then this tag's content will be replaced with the
        contents from the context.
    """
    html_name = None
    tex_cmd = None

    active = False
    include_paragraphs = False

    id_mappings = {'title': 'title',
                   'part': 'part',
                   'chapter': 'ch',
                   'section': 'sec',
                   'subsection': 'subsec',
                   'subsubsection': 'subsubsec',
                   }

    def __init__(self, name, content, attributes, context, **kwargs):

        # If no content is specified, see if it's specified in the context
        if (isinstance(content, str) and content.strip() == '' and
           name in context):
            content = content_to_str(context[name])

        # Call the parent class's constructor
        Tag.__init__(self, name=name, content=content, attributes=attributes,
                     context=context, **kwargs)

        if 'nolabel' not in self.attributes:
            LabelMixin.__init__(self, name=name, content=content,
                                attributes=attributes, context=context,
                                **kwargs)

    def generate_label_id(self):
        if 'id' in self.attributes:
            return self.attributes['id']
        else:
            # If an id wasn't specified, automatically generate one and
            # prepend a heading id mapping. 'my-title' to 'ch:my-title'
            cls_name = self.__class__.__name__.lower()
            label_id = LabelMixin.generate_label_id(self)
            return ":".join((Heading.id_mappings[cls_name], label_id))

    def generate_label_kind(self):
        cls_name = self.__class__.__name__.lower()
        return 'heading', cls_name  # ex: ('heading', 'chapter')

    def default_fmt(self, content=None, attributes=None):
        # Prepare the content with the label. References for the default format
        # are not supported
        label_tag = self.label_tag
        if content is not None:
            pass
        elif label_tag is not None:
            content = self.label_tag.default_fmt()
        else:
            content = content_to_str(self.content)

        return super().default_fmt(content=content, attributes=attributes)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1,
                **kwargs):
        cls_name = self.__class__.__name__.lower()
        content = ''
        attributes = attributes or self.attributes

        # Prepare the tag contents to include the label tag.
        # ex: 'My Title' becomes 'Chap 1. My Title'
        if self.label_tag is not None:
            content += self.label_tag.tex_fmt(mathmode=mathmode,
                                              level=level + 1)

        # Format the heading tag. ex: \chapter{Chapter 1. My First Chapter}
        content = tex_cmd(cls_name, attributes=attributes,
                          formatted_content=content)

        # Get the label for this heading to get its number, if available
        if self.label_id is not None and self.label_anchor is not None:
            assert self.context.is_valid('label_manager')

            label_manager = self.context['label_manager']
            label = label_manager.get_label(id=self.label_id)

            number = label.order[-1] if label.order else None
            number -= 1  # Offset by -1 as the counter is increased
            attrs = ' '.join((cls_name, str(number)))

            content = (tex_cmd('setcounter', attributes=attrs) + '\n' +
                       content + ' ' +
                       self.label_anchor.tex_fmt(mathmode=mathmode,
                                                 level=level + 1))

        return content

    def html_fmt(self, content=None, **kwargs):
        # Prepare the tag contents to include the label tag.
        # ex: 'My Title' becomes 'Chap 1. My Title'
        label_tag = self.label_tag
        if content is not None:
            pass
        elif label_tag is not None:
            content = label_tag
        else:
            content = self.content

        return super().html_fmt(content=content, **kwargs)


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
