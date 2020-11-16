.. _installation:

Installation
============

Disseminate can be run locally on the desktop or in a virtual machine through
dissemia.com.

To install disseminate on the desktop, the following *required* software should
be installed:

- Python 3.6+
- Latex environment for rendering PDF files
  (`TeX Live <https://www.tug.org/texlive/>`_, `MacTeX <https://tug.org/mactex/>`_)
- ImageMagick 7.0+
- Asymptote 2.67+
- pdf2svg 0.2.3+
- rsvg-convert 2.50+

.. _installation_macos:

Mac OS (Terminal)
-----------------

1. *Python3*. Check whether python 3.6+ is installed in a terminal.

   .. raw:: html

       <pre class='terminal'>
         <strong><span class='prompt'>$</span> python --version</strong>
         Python 3.7.3
       </pre>


   If python3 is not installed, you can download the latest version of
   `python <https://www.python.org/downloads/mac-osx/>`_  and install it.

2. *LaTeX*. Check whether `MacTeX <https://tug.org/mactex/>`_ or
   `TeX Live <https://www.tug.org/texlive/>`_ are installed.

   .. raw:: html

       <pre class='terminal'>
         <strong><span class='prompt'>$</span> pdflatex --version</strong>
         pdfTeX 3.14159265-2.6-1.40.21 (TeX Live 2020)
         ...
       </pre>

   .. raw:: html

       <pre class='terminal'>
         <strong><span class='prompt'>$</span> tlmgr --version</strong>
         tlmgr revision 56566 (2020-10-06 05:40:54 +0200)
         tlmgr using installation: /usr/local/texlive/2020
         TeX Live (https://tug.org/texlive) version 2020
       </pre>

   If not, you can download `MacTeX <https://tug.org/mactex/>`_ and install it.

3. *Disseminate*. Install disseminate using pip.

   .. raw:: html

       <pre class='terminal'>
         <strong><span class='prompt'>$</span> pip install disseminate</strong>
       </pre>

4. *Additional dependencies*. Check additional dependencies using disseminate.

   .. include:: ../cmds/dm_setup_check.rst

   If some of these dependencies are not preset, they can be installed using
   MacTeX or TeXLive:

   .. raw:: html

       <pre class='terminal'>
         <strong><span class='prompt'>$</span> sudo tlmgr update --self</strong> <span class='comment'># update texlive</span>
       </pre>

       <pre class='terminal'>
         <strong><span class='prompt'>$</span> sudo tlmgr install caption amsmath mathtools easylist fancyvrb hyperref \
         enumitem geometry xcolor collection-fontsrecommended tufte-latex asymptote</strong>
       </pre>

   And they can be installed using `Homebrew <https://brew.sh>`_. Homebrew can
   be `downloaded <https://brew.sh>`_ and installed.

   .. raw:: html

       <pre class='terminal'>
         <strong><span class='prompt'>$</span> brew install pdf2svg librsvg imagemagick</strong>
       </pre>
