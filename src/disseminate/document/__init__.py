"""
A document corresponds to a single disseminate source file. A document may
contain sub-documents, which in turn may hold sub-documents, to form a tree.
The top-level document is known as a *root document* and the root document and
all sub-documents are known as a project.

A document has the following responsibilities:

1. *Managers*. The root document is responsible for create a label_manager and
   dependency_manager for the project. There should only be one of each type of
   manager in a project, and a project uses the same managers.
2. *Change Detection*. The document checks the modification times of the
   source file to see if the rendered targets need to be updated. Additionally,
   it will use the label_manager to detect changes on dependent labels and
   the dependency_manager to detect changes on dependent files, like images, to
   decide whether the rendered target needs to be updated.
3. *Rendering*. The document is responsible for rendering the document in the
   target format(s).
4. *Processors*. When rendering a document, the 'body' entry in the context
   (*i.e.* the body of the disseminate source file) will be run through a
   list of processors, listed in the document class.
5. *Conversion*. Some documents types must be compiled or converted to their
   final format--*e.g.* to produce ``pdf`` targets, a ``tex`` target must be
   converted using ``pdflatex``. The document manages this conversion as part
   of the rendering process.
6. *Context*. A document owns a context that is populated by the disseminate
   file header, and which holds the variables used in rendering a document into
   a target format.
7. *Paths*. The document manages paths for the disseminate source file and the
   target files.
"""

from .document import Document, DocumentError
from .document_context import DocumentContext
