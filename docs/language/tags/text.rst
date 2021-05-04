.. role:: dm(code)
   :language: dm

Text Formatting
===============

Text formatting tags are used to emphasize text in different ways and
to introduce special characters.

.. rst-class:: dl-parameter

:dm:`@bold{...}`
    Emphasize text by with bold

    .. index::
        single: tags; @bold
        single: tags; @b
        single: tags; @textbf

    :aliases: ``@b`` ``@textbf``

    :examples:

       .. code-block:: dm

          @bold{This text is bold!}
          @b{This text is bold!}
          @textbf{This text is bold!}

:dm:`@italics{...}`
    Emphasize text by with italics

    .. index::
        single: tags; @italics
        single: tags; @i
        single: tags; @textit

    :aliases: ``@i`` ``@textit``

    :examples:

       .. code-block:: dm
       
           @italics{This text is in italics}
           @i{This text is in italics}
           @textit{This text is in italics}

:dm:`@sup{...}`
    Superscript text

    .. index::
        single: tags; @sup
        
    :examples:

       .. code-block:: dm
          
          @sup{1}H


:dm:`@sub{...}`
    Subscript text

    .. index::
        single: tags; @sub

    :examples:

       .. code-block:: dm

          H@sub{2}O

:dm:`@supsub{...}`
    A superscript followed by a subscript text. This tag formats the superscript
    directly above the subscript

    .. index::
        single: tags; @supsub

    :content:

        The superscript and the subscript are separated by two ampersands
        (``&&``)

    :examples:

       .. code-block:: dm

          @supsub{12 && 6}C


:dm:`@symbol{...}`
    Add a symbol

    .. index::
        single: tags; @smb

    :aliases: ``@smb``

    :examples:

       .. code-block:: dm
          
          @symbol{alpha}-helix

:dm:`@verb{...}`
    Mark text as verbatim--i.e. do not process the text and present
    the text without modification.

    .. index::
        single: tags; @verb

    :tex: In tex, this tag will be rendered as an inline ``\verb||``
          command.
    
    :examples:

       .. code-block:: dm

          My @v{@bold{bold}} tag.

:dm:`verbatim{...}`
    Mark a *block of text* as verbatim--*i.e.* do not process the
    text and present the text without modification.

    .. index::
         single: tags; @verbatim

    :tex: In tex, this tag will be rendered as a
          ``\begin{verbatim}...\end{verbatime}`` environment.

    :examples:

       .. code-block:: dm

          @verbatim{My verbatim text}
