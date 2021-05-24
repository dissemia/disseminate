# Disseminate

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/dissemia/disseminate)](https://github.com/dissemia/disseminate/releases/latest)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/disseminate)](https://pypi.org/project/disseminate/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CI](https://github.com/dissemia/disseminate/actions/workflows/ci_linux.yml/badge.svg)](https://github.com/dissemia/disseminate/actions/workflows/ci_linux.yml)
[![Documentation Status](https://readthedocs.org/projects/disseminate/badge/?version=latest)](https://docs.dissemia.org/projects/disseminate/en/latest/?badge=latest)

Disseminate is a document processing system for textbooks, books, novels, 
articles, reports and essays. 

Disseminate is a markup language, like [Markdown] or [reStructuredText], 
written in disseminate text format (``.dm``) that aims to be simple to use, 
to have a simple syntax and to contain useful functionality for academics. 
Projects may contain a single document or a tree of interconnected documents 
comprising chapters, raw data, figures and images in a source controlled 
repository. The Disseminate software is coded in [Python 3] and disseminate 
projects can be converted  to static website with ``.html``, ``.txt``, 
``.tex``, ``.pdf`` and ``.epub`` targets.

- **Documentation**: https://docs.dissemia.org/projects/disseminate/en/latest
- **Mailing list**: https://groups.google.com/g/disseminate-usage
- **Source code**: https://github.com/dissemia/disseminate
- **Bug reports**: https://github.com/dissemia/disseminate/issues


## Features
1. **Header and Body**. Disseminate documents may optionally contain a YAML
   header to configure a document and a body written in disseminate syntax.
2. **Document Trees**. Projects can be as simple as one document, or it can be 
   a book comprising multiple parts and chapters.
3. **Uniform Language**. All tags are written with a simple format
   and all tags are allowed. Certain tags have enhanced typesetting 
   functionality, and tags may optionally have attributes to format how a tag is
   rendered. _ex_: ``This is @b{my} sentence.`` or 
   ``@img[width40%]{src/figure-1.png}``.
4. **Macros**. Macros allow users to generate their own tags for repetitive
   code fragments. These are specified in the document header and are available
   to all sub-documents.
5. **Templates and Typography**. A top priority for disseminate is the 
   production of documents that follow good typographical style. Templates are
   available for textbooks with Tufte formatting, books, novels, reports and
   articles.
6. **Internal Labels**. Labels to other documents, chapters, sections, figures 
   and tables are handled consistently and easily to create internal links.
   The formatting of labels are either controlled by the template or, 
   optionally, defined by the user in document headers.
7. **Multiple Target Formats**. Disseminate projects can be rendered as websites
   (``.html``), ``.pdf``, ``.epub``, ``.txt`` or ``.tex``.
8. **Automatic Conversions**. The Disseminate processor includes a customized 
   build automation system. This system creates build recipes for converting
   files in the correct formats, and it includes features similar to other
   build systems, like [Scons], to detect build changes based
   on source file signatures.
9. **Inline Plots and Diagrams**. Tags can handle data and code 
   to be rendered into images, figures and diagrams.
10. **Equations**. Equation tags for rendering equations in LaTeX format.
11. **Version Control**. Document projects are stored in source code 
    repositories, which enable the tracking of changes, the contribution of
    multiple authors and the inclusion of raw data.
12. **Webserver**. A built-in webserver allows users to preview their processed 
    document projects.

## Installation

### Requirements

### From Github

1. (*Optional*) Setup a virtual environment using python 3.7+
```shell script
$ mkvirtualenv -p python3.7 disseminate
```

2. Clone the github repository
```shell script
$ git clone https://github.com/jlorieau/disseminate.git
```

3. Install disseminate
```shell script
$ cd disseminate/
$ make install  ## or python setup.py install
```

4. Check the installed version
```shell script
$ dm --version
v2.3
```

### Check External Dependencies

```shell script
$ dm setup --check
  Checking required dependencies for 'python'                       [  PASS  ]  
    Checking alternative dependencies for 'executables'             [  PASS  ]  
      Checking dependency 'python3.6'                               [MISSING ]  
      Checking dependency 'python3.7'                               [  PASS  ]  
      Checking dependency 'python3.8'                               [  PASS  ]  
      Checking dependency 'python3.9'                               [  PASS  ]  
    Checking required dependencies for 'packages'                   [  PASS  ]  
      Checking dependency 'regex>=2018.11.22'                       [  PASS  ]  
      Checking dependency 'jinja2>=2.11'                            [  PASS  ]  
      Checking dependency 'lxml>=4.3.0'                             [  PASS  ]  
      Checking dependency 'python-slugify>=2.0.1'                   [  PASS  ]  
      Checking dependency 'pdfCropMargins>=0.1.4'                   [  PASS  ]  
      Checking dependency 'click>=7.0'                              [  PASS  ]  
      Checking dependency 'tornado>=6.1'                            [  PASS  ]  
      Checking dependency 'pygments >=2.6'                          [  PASS  ]  
      Checking dependency 'pandas>=1.2'                             [  PASS  ]  
      Checking dependency 'diskcache>=4.1'                          [  PASS  ]  
      Checking dependency 'pathvalidate>=2.2'                       [  PASS  ]  
  Checking required dependencies for 'image external deps'          [  PASS  ]  
    Checking alternative dependencies for 'executables'             [  PASS  ]  
      Checking dependency 'asy'                                     [  PASS  ]  
      Checking dependency 'convert'                                 [  PASS  ]  
      Checking dependency 'pdf2svg'                                 [  PASS  ]  
      Checking dependency 'pdf-crop-margins'                        [  PASS  ]  
      Checking dependency 'rsvg-convert'                            [  PASS  ]  
  Checking required dependencies for 'pdf'                          [  PASS  ]  
    Checking required dependencies for 'executables'                [  PASS  ]  
      Checking alternative dependencies for 'compilers'             [  PASS  ]  
        Checking dependency 'pdflatex'                              [  PASS  ]  
        Checking dependency 'xelatex'                               [  PASS  ]  
        Checking dependency 'lualatex'                              [  PASS  ]  
      Checking alternative dependencies for 'package_managers'      [  PASS  ]  
        Checking dependency 'kpsewhich'                             [  PASS  ]  
    Checking required dependencies for 'packages'                   [  PASS  ]  
      Checking dependency 'graphicx'                                [  PASS  ]  
      Checking dependency 'caption'                                 [  PASS  ]  
      Checking dependency 'amsmath'                                 [  PASS  ]  
      Checking dependency 'mathtools'                               [  PASS  ]  
      Checking dependency 'bm'                                      [  PASS  ]  
      Checking dependency 'easylist'                                [  PASS  ]  
      Checking dependency 'fancyvrb'                                [  PASS  ]  
      Checking dependency 'hyperref'                                [  PASS  ]  
      Checking dependency 'enumitem'                                [  PASS  ]  
      Checking dependency 'geometry'                                [  PASS  ]  
      Checking dependency 'xcolor'                                  [  PASS  ]  
    Checking alternative dependencies for 'fonts'                   [  PASS  ]  
      Checking dependency 'ecrm1200'                                [  PASS  ]  
      Checking dependency 'tcrm1200'                                [  PASS  ]  
    Checking alternative dependencies for 'classes'                 [  PASS  ]  
      Checking dependency 'article'                                 [  PASS  ]  
      Checking dependency 'report'                                  [  PASS  ]  
      Checking dependency 'tufte-book'                              [  PASS  ]
```

### Usage

1. Create a project directory

```shell script
$ mkdir -p ~/Documents/Disseminate/test-project/src
$ cd ~/Documents/Disseminate/test-project
```

2. Create a root document

```shell script
$ echo "@chapter{My First Chapter}" > src/index.dm
```

3. Start the internal webserver

```shell script
$ dm preview
[2020-04-22 13:36:08 -0500] [58827] [INFO] Goin' Fast @ http://127.0.0.1:8899
[2020-04-22 13:36:08 -0500] [58827] [INFO] Starting worker [58827]
```

4. Go to ``http://localhost:8899``
   
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[Python 3]: https://www.python.org
[Scons]: https://scons.org
[documentation]: https://disseminate.dissemia.org
