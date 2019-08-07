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
`include <header-includes>`_ entry in a document's header.

Projects are organized in a source directory. By default, these are placed in
a ``src`` directory.  One or more disseminate source files and dependent media
files are placed in the root or sub-directories ``src`` directory.

Templates
---------

Documents use `templates`_ to render documents. Disseminate comes with a series
of built-in templates, or custom, user-defined templates can be placed in the
``src`` directory and specified in the ``template`` entry of a document.

Managers
--------

Each project has a `dependency manager <dependency-manager>`_ and a label
manager. The dependency manager coordinates the copying or conversion of
dependent files needed to render to different target formats. The label
manager coordinates links, references and numbering for components of a
document, like headers, figures, tables and equations.
