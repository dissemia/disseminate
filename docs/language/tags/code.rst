.. role:: dm(code)
   :language: dm

Code Fragments
==============

Code highlighting tags are used to represent source code in texts using
`pygments <http://pygments.org>`_.

.. rst-class:: dl-parameter

:dm:`@code{...}`
    Highlight a code fragment

    .. index::
        single: tags; @code

   :contents:

      A code fragment or a path to a source file.

   :attributes:

      ``language``

         The language to use in highlighting the source code fragment.
         See the pygments /docs/lexers/>`_ lexer
         listing.

   :examples:

       .. code-block:: dm

          @code[python]{print('hello!')}

:dm:`@dm{...}`
    Highlight *disseminate* code fragment

    .. index::
        single: tags; @dm

   :contents:

      A code fragment or a path to a dm source file.

   :examples:

       .. code-block:: dm

          @dm{@b{hello!')}

:dm:`@python{...}`
    Highlight a *python* code fragment

    .. index::
        single: tags; @python

   :contents:

      A code fragment or a path to a python source file.

   :examples:

       .. code-block:: dm

          @python{print('hello!')}


:dm:`@html{...}`
    Highlight an *html* code fragment

    .. index::
        single: tags; @html

   :contents:

      A code fragment or a path to a html source file.

   :examples:

       .. code-block:: dm

          @html{<b>hello!</b>}


:dm:`@ruby{...}`
    Highlight a *ruby* code fragment

    .. index::
        single: tags; @ruby

   :contents:

      A code fragment or a path to a ruby source file.

   :examples:

       .. code-block:: dm

          @ruby{print "hello!"}

:dm:`@java{...}`
    Highlight a *java* code fragment

    .. index::
        single: tags; @java

   :contents:

      A code fragment or a path to a java source file.

   :examples:

       .. code-block:: dm

          @java{System.out.println("hello!" );}

:dm:`@javascript{...}`
    Highlight a *javascript* code fragment

    .. index::
        single: tags; @javascript

   :contents:

      A code fragment or a path to a javascript source file.

   :examples:

       .. code-block:: dm

          @javascript{alert('Hello!');}
