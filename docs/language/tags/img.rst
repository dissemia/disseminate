.. role:: dm(code)
   :language: dm

Images
======

Tags to insert and format images

.. _tags-img:

.. rst-class:: dl-parameter

:dm:`@img{...}`
   Insert an image.

   .. index::
      single: tags; @img

   :contents:

      The path and filename of the image. The path can be either relative to
      the same directory as the document, the root directory of the project or
      and absolute path.
      
   :attributes:
      
      ``class=x``

         the css class to use for the image in ``html`` targets.
      
      ``width=x%``
      
         the width of the image using the percentage or px

         (for all targets)

      ``height=x``

         the height of the image using the specified number (for all
         targets)

   :target attributes:

      ``width.html=x``

         the width of the image using the specified percentage or px. The width
         is used in the ``<img />`` tag.

         (``html`` targets)

      ``height.html=x``

         the height of the image using the specified number. The height is
         used in the ``<img \>`` tag.

        (``html`` targets)

      ``width.xhtml=x``

         the width of the image using the specified percentage or px. The width
         is used in the ``<img />`` tag.

         (``epub`` and ``xhtml`` targets)

      ``height.xhtml=x``

         the height of the image using the specified number. The height is
         used in the ``<img \>`` tag.

        (``epub`` and ``xhtml`` targets)

      ``width.tex=x``

         the width of the image using the specified percentage or px. The width
         is used in the ``\includegraphics`` macro.

         (``tex`` and ``pdf`` targets)

      ``height.tex=x``

         the height of the image using the specified number. The height is used
         in the ``\includegraphics`` macro.

        (``tex`` and ``pdf`` targets)

   :examples:

      .. code-block:: dm
         
         @img[class=icon]{media/imgs/template.svg}
         @img[tex.width=30% html.width=2.5in]{media/imgs/simulation.svg}
