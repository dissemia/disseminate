Asymptote Diagrams
==================

Tags to insert and format asymptote diagrams

``@eq{...}``
   Insert an equation

   .. index::
      single: tags; @img

   :attributes:

      ``env`` -- The LaTeX environment to use in rendering the equation.
      By default, equations are rendered inline.

      ``bold`` -- Render the equation in bold

   :html: For ``html`` targets, equations are rendered using LaTeX and
          inserted as ``.svg`` files.

   :tex: For ``tex`` targets, equations are integrated directly in the
         ``.tex`` file.
      
   :examples:

      ::

         @eq{y = x}
         @eq[env=align]{y &= x}
         @eq[env=alignat* 2]{y &= x}
