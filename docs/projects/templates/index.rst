.. _templates:

Templates
=========

Templates are used to render disseminate documents (``.dm``) to other
formats, such as ``.html``, ``.tex`` and ``.pdf``. A variety of
templates are built into disseminate.

Built-in Templates
------------------

Built-in or global templates reside within the disseminate project.

The following templates are available:

   ::

      default
      articles/basic
      books/novel
      books/tufte
      reports/basic

The ``default`` template will be used unless another template is
specified in the header of a document. The specified template will
then be used for the document and all sub-documents.

..
    User-Defined Templates
    ----------------------

    Alternatively, a user can specific a customized template. To specify a
    custom template, create a template file for each target format in the
    source directory, and specify the base filename in the document
    header.
