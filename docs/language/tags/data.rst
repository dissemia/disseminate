.. _language-tags-data:

Data
====

Tags to insert and format data. This tag is used in conjunction with other tags,
like the ``@table`` tag.

.. _tags-data:

``@csv{...}``
   Include comma-separated value (CSV) data.

   .. index::
      single: tags; @data

   :contents:

      Either a path for a file with CSV data or CSV data directly.

   :attributes:

      ``noheader``

         The ``csv`` file does not include header labels in the first line.

Examples
--------

1. The following example loads csv data from a file ``data/class_histogram.csv``
   into a table.

   ::

      @table{
        @csv{data/class_histogram.csv}
      }

2. This example loads csv data directly into a table.

   ::

      @table{
        @csv{
          First Name, Last Name
          John, Smith
          Betty, Sue
          Derek, Johnson
        }
      }

3. This example loads csv data without a header line into a table.

   ::

      @table{
        @csv[noheader]{
          John, Smith
          Betty, Sue
          Derek, Johnson
        }
      }