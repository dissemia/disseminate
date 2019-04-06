"""
Tags for headings.
"""
from lxml.builder import E
from lxml import etree
from markupsafe import Markup

from .tag import Tag
from .utils import content_to_str
from ..utils.string import slugify, titlelize
from .. import settings


toc_levels = ('branch', 'section', 'subsection', 'subsubsection')


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
    tex_name = None
    active = True
    include_paragraphs = False

    label_heading = True

    _nolabel = None
    _id_mappings = None

    def __init__(self, name, content, attributes, context):

        # If no content is specified, see if it's specified in the context
        if (isinstance(content, str) and content.strip() == '' and
           name in context):
            content = content_to_str(context[name])

        # Call the parent class's constructor
        super(Heading, self).__init__(name, content, attributes, context)

        # Determine whether a label should be given. By default, each heading
        # has a label
        if 'nolabel' in self.attributes:
            nolabel = True
            del self.attributes['nolabel']
        else:
            nolabel = False

        if nolabel:
            self.label_heading = False

        if self.label_heading:
            # Add a label for the heading, if needed
            kind = ('heading', self.__class__.__name__.lower())
            id = self.get_id()
            self.attributes['id'] = id
            self.set_label(id=id, kind=kind)

    def get_id(self):
        # Get the id mappings, if not set yet
        if Heading._id_mappings is None:
            Heading._id_mappings = {'branch': 'br',
                                    'section': 'sec',
                                    'subsection': 'subsec',
                                    'subsubsection': 'subsubsec',
                                    }

        id = self.attributes.get('id', None)

        # Assign an id_type, if one was not given
        if id is None:
            # Start the with the heading type. ex: 'br:' or 'sec:'
            classname = self.__class__.__name__.lower()
            id_type = self._id_mappings.get(classname, classname) + ":"

            # Next use the doc_id to construct the heading. ex: 'Introduction'
            doc_id = self.context.get('doc_id', '')

            # Next use the content, if available and usable. To be usable, it
            # should either be a Tag, which can be converted to a raw string, or
            # a string itself or a list of tags and strings.
            content = content_to_str(self.content)
            content = titlelize(content).strip()

            # If there is no content, then just make one up based on a simple
            # counter.
            if not content:
                # If the content is not available or it's an empty string, just
                # give it a number
                i = 'heading_count'
                self.context[i] = self.context.get(i, 0) + 1
                content = str(self.context[i])

            slug_txt = doc_id + '_' + content if doc_id else content

            # Create the id from the heading type (id_type), the doc_id and
            # content
            id = id_type + slugify(slug_txt)
            self.attributes['id'] = id
        return id

    def set_label(self, id, kind, title=None):
        assert id is not None

        document = (self.context['document']() if 'document' in self.context
                    else None)
        title = self.title if title is None else title

        if 'label_manager' in self.context and document is not None:
            label_manager = self.context['label_manager']

            # Create the label
            label_manager.add_heading_label(id=id, kind=kind, title=title,
                                            context=self.context)
            self.label_id = id

    def _get_label_fmt_str(self, tag_name=None, target=None):
        # Specify a _get_label_fmt_str that has 'heading' as the tag name,
        # instead of the name of the tag for Heading subclasses, like 'branch'
        # or 'section'.
        return super(Heading, self)._get_label_fmt_str(tag_name='heading',
                                                       target=target)

    def default_fmt(self, content=None):
        name = self.__class__.__name__.lower()
        label = self.label

        if label is not None:
            label_tag = self.get_label_tag()

            # Replace the label_tag name to this heading's name, ex: 'Chapter'
            label_tag.name = name
            return "\n" + label_tag.default_fmt(content) + "\n\n"
        else:
            return super(Heading, self).default_fmt(content)

    def html_fmt(self, level=1, content=None):
        name = self.__class__.__name__.lower()
        label = self.label

        if label is not None:
            label_tag = self.get_label_tag(target='.html', wrap=False)

            # Replace the label_tag name to this heading's name, ex: 'chapter'
            label_tag.name = name

            # Wrap the label tag in a h1/h2/h3/.. heading
            e = E(self.html_name, label_tag.html_fmt(level+1),
                  **self.attributes)

            # Return the html element as either text (level=1) or simply an
            # element
            if level == 1:
                s = (etree.tostring(e, pretty_print=settings.html_pretty)
                          .decode("utf-8"))
                return Markup(s)  # Mark string as safe bc it's escaped by lxml
            else:
                return e
        else:
            return super(Heading, self).html_fmt(level, content)

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
