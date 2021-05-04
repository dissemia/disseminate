.. role:: dm(code)
   :language: dm

.. _language-tags-table:

Tables
======

Tags to insert and format tables

.. _tags-table:

.. rst-class:: dl-parameter

:dm:`@table{...}`
   Insert a table

   .. index::
      single: tags; @table

   :contents:

      A data tag and, optionally, a caption tag.

   :attributes:

      ``id=x``

         The identifier for the table caption

      ``class=x``

         The formatting class for the table

   :examples:

       .. code-block:: dm

         @table{
            @csv{
              First Name, Last Name
              John, Smith
              Betty, Sue
              Derek, Johnson
            }
          }

       The following table includes a csv file and a caption title.

       .. code-block:: dm

         @mtable{
            @caption{Populations by age group for tennis players}
            @csv{data/populations.csv}
          }

:dm:`@margintable{...}`
    Insert a table in the margin

    .. index::
       single: tags; @margintable

    :contents:

        A data tag and, optionally, a caption tag.

    :attributes:

       ``id=x``

         The identifier for the table caption

      ``class=x``

         The formatting class for the table

   :examples:

       .. code-block:: dm

         @margintable{
            @caption{Populations by age group for tennis players}
            @csv{data/populations.csv}
          }

:dm:`@fulltable{...}`
    Insert a table that spans the whole page

    .. index::
       single: tags; @fulltable

    :contents:

        A data tag and, optionally, a caption tag.

    :attributes:

       ``id=x``

         The identifier for the table caption

      ``class=x``

         The formatting class for the table

   :examples:

       The following table includes a csv file and a caption title.

       .. code-block:: dm

         @fullable{
            @caption{Populations by age group for tennis players}
            @csv{data/populations.csv}
          }