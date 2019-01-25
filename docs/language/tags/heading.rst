Headings
========

Headings are used to group and demarcate parts of the document's text.

``@chapter{...}``
    A chapter heading

    .. index::
        single: tags; @chapter
        single: tags; @h1

    :aliases: ``@h1``
    :attributes:

        ``id`` -- The section heading's marker label
        
        ``nolabel`` -- If specified, a label is not created with this
        heading for TOC entries and links
        
        ``short`` -- The short title, which can be used in the TOC
        
        ``fmt`` -- The format for a tag’s label

    :examples:

        ::
          
           @chapter{Object Decorators}
           @chapter[fmt="Chapter {label.tree_number}. '{label.short}'"]{Introduction}


``@section{...}``
    A section heading

    .. index::
        single: tags; @section
        single: tags; @h2

    :aliases: ``@h2``
    :attributes:

        ``id`` -- The section heading's marker label
        
        ``nolabel`` -- If specified, a label is not created with this
        heading for TOC entries and links
        
        ``short`` -- The short title, which can be used in the TOC
        
        ``fmt`` -- The format for a tag’s label

    :examples:

       ::
          
          @section{Introduction}
          @section[id="chapter1-introduction"]{Introduction}
          @h2{Introduction}

``@subsection{...}``
    A subsection heading

    .. index::
        single: tags; @subsection
        single: tags; @h3

    :aliases: ``@h3``
    :attributes:

        ``id`` -- The subsection heading's marker label

        ``nolabel`` -- If specified, a label is not created with this
        heading for TOC entries and links
        
        ``short`` -- The short title, which can be used in the TOC
        
        ``fmt`` -- The format for a tag’s label

    :examples:

       ::

          @subsection{Methods}
          @h3{Methods}

``@subsubsection{...}``
    A subsubsection heading

    .. index::
        single: tags; @subsubsection
        single: tags; @h4

    :aliases: ``@h4``
    :attributes:

        ``id`` -- The subsubsection heading's marker label

        ``nolabel`` -- If specified, a label is not created with this
        heading for TOC entries and links
        
        ``short`` -- The short title, which can be used in the TOC
        
        ``fmt`` -- The format for a tag’s label

    :examples:

       ::

          @subsubsection{Titration Procedure}
          @h4{Titration Procedure}

``@paragraph{...}``
    A paragraph heading

    .. index::
        single: tags; @paragraph
        single: tags; @h5

    :aliases: ``@h5``
    :attributes:

        ``id`` -- The paragraph heading's marker label.

    :html: In html, this tag will be rendered as a
           ``<span class="paragraph-heading">`` instead of an ``<h5>`` element.

    :note: This tag is distinct from the ``@p``, which is used to identify a
           paragraph element.

    :examples:

       ::

          @paragraph{Group A}. The first group ...
          @h5{Group A}. The first group ...
