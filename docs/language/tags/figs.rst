Figures
=======

Tags to insert figures

``@marginfig{...}``
   Insert a figure in the margin

   .. index::
      single: tags; @marginfig

   :aliases: ``@marginfigure``

   :contents:

      An ``@img`` tag and, optionally, a ``@caption`` tag
      
   :attributes:

      ``id=x``

         The margin figure's marker label

      ``height_offset.tex``

         **(Tufte template)** offset the margin figure by the given vertical
         dimension. (*ex:* ``-15em.tex``)
      
   :examples:

      ::

         @marginfig[id=my-graph]{
            @img{media/graph.svg}
            @caption{My first graph}
         }

        @marginfig[-15em.tex]{
            @img{media/graph.svg}
            @caption{My second graph}
         }


``@fig{...}``
   Insert a figure in the main text.

   .. index::
      single: tags; @fig
      single: tags; @figure

   :aliases: ``@figure``

   :contents:

      An ``@img`` tag and, optionally, a ``@caption`` tag

   :attributes:

      ``id=x``

         The figure's marker label

   :examples:

      ::

         @fig[id=my-graph]{
            @img{media/graph.svg}
            @caption{My first graph}
              }


``@fullfig{...}``
   Insert a full figure that spans the main text and margin.

   .. index::
      single: tags; @ffig
      single: tags; @fullfigure
      single: tags; @fullfig

   :aliases: ``@fullfigure``, ``@ffig``

   :contents:

      An ``@img`` tag and, optionally, a ``@caption`` tag

   :attributes:

      ``id=x``

         The figure's marker label

   :examples:

      ::

         @fullfig[id=my-graph]{
            @img{media/graph.svg}
            @caption{My first graph}
              }


``@panel{...}``
   Insert a panel in a figure.

   .. index::
      single: tags; @panel

   :contents:

      An ``@img`` tag and text

   :attributes:

      ``width="x"``

         The panel's width in percentage, px units

      ``width.html="x"``

         The panel's width in percentage, px units (for ``html`` targets)

      ``width.tex="x"``

         The panel's width in percentage, px units (for ``tex`` targets)

   :examples:

      ::

         @panel[width=30%]{
            @img{media/graph.svg}
              }