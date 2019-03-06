"""Tags to render collections of documents
"""

from .core import Tag
from .. import settings


class Collection(Tag):
    """Collections are simple tags used to render tags of a document as well as
    the tags of all sub-documents."""

    active = True
    include_paragraphs = False

    def fetch_tags(self, content=None, target=None):
        """Collect the tags from the sub-documents into a list."""
        # Retrieve the name of the context variable from this tag's contents.
        # If not specified, use the default body variable.
        content = content if content is not None else self.content
        context_name = content.strip()
        context_name = (context_name if context_name != "" else
                        settings.body_attr)

        # Load subdocuments
        doc = self.context.get('document', None)
        doc = doc() if doc is not None else None  # dereference the weakref

        subdocs = (doc.documents_list(only_subdocuments=True, recursive=True)
                   if doc is not None else [])

        # Filter subdocuments that match the given the target
        if target is not None:
            subdocs = [subdoc for subdoc in subdocs if target in subdoc.targets]

        # Retrieve the context tags that match the context_name
        return [subdoc.context[context_name] for subdoc in subdocs
                if context_name in subdoc.context and
                isinstance(subdoc.context[context_name], Tag)]

    @property
    def mtime(self):
        tags = self.fetch_tags()
        mtimes = [tag.mtime for tag in tags if hasattr(tag, 'mtime')]
        mtimes = [mtime for mtime in mtimes if mtime is not None]  # Filter None

        return max(mtimes) if len(mtimes) > 0 else None

    def default_fmt(self, content=None):
        tags = self.fetch_tags(content=None, target=None)
        return super(Collection, self).default_fmt(content=tags)

    def html_fmt(self, level=1, content=None):
        tags = self.fetch_tags(content=None, target='.html')
        return super(Collection, self).html_fmt(level=level, content=tags)

    def tex_fmt(self, level=1, mathmode=False, content=None):
        tags = self.fetch_tags(content=None, target='.tex')
        return super(Collection, self).tex_fmt(level=level, mathmode=mathmode,
                                               content=tags)
