Figures
=======

Tags to insert figures

``@marginfig{...}``
   Insert an margin figure

   .. index::
      single: tags; @marginfig

   :contents:

      An ``@img`` tag and, optionally, a ``@caption`` tag
      
   :attributes:

      ``id=x``

         The margin figure's marker label
      
   :examples:

      ::

         @marginfig[id=my-graph]{
            @img{media/graph.svg}
            @caption{My first graph}
              }
