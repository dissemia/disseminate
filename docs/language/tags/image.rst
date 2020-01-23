Images
======

Tags to insert and format images

.. _tags-img:

``@img{...}``
   Insert an image.

   .. index::
      single: tags; @img

   :contents:

      The path and filename of the image.
      
   :attributes:
      
      ``class=x``

         the css class to use for the image in ``html`` targets.
      
      ``width=x%``
      
         the width of the image using the percentage or px

         (for all targets)

      ``width.html=x``
      
         the width of the image using the specified percentage or px. The width
         is used in the ``<img />`` tag.

         (``html`` targets)

      ``width.tex=x``

         the width of the image using the specified percentage or px. The width
         is used in the ``\includegraphics`` macro.

         (``tex`` and ``pdf`` targets)
         
      ``height=x``

         the height of the image using the specified number (for all
         targets)

      ``height.html=x``

         the height of the image using the specified number (for
         ``html`` targets only). The height is used in the ``<img \>``
         tag.

      ``height.tex=x``

         the height of the image using the specified number (for
         ``tex`` targets only). The height is used in the
         ``\includegraphics`` macro.

      .. note:: attribute options for specific image types can be
                found in the :ref:`dependency-manager` and
                :ref:`file-converters` tools.

   :examples:

      ::
         
         @img[class=icon]{media/imgs/template.svg}
         @img[tex.width=30% html.width=2.5in]{media/imgs/simulation.svg}
