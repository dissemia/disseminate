.. role:: dm(code)
   :language: dm

Asymptote Diagrams
==================

Tags to insert and format `asymptote
<http://asymptote.sourceforge.net>`_ vector graphics diagrams

.. _tags-asy:

.. rst-class:: dl-parameter

:dm:`@asy{...}`
   Insert an asymptote image

   .. index::
      single: tags; @asy

   :contents:

      The figure in Asymptote syntax or the location of an asymptote source
      file.

   :attributes:

      ``scale=x``

         xcale the image by the specified factor

   :html: For ``html`` targets, asymptote images are rendered using
          asymptote and inserted as ``.svg`` files.

   :tex: For ``tex`` targets, asymptote images are inserted
         directly.
      
   :examples:

      .. code-block:: dm

         @asy[scale=2.0]{
              size(200);                                                                                                                                             
              draw(unitcircle);
              }
