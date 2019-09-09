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
      
         the width of the image using the percentage

         (for all targets)

      ``html.width=x``
      
         the width of the image using the specified percentage. The width
         is used in the ``<img />`` tag.

         (``html`` targets)

      ``tex.width=x``

         the width of the image using the specified percentage. The width
         is used in the ``\includegraphics`` macro.

         (``tex`` and ``pdf`` targets)
         
      ``height=x``

         the height of the image using the specified number (for all
         targets)

      ``html.height=x``

         the height of the image using the specified number (for
         ``html`` targets only). The height is used in the ``<img \>``
         tag.

      ``tex.height=x``

         the height of the image using the specified number (for
         ``tex`` targets only). The height is used in the
         ``\includegraphics`` macro.

      .. note:: attribute options for specific image types can be
                found in the :ref:`dependency-manager` and
                :ref:`file-converters` tools.

   :examples:

      ::
         
         @img[class=icon]{media/imgs/template.svg}
         @img[tex.width=30% html.width=15%]{media/imgs/simulation.svg}
