Figures
=======

Tags to insert figures

``@marginfig{...}``
   Insert a figure in the margin

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