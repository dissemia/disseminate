.. _file-converters:

File Converters
===============

File converters work in coordination with the dependency manager to
manage the files needed to render target documents.


``asy`` converters
------------------

.. _asy2pdf:

asy2pdf
   Convert files from ``.asy`` format to ``.pdf`` format.

   .. index::
      single: converter; asy2pdf

   :required software:

      asy

      
.. _asy2svg:

asy2svg
   Convert files from ``.asy`` format to ``.svg`` format.

   .. index::
      single: converter; asy2svg

   :required software:

      asy

   :notes:

      This converter combines the :ref:`asy2pdf <asy2pdf>` and the
      :ref:`pdf2svg <pdf2svg>` converters, and it uses the
      requirements and the tag attributes for these.

      
``pdf`` converters
------------------
      
.. _pdf2svg:

pdf2svg
   Convert files from ``.pdf`` format to ``.svg`` format.

   .. index::
      single: converter; pdf2svg

   :required software:

      `pdf2svg software <https://github.com/dawbarton/pdf2svg>`_

   :optional software:

      `pdfcrop <https://ctan.org/pkg/pdfcrop?lang=en>`_

      `rsvg-convert <https://wiki.gnome.org/Projects/LibRsvg>`_
      
   :tag attributes:

      - ``scale=x.x`` - scale the image by the specified real number
        (for all targets)

      - ``html.scale=x.x`` - scale the image by the specified real
        number (for ``html`` targets only)

      - ``tex.scale=x.x`` - scale the image by the specified real
        number (for ``tex`` or ``pdf`` targets only)

      ..
  
      - ``page=x`` - use the following page(s) from the pdf (for all
        targets)

      - ``html.page=x`` - use the following page(s) from the pdf (for
        ``html`` targets only)

      - ``tex.page=x`` - use the following page(s) from the pdf (for
        ``tex`` and ``pdf`` targets only)
      
   :examples:
   
      ::

         @img[scale=2.0]{assets/graphics.svg}

         
``tex`` converters
------------------
         
.. _tex2pdf:

tex2pdf (pdflatex)
   Convert files from ``.tex`` format to ``.pdf`` format.

   .. index::
      single: converter; tex2pdf

   :required software:

      pdflatex


.. _tex2svg:

tex2svg
   Convert files from ``.tex`` format to ``.svg`` format.

   .. index::
      single: converter; tex2svg

   :notes:

      This converter combines the :ref:`tex2pdf <tex2pdf>` and the
      :ref:`pdf2svg <pdf2svg>` converters, and it uses the
      requirements and tag attributes for these.
