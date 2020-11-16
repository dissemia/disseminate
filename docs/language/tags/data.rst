.. role:: dm(code)
   :language: dm

.. _language-tags-data:

Data
====

Tags to insert data. This tag is used in conjunction with other tags, like the
``@table`` tag.

.. _tags-data:

.. rst-class:: dl-parameter

:dm:`@csv{...}`
   Include comma-separated value (CSV) data.

   .. index::
      single: tags; @data

   :contents:

      Either a path for a file with CSV data or CSV data directly.

   :attributes:

      ``noheader``

         The ``csv`` file does not include header labels in the first line.

   :examples:

       The following example loads csv data from a file
       ``data/class_histogram.csv`` into a table.

       .. code-block:: dm

          @table{
            @csv{data/class_histogram.csv}
          }

       This example loads csv data directly into a table.

       .. code-block:: dm

          @table{
            @csv{
              First Name, Last Name
              John, Smith
              Betty, Sue
              Derek, Johnson
            }
          }

       This example loads csv data without a header line into a table.

       .. code-block:: dm

          @table{
            @csv[noheader]{
              John, Smith
              Betty, Sue
              Derek, Johnson
            }
          }
