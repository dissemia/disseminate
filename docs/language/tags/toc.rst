.. role:: dm(code)
   :language: dm

Table of Contents
=================

Table of contents are used to create links to headings, content or other
documents.

.. rst-class:: dl-parameter

:dm:`@toc{...}`
    A table of contents

    .. index::
        single: tags; @toc

    :contents\: label types:

        ``document``

           List documents

        ``heading``

            List headings like chapters, sections, subsections and
            subsubsections

        ``figure``

           List figure captions

        ``table``

            List tables

    :contents\: modifiers:

        ``all``

            List entries for all documents. By default, only the entries for
            the current document are listed.

        ``current``

            List entries for the current document only (default)

        ``expanded``

            When ``all documents`` or ``all headings`` is used,
            show all headers for all documents

        ``abbreviated``

            When ``all documents`` or ``all headings`` is used,
            only show headers for the current document and document labels for
            the other documents

        ``collapsed``

            When ``all documents`` or ``all headings`` is used,
            only show the document labels

    :examples:

        .. code-block:: dm

           @toc{headings collapsed}
           @toc{all headings expanded}

