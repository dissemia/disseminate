"""
Tags for captions and references.
"""
from collections import OrderedDict

from lxml.builder import E

from .core import Tag
from .utils import format_label_tag, label_term, set_html_tag_attributes
from ..utils.string import hashtxt


class CaptionError(Exception):
    """An error was encountered in processing a caption."""
    pass


class RefError(Exception):
    """An error was encountered in a reference."""
    pass


class Caption(Tag):
    """A tag for captions.

    .. note:: The use of a naked caption tag is allowed (i.e. a caption not
              nested within a figure or table), but this won't register a label
              with the label manager. This is because the 'add_label' method
              will not be called.
    """

    html_name = 'caption-text'
    tex_name = 'caption'
    kind = None
    active = True

    def set_label(self, id=None, kind=None):
        """Add a label to the caption.

        .. note:: This function is run by the parent tag so that the kind is
                  properly set. If an 'id' is not specified, one is generated
                  from the hash of the contents for this caption.

        Parameters
        ----------
        kind : str
            The kind of label. ex: 'chapter', 'figure', 'equation'
        id : str, optional
            The label of the label ex: 'ch:nmr-introduction'
            If a label id is not specified, a short one based on the
            document and label count will be generated.
        """
        # If an id was specified, use it. Otherwise, get the id from this tag,
        # if it has one
        id = id if id is not None else self.get_attribute(name='id', clear=True)

        # If an id still hasn't been specified, generate one from the caption's
        # contents
        if id is None:
            text = self.default_fmt()
            id = 'caption-' + hashtxt(text)

        kind = ('caption',) if kind is None else kind
        super(Caption, self).set_label(id=id, kind=kind)

        self.kind = ('caption',) if kind is None else (kind, 'caption')

    def default_fmt(self, content=None):
        """Add newline to the end of a caption"""
        label = self.label
        if label is not None:
            label_tag = format_label_tag(tag=self, target=None)
            # add the label to the caption
            return (label_tag.default_fmt() + ' ' +
                    super(Caption, self).default_fmt())
        else:
            return super(Caption, self).default_fmt()

    def html_fmt(self, level=1, content=None):
        label = self.label
        if self.label is not None:
            label_tag = format_label_tag(tag=self, target='.html')

            tag = E('span',
                    label_tag.html_fmt(level+1),
                    label_term(tag=self, target='.html') + ' ',
                    super(Caption, self).html_fmt(level+1))

            # Set the html tag attributes, in order
            kwargs = OrderedDict()
            kwargs['class'] = ' '.join(self.kind)
            kwargs['id'] = label.id
            set_html_tag_attributes(html_tag=tag, attrs_dict=kwargs)

            return tag
        else:
            return super(Caption, self).html_fmt(level+1)

    def tex_fmt(self, level=1, mathmode=False, content=None):
        content = content if content is not None else self.content
        label = self.label

        if self.label is not None:
            label_tag = format_label_tag(tag=self, target='.tex')

            # Format the label and add it to the caption
            string = label_tag.tex_fmt(level+1, mathmode)
            string += label_term(tag=self, target='.tex') + ' '

            if isinstance(content, list):
                content = [string] + content
            elif isinstance(content, str):
                content = string + content

            # Format the caption
            return ("  " +
                    super(Caption, self).tex_fmt(level + 1, mathmode, content) +
                    " \\label{{{id}}}".format(id=label.id) + "\n")
        else:
            return super(Caption, self).tex_fmt(level + 1, mathmode, content)


class Ref(Tag):
    """A tag to reference a label."""

    active = True

    def __init__(self, name, content, attributes, context):
        super(Ref, self).__init__(name, content, attributes, context)

        # Set the label_id
        # Get the identifier; it has to be a text string
        if not isinstance(self.content, str):
            msg = "The reference '{}' should be a simple text identifier."
            raise RefError(msg.format(str(self.content)))
        self.label_id = self.content.strip()

    def default_fmt(self, content=None):
        label_tag = format_label_tag(tag=self)
        return label_tag.default_fmt(content)

    def html_fmt(self, level=1, content=None):
        label = self.label
        label_tag = format_label_tag(tag=self, target='.html')

        # Wrap the label_tag in a link to the label's target
        target_filepath = label.document.target_filepath('.html')

        # Generate the link for the document.
        link = target_filepath.get_url(context=label.document.context)

        # Add the id to the link, if it's not a link to the whole document
        if label.kind[0] != 'document':
            link += '#' + label.id

        kwargs = {'href': link}
        return E('a', label_tag.html_fmt(level+1), **kwargs)

    def tex_fmt(self, level=1, mathmode=False, content=None, page=False):
        label = self.label
        label_tag = format_label_tag(tag=self, target='.tex')

        tex = label_tag.tex_fmt(level+1, mathmode)

        if self.get_attribute(name='page') or page:
            # If the 'page' attribute is set, return a reference for the page.
            return "\\pageref{{{id}}}".format(id=label.id)
        else:
            # Otherwise just return a link to the label
            return "\\hyperref[{id}]{{{content}}}".format(id=label.id,
                                                          content=tex)
