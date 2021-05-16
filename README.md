# Disseminate

[![Build Status](https://travis-ci.com/jlorieau/disseminate.svg?token=4HVxi2sGcJHxUFriAmGB&branch=development)](https://travis-ci.com/jlorieau/disseminate)

Disseminate is a document processing system for textbooks, books, novels, 
articles, reports and essays. 

Disseminate is a markup language, 
like [Markdown](https://daringfireball.net/projects/markdown/) or 
[reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html), 
written in disseminate text format (``.dm``)that aims to be simple to use, to 
have a simple syntax and to contain useful functionality for academics. 
Projects may contain a single document or a tree of interconnected documents 
comprising chapters, raw data, figures and images in a source controlled 
repository. The Disseminate software is coded in 
[Python 3](https://www.python.org) and disseminate projects can be converted 
to static website with ``.html``, ``.txt``, ``.tex``, ``.pdf`` and ``.epub`` 
targets.

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
   build systems, like [Scons](https://scons.org), to detect build changes based
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
v1.0
```

### Check External Dependencies

```shell script
$ dm setup --check
  Checking required dependencies for 'python'                       [  PASS  ]  
    Checking alternative dependencies for 'executables'             [  PASS  ]  
      Checking dependency 'python3.6'                               [  PASS  ]  
      Checking dependency 'python3.7'                               [  PASS  ]  
    Checking required dependencies for 'packages'                   [  PASS  ]  
      Checking dependency 'regex>=2018.11.22'                       [  PASS  ]  
      Checking dependency 'jinja2>=2.10'                            [  PASS  ]  
      Checking dependency 'lxml>=4.3.0'                             [  PASS  ]  
      Checking dependency 'python-slugify>=2.0.1'                   [  PASS  ]  
      Checking dependency 'click>=7.0'                              [  PASS  ]  
      Checking dependency 'pdfCropMargins>=0.1.4'                   [  PASS  ]  
      Checking dependency 'sanic>=19.0'                             [  PASS  ]  
      Checking dependency 'pandas>=0.25'                            [  PASS  ]  
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
      Checking dependency 'hyperref'                                [  PASS  ]  
      Checking dependency 'enumitem'                                [  PASS  ]  
      Checking dependency 'geometry'                                [  PASS  ]  
      Checking dependency 'xcolor'                                  [  PASS  ]  
    Checking alternative dependencies for 'fonts'                   [  PASS  ]  
      Checking dependency 'ecrm1200'                                [  PASS  ]  
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

## Implementation
### Core Components
1. **Document**. A document corresponds to a single disseminate source file. 
   A document may contain subdocuments, which in turn may hold additional 
   subdocuments, to form a project tree. The top-level document is known as a 
   root document, and the root document and all its subdocuments are known as 
   a project. Documents have signals for the creation, loading, deletion and 
   updating of the tree to properly process the source file.
2. **Context**. Each document own a context, which is an object derived from 
   a dict class. The basic settings for rendering a document are stored in a 
   context, and the user may change these values with entries in a document’s 
   header in the disseminate source file.
3. **Tags**. The body of the disseminate source file is placed in the body 
  entry of the context and rendered with the ``@body`` tag. Tags can be nested 
  arbitrarily up to a maximum of 30 recursions. The creation of a tag emits a 
  ``tag_created`` signal and processing of the tag contents and attributes is 
  conducted through receiver functions. The signal/receiver framework allows 
  for the easy and modular extension of new tag processing functionality.
4. **Attributes**. Attributes are parsed into a dict, which is an object 
  derived from an ordered dict. Attributes may be general, like `
  ``id=figure-1``, or they may be specific to a rendered target, like 
  ``-0.25em.tex`` for tex targets. Attributes may also be positional or 
  key-value pairs.
5. **Label Manager**. The label manager tracks the labels created by various 
   tags, like ``@chapter`` or ``@caption``, and creates links to these elements 
   in the rendered target formats using the ``@ref`` tag. The context of the 
   root document (root context) owns the label manager.
6. **Dependency Manager, Checkers and Renderers**. The old build system to 
   convert parsed documents into the rendered target projects, like html and 
   tex. The dependency manager tracks file dependencies for each disseminate 
   document, the checkers find external programs needed for conversions and 
   the renderers convert parsed tags to documents. This system is being 
   replaced by the Builder system.
7. **Templates**. Template files for producing the rendered target files.
8. **Settings**. The default settings and behavior of Disseminate when load 
   and rendering files.

### Utility Components
1. **Signals**. Disseminate uses custom signal/receiver framework inspired by 
   Blinker. This custom signal/receiver framework allows signals to also 
   register an order so that receiver functions can be executed in a specific 
   order.
2. **Paths**. Paths implements the ``SourcePath`` and ``TargetPath`` classes, 
   which are derived from ``pathlib.Path``. The SourcePath parses paths into 
   the ``project_root`` and ``subpath`` components, while the TargetPath 
   parses paths into the ``target_root``, ``target`` and ``subpath`` 
   components. Parsing of the path components is needed to recreate source 
   file tree into the rendered target formats.
3. **Server**. The server component implement a localhost webserver with 
   Sanic to display rendered files and projects.
4. **Formats**. A collection of functions to render tags and text into various 
   target formats, like html and tex. These check allowed tags in the settings.
5. **Utils**. General basic utilities used by multiple core components.

## Roadmap
### Language
1. **Builder**. Implement the Builder framework for building dependencies 
   based on md5 hashes. The builder works asyncronously to speed up builds.
2. **Citation**. Implement the ```@cite``` tag for pulling citations from 
   external sources and rendering them in the correct format.
3. **Plotting**. Implement the ``@plot`` tag to work in conjunction with the 
   ``@data`` tags to render plots.

### UI
1. **Editor**. Implement an editor interface (electron) with syntax 
   highlighting and helper functions to easily edit and submit Disseminate 
   projects.