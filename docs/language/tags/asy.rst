Asymptote Diagrams
==================

Tags to insert and format `asymptote
<http://asymptote.sourceforge.net>`_ vector graphics diagrams

.. _tags-asy:

``@asy{...}``
   Insert an asymptote image

   .. index::
      single: tags; @asy

   :contents:

      The figure in Asymptote syntax.

   :attributes:

      ``scale=x``

         xcale the image by the specified factor

   :html: For ``html`` targets, asymptote images are rendered using
          asymptote and inserted as ``.svg`` files.

   :tex: For ``tex`` targets, asymptote images are inserted
         directly.
      
   :examples:

      ::

         @asy[scale=2.0]{
              size(200);                                                                                                                                             
              draw(unitcircle);
              }

Dependencies
------------

``html`` targets
~~~~~~~~~~~~~~~~

For ``html`` targets, the following software dependencies are needed:

+--------------+----------------------------------------------------+
| Software     | Purpose                                            |
+==============+====================================================+
| asy          | renders the asymptote diagrame to a ``.pdf`` file  |
+--------------+----------------------------------------------------+
| pdf2svg      | converts the ``.pdf`` file to an ``.svg`` file     |
+--------------+----------------------------------------------------+
| rsvg-convert | scales and crops the ``.svg`` file                 |
+--------------+----------------------------------------------------+

``pdf`` targets
~~~~~~~~~~~~~~~

For ``pdf`` targets, the following software dependencies are needed:

+--------------+----------------------------------------------------+
| Software     | Purpose                                            |
+==============+====================================================+
| asy          | renders the asymptote diagrame to a ``.pdf`` file  |
+--------------+----------------------------------------------------+
