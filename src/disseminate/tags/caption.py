"""
Tags for captions and references.
"""
from lxml.builder import E

from .core import Tag
from ..utils.string import hashtxt
from ..attributes import get_attribute_value, remove_attribute


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
        # Get the id, if this caption has one
        id = id if id is not None else get_attribute_value(self.attributes,
                                                           'id')
        self.attributes = remove_attribute(self.attributes, 'id')

        # If an id still hasn't been specified, generate one from the caption's
        # contents
        if id is None:
            text = self.default()
            id = 'caption-' + hashtxt(text)

        kind = ('caption',) if kind is None else kind

        super(Caption, self).set_label(id=id, kind=kind)

    def default(self):
        """Add newline to the end of a caption"""
        default = super(Caption, self).default()

        if self.label is not None:
            # add the label to the caption
            return ' '.join((self.label.label(target='default'), default))
        else:
            return default

    def html(self, level=1):
        html = super(Caption, self).html(level+1)
        if self.label is not None:
            # add the label to the caption
            label = self.label.label(target='.html')
            kwargs = {'class': 'caption'}
            return E('span', label, html, **kwargs)
        else:
            return html

    def tex(self, level=1, mathmode=False):
        tex = super(Caption, self).tex(level + 1, mathmode)

        if self.label is not None:
            # add the label to the caption
            return ' '.join((self.label.label(target='.tex'), tex)) + '\n'
        else:
            return tex + '\n'


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

    def get_label(self):
        """Retrieve a label from the label_manager."""
        assert 'label_manager' in self.context
        label_manager = self.context['label_manager']
        label = label_manager.get_label(id=self.label_id)

        return label

    def default(self, level=1):
        label = self.get_label()
        return label.ref(target='default')

    def html(self, level=1):
        label = self.get_label()
        return label.ref(target='.html')

    def tex(self, level=1, mathmode=False):
        label = self.get_label()
        return label.ref(target='.tex')
