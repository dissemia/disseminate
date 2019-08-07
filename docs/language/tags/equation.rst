.. _language-tags-eq:

Equations
=========

Tags to insert and format equations

.. _tags-eq:

``@eq{...}``
   Insert an equation

   .. index::
      single: tags; @eq

   :contents:

      The equation in LaTeX format.
      
   :attributes:

      ``env=x``

         The LaTeX environment to use in rendering the equation.  By
         default, equations are rendered inline. Note that additional
         parameters may be needed, depending on the environment.

      ``color=x``

         The color of the equation.

      ``bold``

         Render the equation in bold

   :html: For ``html`` targets, equations are rendered using LaTeX and
          inserted as ``.svg`` files.

   :tex: For ``tex`` targets, equations are integrated directly in the
         ``.tex`` file.
      
   :examples:

      ::

         @eq{y = x}
         @eq[env=align]{y &= x}
         @eq[env=alignat* 2]{y &= x}

Dependencies
------------

``html`` targets
~~~~~~~~~~~~~~~~

Equations are rendered in ``html`` using LaTeX and ``svg``
files. Javascript libraries are available to render
equations. However, these are not used for the following reasons:

1. Javascript must be enabled to view the page properly. Disseminate
   follows the philosophy that javascript is used to *enhance* the
   function of a website. The proper functioning of a website should
   not be impeded if javascript is not available.
2. Rendering of the equations using the same engine for ``pdf`` files
   ensures that these will be shown correctly and in the same way
   between formats. Furthermore, javascript libraries for rendering
   equations often do not support all LaTeX equation functions.
3. Caching and rendering of images is quick in html.

For ``html`` targets, the following software dependencies are needed:

+--------------+----------------------------------------------------+
| Software     | Purpose                                            |
+==============+====================================================+
| pdflatex     | renders the LaTeX ``.tex`` file to a ``.pdf`` file |
+--------------+----------------------------------------------------+
| pdf2svg      | converts the ``.pdf`` file to an ``.svg`` file     |
+--------------+----------------------------------------------------+
| rsvg-convert | scales and crops the ``.svg`` file                 |
+--------------+----------------------------------------------------+

``pdf`` targets
~~~~~~~~~~~~~~~

For ``pdf`` targets, the following software dependencies are needed:

+----------+----------------------------------------------------+
| Software | Purpose                                            |
+==========+====================================================+
| pdflatex | renders the LaTeX ``.tex`` file to a ``.pdf`` file |
+----------+----------------------------------------------------+
