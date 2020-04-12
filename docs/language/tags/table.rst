.. _language-tags-table:

Tables
======

Tags to insert and format tables

.. _tags-table:

``@table{...}``
   Insert a table

   .. index::
      single: tags; @table

   :contents:

      A data tag.

   :attributes:

      ``id=x``

         The identifier for the table caption

      ``class=x``

         The formatting class for the table


Examples
--------

1. The following table includes csv data.

   ::

      @table{
        @csv{
          First Name, Last Name
          John, Smith
          Betty, Sue
          Derek, Johnson
        }
      }
