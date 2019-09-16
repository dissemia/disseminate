Code Fragments
==============

Code highlighting tags are used to represent source code in texts.

``@code{...}``
    Highlight a code fragment

    .. index::
        single: tags; @code

   :contents:

      A code fragment or a path to a source file.

   :attributes:

      ``language``

         The language to use in highlighting the source code fragment.
         See the pygments `lexer <http://pygments.org/docs/lexers/>`_ lexer
         listing.

   :examples:

       ::

          @code[python]{print('hello!')}


``@python{...}``
    Highlight a _python_ code fragment

    .. index::
        single: tags; @python

   :contents:

      A code fragment or a path to a python source file.

   :examples:

       ::

          @python{print('hello!')}


``@html{...}``
    Highlight an _html_ code fragment

    .. index::
        single: tags; @html

   :contents:

      A code fragment or a path to a html source file.

   :examples:

       ::

          @html{<b>hello!</b>}


``@ruby{...}``
    Highlight a _ruby_ code fragment

    .. index::
        single: tags; @ruby

   :contents:

      A code fragment or a path to a ruby source file.

   :examples:

       ::

          @ruby{print "hello!"}

``@java{...}``
    Highlight a _java_ code fragment

    .. index::
        single: tags; @java

   :contents:

      A code fragment or a path to a java source file.

   :examples:

       ::

          @java{System.out.println("hello!" );}

``@javascript{...}``
    Highlight a _javascript_ code fragment

    .. index::
        single: tags; @javascript

   :contents:

      A code fragment or a path to a javascript source file.

   :examples:

       ::

          @javascript{alert('Hello!');}

