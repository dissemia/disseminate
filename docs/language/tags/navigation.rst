.. role:: dm(code)
   :language: dm

Navigation
==========

Navigation tags are used to create html links to other documents, like the
previous or next document.

.. rst-class:: dl-parameter

:dm:`@prev`
    A link to the previous document

    .. index::
        single: tags; @prev

    :attributes:

        ``kind``

           The kind of label to link to create the link to. By default,
           the link is created to the first heading label, like ``@chapter``.

    :examples:

       .. code-block:: dm

          @prev


:dm:`@next`
    A link to the next document

    .. index::
        single: tags; @next

    :attributes:

        ``kind``

           The kind of label to link to create the link to. By default,
           the link is created to the first heading label, like ``@chapter``.

    :examples:

       .. code-block:: dm

          @next

