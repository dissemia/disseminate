"""
Tags for captions and references.
"""
from .core import Tag
from ..attributes import get_attribute_value
from .. import settings


class CaptionError(Exception):
    """An error was encountered in processing a caption."""
    pass


class RefError(Exception):
    """An error was encountered in a reference."""
    pass


class Caption(Tag):
    """A tag for captions."""

    html_name = 'caption'
    tex_name = 'caption'
    active = True

    def add_label(self, local_context, global_context, kind,
                  id=None, contents=None):
        """Add a label to the caption.

        .. note:: This function is run by the parent tag so that the kind is
                  properly set.

        Parameters
        ----------
        local_context : dict, optional
            The context with values for the document that owns this label. The
            values in this dict do not depend on values from other documents.
            (local)
        global_context : dict
            The context with values for all documents in a project.
        kind : str
            The kind of label. ex: 'chapter', 'figure', 'equation'
        id : str, optional
            The label of the label ex: 'ch:nmr-introduction'
            If a label id is not specified, a short one based on the
            document and label count will be generated.
        contents : str, optional
            The short description for the label that can be used as the
            reference.
        """
        # Get the id, if this caption has one
        id = id if id is not None else get_attribute_value(self.attributes,
                                                           'id')

        # Get the label manager and add the label
        if '_label_manager' in global_context:
            label_manager = global_context['_label_manager']
            label = label_manager.add_label(local_context=local_context,
                                            global_context=global_context,
                                            kind=kind,
                                            id=id,
                                            contents=contents)
            # Get the label's text and add it to the caption
            label_text = label.short(local_context=local_context,
                                     global_context=global_context)
            label_text = label_text + settings.label_sep + ' '

            # Add the label's short text to this caption's text.
            if isinstance(self.content, str):
                self.content = ' '.join((label_text, self.content))
            elif (isinstance(self.content, list) and
                  len(self.content) > 0 and
                  isinstance(self.content[0], str)):
                self.content[0] = ' '.join((label_text, self.content[0]))


class Ref(Tag):
    """A tag to reference a label."""

    active = True

    def get_label(self):
        """Retrieve a label from the label_manager."""
        assert '_label_manager' in self.global_context

        # Get the identifier; it has to be a text string
        if not isinstance(self.content, str):
            msg = "The reference '{}' should be a simple text identifier."
            raise RefError(msg.format(str(self.content)))
        id = self.content

        label_manager = self.global_context['_label_manager']
        label = label_manager.get_label(id=id)

        return label

    def default(self, level=1):
        label = self.get_label()
        return label.short(local_context=self.local_context,
                           global_context=self.global_context)

    def html(self, level=1):
        label = self.get_label()
        return label.html_ref(local_context=self.local_context,
                              global_context=self.global_context)

    def tex(self, level=1):
        label = self.get_label()
        return label.tex_ref(local_context=self.local_context,
                             global_context=self.global_context)
