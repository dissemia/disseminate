.. role:: dm(code)
   :language: dm

References
==========

Reference tags create links to other documents and content like figures and
tables.

.. rst-class:: dl-parameter

:dm:`@ref{...}`
    A reference to a label

    .. index::
        single: tags; @ref

    :content:

        The unique label identifer (``label_id``) for the content element.
        The ``label_id`` must be unique for each document. If a ``label_id`` is
        reused between multiple documents, then the ``doc_id`` must also be
        specified with 2 colons as separator. *i.e.* ``doc_id::label_id``. The
        ``doc_id`` can be specified in the :ref:`header`.

    :examples:

        .. code-block:: dm

            @ref{chap1::intro}
            @ref{fig:overview}
