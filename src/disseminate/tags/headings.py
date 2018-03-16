"""
Tags for headings.
"""
from .core import Tag
from ..attributes import get_attribute_value


class Heading(Tag):
    """A heading tag."""
    html_name = None
    tex_name = None
    active = True
    include_paragraphs = False

    label_heading = True

    def __init__(self, name, content, attributes, local_context,
                 global_context):
        super(Heading, self).__init__(name, content, attributes, local_context,
                                      global_context)

        # Add a label for the heading
        if (self.label_heading and
           '_label_manager' in global_context and
           '_document' in local_context):

            label_manager = global_context['_label_manager']
            document = local_context['_document']
            kind = self.__class__.__name__.lower()
            id = get_attribute_value(self.attributes, 'id')

            label_manager.add_label(document=document, kind=kind, id=id,
                                    contents=self.content)

    def tex(self, level=1, mathmode=False):
        # Add newlines around headings
        tex = super(Heading, self).tex(level, mathmode)
        return "\n" + tex + "\n\n"


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
