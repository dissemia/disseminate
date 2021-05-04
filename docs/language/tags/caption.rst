.. role:: dm(code)
   :language: dm

Captions
========

Tags to insert captions for figures and tables

.. rst-class:: dl-parameter

:dm:`@caption{...}`
   Insert a caption

   .. index::
      single: tags; @caption

   :contents:

      The figure caption
      
   :attributes:

      ``id=x``

         The caption marker label

   :notes:

      The ``@caption`` tag is designed to be used with a figure tag or
      a table tag. A naked ``@caption`` is allowed, but a label will
      not be registered for it.
      
   :examples:

      .. code-block:: dm

         @fig{@img{image.svg}
              @caption{My first figure}
              }
              
