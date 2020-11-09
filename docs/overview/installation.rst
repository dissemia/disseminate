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


   If python3 is not installed, you can
   `download <https://www.python.org/downloads/mac-osx/>`_ the latest version
   and install it.

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

   If not, you can `download <https://tug.org/mactex/>`_ and install MacTeX.

3. *Disseminate*. Install disseminate using pip.

   .. raw:: html

       <pre class='terminal'>
         <strong><span class='prompt'>$</span> pip install disseminate</strong>
       </pre>

4. *Additional dependencies*. Check additional dependencies using disseminate.

   .. raw:: html

       <pre class='terminal'>
         <strong><span class='prompt'>$</span> dm setup --check</strong>
          Checking required dependencies for 'python'                       <span class='green'>[  PASS  ]</span>
            Checking alternative dependencies for 'executables'             <span class='green'>[  PASS  ]</span>
              Checking dependency 'python3.6'                               <span class='green'>[  PASS  ]</span>
              Checking dependency 'python3.7'                               <span class='green'>[  PASS  ]</span>
              Checking dependency 'python3.8'                               <span class='green'>[  PASS  ]</span>
              Checking dependency 'python3.9'                               <span class='yellow'>[MISSING ]</span>
            Checking required dependencies for 'packages'                   <span class='green'>[  PASS  ]</span>
              Checking dependency 'regex>=2018.11.22'                       <span class='green'>[  PASS  ]</span>
              Checking dependency 'jinja2>=2.10'                            <span class='green'>[  PASS  ]</span>
              Checking dependency 'lxml>=4.3.0'                             <span class='green'>[  PASS  ]</span>
              Checking dependency 'python-slugify>=2.0.1'                   <span class='green'>[  PASS  ]</span>
              Checking dependency 'pdfCropMargins>=0.1.4'                   <span class='green'>[  PASS  ]</span>
              Checking dependency 'click>=7.0'                              <span class='green'>[  PASS  ]</span>
              Checking dependency 'sanic>=19.0'                             <span class='green'>[  PASS  ]</span>
              Checking dependency 'pygments >=2.6'                          <span class='green'>[  PASS  ]</span>
              Checking dependency 'pandas>=0.25'                            <span class='green'>[  PASS  ]</span>
              Checking dependency 'diskcache>=4.1'                          <span class='green'>[  PASS  ]</span>
              Checking dependency 'pathvalidate>=2.2'                       <span class='green'>[  PASS  ]</span>
          Checking required dependencies for 'image external deps'          <span class='green'>[  PASS  ]</span>
            Checking alternative dependencies for 'executables'             <span class='green'>[  PASS  ]</span>
              Checking dependency 'asy'                                     <span class='green'>[  PASS  ]</span>
              Checking dependency 'convert'                                 <span class='green'>[  PASS  ]</span>
              Checking dependency 'pdf2svg'                                 <span class='green'>[  PASS  ]</span>
              Checking dependency 'pdf-crop-margins'                        <span class='green'>[  PASS  ]</span>
              Checking dependency 'rsvg-convert'                            <span class='green'>[  PASS  ]</span>
          Checking required dependencies for 'pdf'                          <span class='green'>[  PASS  ]</span>
            Checking required dependencies for 'executables'                <span class='green'>[  PASS  ]</span>
              Checking alternative dependencies for 'compilers'             <span class='green'>[  PASS  ]</span>
                Checking dependency 'pdflatex'                              <span class='green'>[  PASS  ]</span>
                Checking dependency 'xelatex'                               <span class='green'>[  PASS  ]</span>
                Checking dependency 'lualatex'                              <span class='green'>[  PASS  ]</span>
              Checking alternative dependencies for 'package_managers'      <span class='green'>[  PASS  ]</span>
                Checking dependency 'kpsewhich'                             <span class='green'>[  PASS  ]</span>
            Checking required dependencies for 'packages'                   <span class='green'>[  PASS  ]</span>
              Checking dependency 'graphicx'                                <span class='green'>[  PASS  ]</span>
              Checking dependency 'caption'                                 <span class='green'>[  PASS  ]</span>
              Checking dependency 'amsmath'                                 <span class='green'>[  PASS  ]</span>
              Checking dependency 'mathtools'                               <span class='green'>[  PASS  ]</span>
              Checking dependency 'bm'                                      <span class='green'>[  PASS  ]</span>
              Checking dependency 'easylist'                                <span class='green'>[  PASS  ]</span>
              Checking dependency 'fancyvrb'                                <span class='green'>[  PASS  ]</span>
              Checking dependency 'hyperref'                                <span class='green'>[  PASS  ]</span>
              Checking dependency 'enumitem'                                <span class='green'>[  PASS  ]</span>
              Checking dependency 'geometry'                                <span class='green'>[  PASS  ]</span>
              Checking dependency 'xcolor'                                  <span class='green'>[  PASS  ]</span>
            Checking alternative dependencies for 'fonts'                   <span class='green'>[  PASS  ]</span>
              Checking dependency 'ecrm1200'                                <span class='green'>[  PASS  ]</span>
            Checking alternative dependencies for 'classes'                 <span class='green'>[  PASS  ]</span>
              Checking dependency 'article'                                 <span class='green'>[  PASS  ]</span>
              Checking dependency 'report'                                  <span class='green'>[  PASS  ]</span>
              Checking dependency 'tufte-book'                              <span class='green'>[  PASS  ]</span>
       </pre>

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
