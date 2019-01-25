Text Formatting
===============

Text formatting tags are used to emphasize text in different ways and
to introduce special characters.

``@bold{...}``
    Emphasize text by with bold

    .. index::
        single: tags; @bold
        single: tags; @b
        single: tags; @textbf

    :aliases: ``@b`` ``@textbf``

    :examples:

       ::

          @bold{This text is bold!}
          @b{This text is bold!}
          @textbf{This text is bold!}

``@italics{...}``
    Emphasize text by with italics

    .. index::
        single: tags; @italics
        single: tags; @i
        single: tags; @textit

    :aliases: ``@i`` ``@textit``

    :examples:

        ``@italics{This text is in italics}``

        ``@i{This text is in italics}``

        ``@textit{This text is in italics}``

``@sup{...}``
    Superscript text

    .. index::
        single: tags; @sup
        
    :examples:

        ``@sup{1}H``


``@sub{...}``
    Subscript text

    .. index::
        single: tags; @sub

    :examples:

       ::

          H@sub{2}O

``@symbol{...}``
    Add a symbol

    .. index::
        single: tags; @smb

    :aliases: ``@smb``

    :examples:

       ::
          
          @symbol{alpha}-helix

``@verb{...}``
    Mark text as verbatim--i.e. do not process the text and present
    the text without modification.

    .. index::
        single: tags; @verb

    :tex: In tex, this tag will be rendered as an inline ``\verb||``
          command.
    
    :examples:

       ::

          My @v{@bold{bold}} tag.

``verbatim{...}``
    Mark a *block of text* as verbatim--*i.e.* do not process the
    text and present the text without modification.

    .. index::
         single: tags; @verbatim

    :tex: In tex, this tag will be rendered as a
          ``\begin{verbatim}...\end{verbatime}`` environment.

    :examples:

       ::

          @verbatim{My verbatim text}
