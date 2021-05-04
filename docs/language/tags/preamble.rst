.. role:: dm(code)
   :language: dm

Preamble
========

The preamble tags format introductory material for a document or project.

.. rst-class:: dl-parameter

:dm:`@titlepage`
  Render a title page for the document
  
  :Examples:

     .. code-block:: dm
        
        @titlepage{}

:dm:`@toc{...}`
    Render a table of contents. The table of contents behaves as a site map for
    the project

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

       .. code-block:: dm

          @toc[header]{all documents}
          @toc{all documents collapsed}
