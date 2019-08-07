Captions
========

Tags to insert captions for figures and tables

``@caption{...}``
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

      ::

         @fig{@img{image.svg}
              @caption{My first figure}
              }
              
