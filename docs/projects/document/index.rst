.. _document:

Documents
=========

Each disseminate source file is a document. Documents are rendered into
target formats.

Trees
-----

A document may have sub-documents which, in turn, may each have sub-documents.
The tree of documents forms a *project*, and the top-level document is the
*root document*.

Document trees are created by *including* sub-documents in a document with the
:ref:`include <header-includes>` entry in a document's header.

Projects are organized in a source directory. By default, these are placed in
a ``src`` directory.  One or more disseminate source files and dependent media
files are placed in the root or sub-directories ``src`` directory.

Templates
---------

Documents use :ref:`templates` to render documents. Disseminate comes with a
series of built-in templates, or custom, user-defined templates can be placed
in the ``src`` directory and specified in the ``template`` directory.

Path Precedence
---------------
Documents and projects may include image, media and data files. Paths are stored
in a list in the ``'path'`` entry of the document context. Paths are searched
in the following order:

1. *Template paths*. Includes template files like ``.css`` stylesheets. May
   include the template path for derived templates followed by the parent
   template path.
   Defined in :py:func:`.document.receivers.process_headers`.
2. *Local path*. The path local to the document. For example, the file
   ``src/chapter1/figures/fig1.png`` included in ``src/chapter1/chapter1.dm``
   will be used and copied to the target path
   ``html/chapter1/figures/fig1.png``. Defined in
   :py:meth:`.document.document_context.DocumentContext.reset`.
3. *Project root path*. The path of the project root directory. For example,
   the file ``src/media/figures/fig1.png`` included in
   ``src/chapter1/chapter1.dm`` will be used and copied to the target
   path ``html/media/figures/fig1.png``. Defined in
   :py:meth:`.document.document_context.DocumentContext.reset`.
