Preamble
========

The preamble tags format and present the meta information for the
title and author(s) for the document.

``@titlepage``
  Render a title page for the document
  
  :Examples:

     ::
        
        @titlepage{}

Table-of-Contents
-----------------

The Table-of-Contents (TOC) tag is used to render the table of
contents or site map of a project.

``@toc{...}``
    Render a table of contents

    .. index::
        single: tags; @toc

    :contents:

        ``all``

           Include labels from all sub-documents in the TOC. If all is
           not specified, only the labels for the current document
           will be presented.
        
        ``documents``

           Render a document TOC with the document and heading
           entries.
        
        ``headings``

           Render a TOC with heading entries.

        ``figure``

           Render a TOC with figure caption entries.

    :content modifiers:

        ``collapsed`` (default)

           Show only the documents without headings. Pertains to ``all
           documents`` and ``all headings``.
        
        ``expanded``

           Show all documents are including all headings. Pertains to
           ``all documents`` and ``all headings``.

        ``abbreviated``

           show all documents but only show headings for the current
           document. Pertains to ``all documents`` and ``all
           headings``.
        
    :attributes:

        ``header``

           Include a ‘Table of Contents’ heading for the TOC. Note
           that this heading won’t appear in the TOC.

    :examples:

       ::

          @toc[header]{all documents}
          @toc{all documents collapsed}

Collection
----------

Collection tags are used to group all the subdocuments in a project
into a collection, like a book.

``@collection{}``
    A collection tag for a document and all its sub-documents.

    .. index::
       single: tags; @collection

    :examples:

       ::

          @collection{}
