"""
The Ref tag to reference captions and other labels.
"""
from .core import Tag
from .. import ast
from ..utils.string import StringTemplate


class RefError(Exception):
    """A reference to a document could not be found."""
    pass


class Ref(Tag):
    """A tag to reference a label."""

    active = True
    doc_id = None

    def __init__(self, name, content, attributes, context, doc_id=None):
        super(Ref, self).__init__(name, content, attributes, context)
        self.doc_id = doc_id

        # Set the label_id
        # Get the identifier; it has to be a text string
        if not isinstance(self.content, str):
            msg = "The reference '{}' should be a simple text identifier."
            raise RefError(msg.format(str(self.content)))
        self.label_id = self.content.strip()

    def get_label_tag(self, target=None):
        """Create a new formatted tag for the label associated with this ref
        tag.

        Parameters
        ----------
        target : str, optional
            The optional target for the label's format string.

        Returns
        -------
        label_tag : :obj:`disseminate.tags.Tag`
            The formatted tag for this tag's label.
        """
        assert self.context.is_valid('document', 'root_document')

        # Get the tag's label
        label = self.label

        # Get the format string for the label, either from this tag's
        # attributes, this tag's context or the default context.
        label_fmt = self._get_label_fmt_str(target=target)

        # Get the link for the label. The link is
        # generated from the specified document's target_filepath.
        if self.doc_id is None:
            current_document = self.context['document']()
            target_filepath = current_document.target_filepath(target)
        else:
            # Search for the ref document by doc_id
            root_document = self.context['root_document']()  # de-reference
            docs_by_doc_id = root_document.documents_by_id(recursive=True)

            if self.doc_id not in docs_by_doc_id:
                raise RefError
            other_document = docs_by_doc_id[self.doc_id]
            target_filepath = other_document.target_filepath('.html')

        # Generate the link for the document.
        link = target_filepath.get_url(context=self.context)

        # Add the id to the link, if it's not a link to the whole document
        if label.kind[0] != 'document':
            link += '#' + label.id

        # Convert the label_fmt string to a string template
        label_tmplt = StringTemplate(label_fmt)

        # A label format string has been found. Now format it.
        label_string = label_tmplt.substitute(label=label, link=link)

        # Format any tags
        label_tag = ast.process_ast(label_string, context=self.context)
        label_tag.name = self.name  # convert tag name from 'root' to 'ref'
        return label_tag

    def default_fmt(self, content=None):
        # Return the default result for the label tag created for the label
        # linked to by this ref.
        label_tag = self.get_label_tag()
        return label_tag.default_fmt(content)

    def html_fmt(self, level=1, content=None):
        # Return the html result for the label tag created for the label
        # linked to by this ref.
        label_tag = self.get_label_tag(target='.html')
        return label_tag.html_fmt(level+1, content)

    def tex_fmt(self, level=1, mathmode=False, content=None, page=False):
        # Return the tex result for the label tag created for the label
        # linked to by this ref.
        label_tag = self.get_label_tag(target='.tex')
        return label_tag.tex_fmt(level+1, mathmode)
