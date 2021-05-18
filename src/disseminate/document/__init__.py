"""
A document corresponds to a single disseminate source file. A document may
contain sub-documents, which in turn may hold sub-documents, to form a tree.
The top-level document is known as a *root document* and the root document and
all sub-documents are known as a project.

Responsibilities
----------------

A document has the following responsibilities:

1. *Managers*. The root document is responsible to create managers.
   There should only be one of each type of manager in a project, and a
   project uses the same managers.
2. *Rendering*. The document is responsible for delegating rendering of the
   document in the target format(s).
3. *Processors*. When rendering a document, the 'body' entry in the context
   (*i.e.* the body of the disseminate source file) will be run through a
   list of processors, listed in the document class.
4. *Conversion*. Some documents types must be compiled or converted to their
   final format--*e.g.* to produce ``pdf`` targets, a ``tex`` target must be
   converted using ``pdflatex``. The document manages this conversion as part
   of the rendering process.
5. *Context*. A document owns a context that is populated by the disseminate
   file header, and which holds the variables used in rendering a document into
   a target format.
6. *Paths*. The document manages paths for the disseminate source file and the
   target files.

Definitions
-----------
1. *Root document*. A document that is not included as a sub-document to
   another document. The root document's context will have objects, like the
   label manager, that are shared by its sub-documents in a project.
2. *Project*. A root document and zero or more sub-documents forming a document
   tree. Sub-documents are included by ``include`` statements in the header of
   the root document.
3. *doc_id*. The document identifier for a document. It is unique for a
   document in a project.


"""

from .document import Document
from .document_context import DocumentContext
from . import exceptions, signals, receivers

__all__ = ('Document', 'DocumentContext', 'exceptions', 'signals', 'receivers')
