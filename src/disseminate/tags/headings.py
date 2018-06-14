"""
Tags for headings.
"""
from lxml.builder import E

from .core import Tag
from .utils import format_label_tag
from ..attributes import set_attribute, kwargs_attributes
from ..utils.string import slugify


toc_levels = ('branch', 'section', 'subsection', 'subsubsection')


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

    _nolabel = None
    _id_mappings = None

    def get_id(self):
        # Get the id mappings, if not set yet
        if Heading._id_mappings is None:
            Heading._id_mappings = {'branch': 'br',
                                    'section': 'sec',
                                    'subsection': 'subsec',
                                    'subsubsection': 'subsubsec',
                                    }

        id = self.get_attribute(name='id')

        # Assign an id_type, if one was not given
        if id is None:
            classname = self.__class__.__name__.lower()
            id_type = self._id_mappings.get(classname, classname) + ":"
            id = id_type + slugify(self.content)
            self.attributes = set_attribute(self.attributes, ('id', id))
        return id

    def __init__(self, name, content, attributes, context):
        super(Heading, self).__init__(name, content, attributes, context)

        # Determine whether a label should be given. By default, each heading
        # has a label
        nolabel = self.get_attribute('nolabel', clear=True)
        if nolabel:
            self.label_heading = False

        if self.label_heading:
            # Add a label for the heading, if needed
            kind = ('heading', self.__class__.__name__.lower())
            id = self.get_id()
            self.attributes = set_attribute(self.attributes, ('id', id))
            self.set_label(id=id, kind=kind)

    def default_fmt(self, content=None):
        name = self.__class__.__name__.lower()
        label = self.label
        if label is not None:
            label_tag = format_label_tag(tag=self)

            # Replace the label_tag name to this heading's name, ex: 'Chapter'
            label_tag.name = name
            return ("\n" +
                    label_tag.default_fmt(content) + "\n\n")
        else:
            return super(Heading, self).default_fmt(content)

    def html_fmt(self, level=1, content=None):
        name = self.__class__.__name__.lower()
        label = self.label

        if label is not None:
            label_tag = format_label_tag(tag=self, target='.html')

            # Replace the label_tag name to this heading's name, ex: 'chapter'
            label_tag.name = name
            kwargs = kwargs_attributes(self.attributes)
            return E(self.html_name, label_tag.html_fmt(level+1), **kwargs)
        else:
            return super(Heading, self).html_fmt(level+1, content)

    def tex_fmt(self, level=1, mathmode=False, content=None):
        name = (self.tex_name if self.tex_name is not None else
                self.__class__.__name__.lower())

        label = self.label
        if label is not None:
            # set counter. ex: \setcounter{chapter}{3}
            string = "\n\\setcounter{{{name}}}{{{number}}}"
            number = (label.global_order[-1] if name == 'chapter' else
                      label.local_order[-1])
            string = string.format(name=name, number=number)

            # Add the section heading and label id.
            # ex: \chapter{Chapter One} \label{ch:chapter-one}
            string += ("\n" + "\\{name}".format(name=name) + "{" +
                       label.title + "} " +
                       "\\label{{{id}}}".format(id=label.id) + "\n\n")
            return string
        else:
            return ("\n" + super(Heading, self).tex_fmt(level+1, mathmode,
                                                        content)
                    + "\n\n")


class Branch(Heading):
    aliases = ("h1", "chapter", "title")
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
