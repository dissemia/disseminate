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

Basic Variables
---------------

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

      ::

         include:
           part1/introduction.dm
           part1/cakes.dm
           part1/tarts.dm
