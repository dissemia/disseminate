.. role:: dm(code)
   :language: dm

Headings
========

Headings are used to group and demarcate parts of a document or project.

.. rst-class:: dl-parameter


:dm:`@part{...}`
    A part heading

    .. index::
        single: tags; @part
        single: tags; @h1

    :aliases: ``@h1``

    :attributes:

        .. include:: header_attributes.rst

    :examples:

        .. code-block:: dm

           @chapter{Object Decorators}
           @chapter[fmt="Chapter {label.tree_number}. '{label.short}'"]{Introduction}


:dm:`@chapter{...}`
    A chapter heading

    .. index::
        single: tags; @chapter
        single: tags; @h2

    :aliases: ``@h2``
              
    :attributes:

        .. include:: header_attributes.rst

    :examples:

        .. code-block:: dm
          
           @chapter{Object Decorators}
           @chapter[fmt="Chapter {label.tree_number}. '{label.short}'"]{Introduction}


:dm:`@section{...}`
    A section heading

    .. index::
        single: tags; @section
        single: tags; @h3

    :aliases: ``@h3``

    :attributes:

        .. include:: header_attributes.rst
       
    :examples:

       .. code-block:: dm
          
          @section{Introduction}
          @section[id="chapter1-introduction"]{Introduction}
          @h2{Introduction}

:dm:`@subsection{...}`
    A subsection heading

    .. index::
        single: tags; @subsection
        single: tags; @h4

    :aliases: ``@h4``

    :attributes:

        .. include:: header_attributes.rst
       
    :examples:

       .. code-block:: dm

          @subsection{Methods}
          @h3{Methods}

:dm:`@subsubsection{...}`
    A subsubsection heading

    .. index::
        single: tags; @subsubsection
        single: tags; @h5

    :aliases: ``@h5``
              
    :attributes:

        .. include:: header_attributes.rst
       
    :examples:

       .. code-block:: dm

          @subsubsection{Titration Procedure}
          @h4{Titration Procedure}

:dm:`@paragraph{...}`
    A paragraph heading

    .. index::
        single: tags; @paragraph
        single: tags; @h6

    :aliases: ``@h6``
              
    :attributes:

       ``id=x``

           The paragraph's marker label

    :html: In html, this tag will be rendered as a
           ``<span class="paragraph-heading">`` instead of an ``<h5>`` element.

    :note: This tag is distinct from the ``@p``, which is used to identify a
           paragraph element.

    :examples:

       .. code-block:: dm

          @paragraph{Group A}. The first group ...
          @h5{Group A}. The first group ...


Identifiers and Labels
----------------------

By default, all headings have a *unique* identifier and label. Labels allow
other portions of a project to reference the heading.

If a heading without a label is desired, the ``nolabel`` attribute can be used.
Headings without a label cannot be linked and referenced in the project, and
the heading will not be included in Tables of Content.

Otherwise, it is recommended to use an identifier. An identifier is specified
with the ``id=x`` attribute, and it should be *unique* for the project. If an
identifier is not specified, an identifier will be generated.

Empty Contents
--------------
If the contents are empty, the tag will search the header entries to
see if an entry with the same name is present. For example, if
the header has an entry ``chapter: My First Chapter``, then inserting
the ``@chapter`` tag in the body will use the 'My First Chapter' text
as its contents.