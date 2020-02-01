.. _document:

Documents
=========

Each disseminate source file is a document. Documents are rendered into the
specified target formats.

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
in the ``src`` directory and specified in the ``template`` entry of a document.

Managers
--------

Each project has a :ref:`dependency manager <dependency-manager>` and a label
manager. The dependency manager coordinates the copying or conversion of
dependent files needed to render to different target formats. The label
manager coordinates links, references and numbering for components of a
document, like headers, figures, tables and equations.

Path Precedence
---------------
Documents and projects may include image, media and data files. Tags like
:ref:`@img <tags-img>` will search for these files in the following paths, in
this order:

1. Template files, like ``.css`` stylesheets
2. The path local to the document.

   .. note::

       For example, the file ``src/chapter1/figures/fig1.png`` included in
       ``src/chapter1/chapter1.dm`` will be used and copied to the target
       path ``html/chapter1/figures/fig1.png``.

3. The root path for the project.

    .. note::

       For example, the file ``src/media/figures/fig1.png`` included in
       ``src/chapter1/chapter1.dm`` will be used and copied to the target
       path ``html/media/figures/fig1.png``.
