.. role:: dm(code)
   :language: dm

.. _language-tags-eq:

Equations
=========

Tags to insert and format equations

.. _tags-eq:

.. rst-class:: dl-parameter

:dm:`@eq{...}`
   Insert an equation

   .. index::
      single: tags; @eq

   :contents:

      The equation in LaTeX format.
      
   :attributes:

      ``env=x``

         The LaTeX environment to use in rendering the equation.  By
         default, equations are rendered inline within paragraphs or as
         ``align*`` environments for block equations. Note that additional
         parameters may be needed, depending on the environment.

      ``color=x``

         The color of the equation.

      ``bold``

         Render the equation in bold

   :html: For ``html`` targets, equations are rendered using LaTeX and
          inserted as ``.svg`` files.

   :tex/pdf: For ``tex`` targets, equations are integrated directly in the
             ``.tex`` file.

   :epub/xhtml: For ``epub`` and ``xhtml`` targets, equations are rendered
                using LaTeX and inserted as ``.svg`` files.

   :examples:

      .. code-block:: dm

         @eq{y = x}
         @eq[env=align]{y &= x}
         @eq[env=alignat* 2]{y &= x}
