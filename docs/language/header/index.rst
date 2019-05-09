Header
======

Headers contain useful meta information on the document like the title
and author. Meta information in disseminate is stored in a context,
and these modify the behavior of tags and the rendering of documents.

Headers are optionally present at the start of a disseminate
document. Headers are enclosed by 3 or more hyphens (’``-``‘). The
following is an example of the header for this page.

::

   ---
   title: Disseminate Headers
   author: Justin L Lorieau
   template: component
   targets: html, tex, pdf
   include:
     part1/introduction.dm
     part1/cakes.dm
     part1/tarts.dm
   ---

Since documents can include sub-documents, the context of a parent
document is copied over to the sub-documents, which in turn, can
overwrite these values.

Entries
-------

Basic Entries
~~~~~~~~~~~~~

``title``
   The document's title

   .. index::
      single: header; title

   :examples:

      ::

         title: My First Document

``short``
   The document's *short* title

   .. index::
      single: header; short

   :examples:

      ::

         short: First

``author``
   The document’s author

   .. index::
      single: header; author

   :examples:

      ::

         author: Justin L Lorieau

``targets``
   The target formats to render the document

   .. index::
      single: header; targets

   :examples:

      ::

         targets: html, tex, pdf

``template``
   The template to use in rendering the document

   .. index::
      single: header; template

   :notes:

      Templates are written in Jinja2 format. A template file should
      be available for each of the desired targets. ex:
      ``component.html`` for ``.html`` targets and ``component.tex``
      for ``.tex`` targets.
      
   :examples:

      ::

         template: book/tufte

``include``
   The sub-documents to include in a project

   :notes:

      See the section on :ref:`header-includes`.


Render Options
~~~~~~~~~~~~~~

``label_fmts``
   The formats for labels in rendering the document.

   .. index::
      single: header; label_fmts

   :examples:

      .. code-block:: none

         label_fmts:
            document: "@label.title"
            ref_document: "@label.title"
            heading: "@label.tree_number."
            heading_part: "Part @label.part_number. "
            heading_chapter': "Chapter @label.chapter_number. "


``label_resets``
   Specify which label kinds reset the counters of other label kind counter.

   .. index:: single: header; label_resets


   :examples:

      A project may need to have the the chapter, section and subsection numbers
      reset every time there is a new part. To achieve this sort of reset,
      the following entry would be entered in the heading of the root document.


      .. code-block:: none

         label_resets:
            part: chapter, section, subsection



``relative_links``
   If True (default), html links are referenced relative to the document's
   path. If False, links are absolute.

   .. index::
      single: header; relative_links

   :examples:

      .. code-block:: none

         relative_links: True


``base_url``
    If absolute links are used and ``relative_links`` is False, then the
    base_url string will be prepended to links.

   .. index::
      single: header; base_url

   :examples:

      .. code-block:: none

         base_url: /{target}/{subpath}


``process_paragraphs``
   A list of context entries for which paragraphs should be processed

   .. index::
      single: header; process_paragraphs

   :notes:

      By default, automated paragraph processing is enabled for the body entry.

   :examples:

      .. code-block:: none

         process_paragraphs: body


.. _header-includes:

Includes
--------

Sub-documents like parts of books, chapters or sections can be
included with an include statement in the header. Sub-documents can be
nested to form projects with multiple sub-levels. The include
statement lists the sub-documents directly subordinate to a document.

``include``
   Sub-documents to include in the document tree

   .. index::
      single: header; include

   :notes:

      Sub-documents and their paths are listed one per line with at
      least two spaces before each entry. The paths are relative to
      the current document.

   :examples:

      .. code-block:: none

         include:
           part1/introduction.dm
           part1/cakes.dm
           part1/tarts.dm



Inheritance
-----------

Additional Notes
----------------

How do I include quotations in header entries?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Quotations within a sentence or string will not be removed

:example:

   .. code-block:: none

      title: This is my "test" title

However, quotations on the end of a sentence or string will be removed. To
include these quotations, simply add the quotation mark twice on each side
of the entry.

:example:

   .. code-block:: none

      title: ""This is my test title""

In the above example, the title will be ``"This is my test title"`` with the
double quotations.