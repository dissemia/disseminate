"""
Tags for headings.
"""
from .core import Tag
from ..attributes import get_attribute_value, set_attribute, remove_attribute
from ..utils.string import slugify


toc_levels = ('chapter', 'section', 'subsection', 'subsubsection')


class Heading(Tag):
    """A heading tag.

    Tag Attributes
    --------------
    - nolabel: If specified, a label entry will not be created for this heading.
    """
    html_name = None
    tex_name = None
    active = True
    include_paragraphs = False

    label_heading = True
    label = None

    _nolabel = None

    def __init__(self, name, content, attributes, context):
        super(Heading, self).__init__(name, content, attributes, context)

        # Determine whether a label should be given. By default, each heading
        # has a label
        nolabel = get_attribute_value(self.attributes, 'nolabel')
        self.attributes = remove_attribute(self.attributes, 'nolabel')
        if nolabel:
            self.label_heading = False

        # Add a label for the heading, if needed
        if (self.label_heading and
           'label_manager' in context and 'document' in context):

            label_manager = context['label_manager']
            document = context['document']
            kind = ('heading', self.__class__.__name__.lower())

            id = get_attribute_value(self.attributes, 'id')

            # Assign an label, if one was not given
            if id is None:
                label = self.__class__.__name__.lower() + ":"
                id = label + slugify(self.content)
                self.attributes = set_attribute(self.attributes, ('id', id))

            label = label_manager.add_label(document=document, tag=self,
                                            kind=kind, id=id)
            self.label = label

    def tex(self, level=1, mathmode=False):
        # Add newlines around headings
        name = (self.tex_name if self.tex_name is not None else
                self.__class__.__name__.lower())
        # Get the label
        if self.label is not None:
            label = ' ' + self.label.label(target='.tex')
        else:
            label = ''

        fmt = '\n\\{name}{{{content}}}{label}\n\n'.format(name=name,
                                                          content=self.content,
                                                          label=label)
        return fmt


class Chapter(Heading):
    """A section heading tag."""
    aliases = ("h1", "title" )
    html_name = "h1"
    tex_name = "chapter"
    active = True
    include_paragraphs = False


class Section(Heading):
    """A section heading tag."""
    aliases = ("h2", )
    html_name = "h2"
    tex_name = "section"
    active = True
    include_paragraphs = False


class SubSection(Heading):
    """A subsection heading tag."""
    aliases = ("h3",)
    html_name = "h3"
    tex_name = "subsection"
    active = True
    include_paragraphs = False


class SubSubSection(Heading):
    """A subsubsection heading tag."""
    aliases = ("h4",)
    html_name = "h4"
    tex_name = "subsubsection"
    active = True
    include_paragraphs = False


class Para(Tag):
    """A paragraph heading tag."""
    aliases = ("h5",)

    html_name = "paragraph-heading"
    tex_name = "paragraph"
    active = True
    include_paragraphs = False

    label_heading = False
