# Disseminate

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/dissemia/disseminate)](https://github.com/dissemia/disseminate/releases/latest)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/disseminate)](https://pypi.org/project/disseminate/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CI](https://github.com/dissemia/disseminate/actions/workflows/ci_linux.yml/badge.svg)](https://github.com/dissemia/disseminate/actions/workflows/ci_linux.yml)
[![Documentation Status](https://readthedocs.org/projects/disseminate/badge/?version=latest)](https://docs.dissemia.org/projects/disseminate/en/latest/?badge=latest)

Disseminate is a document processing system and static site generator for 
textbooks, books, novels, articles, reports and essays. 

Disseminate is a markup language, like [Markdown] or [reStructuredText], 
written in disseminate text format (``.dm``) that aims to be simple to use, 
to have a simple syntax and to contain useful functionality for academic
and non-academics. Projects may contain a single document or a tree of 
interconnected documents comprising chapters, raw data, figures and images in 
a source controlled repository. The Disseminate software is coded in 
[Python 3] and disseminate projects can be converted to a static website 
with ``.html``, ``.txt``, ``.tex``, ``.pdf`` and ``.epub`` targets.

- **Documentation**: https://docs.dissemia.org/projects/disseminate/en/latest
- **Mailing list**: https://groups.google.com/g/disseminate-usage
- **Source code**: https://github.com/dissemia/disseminate
- **Bug reports**: https://github.com/dissemia/disseminate/issues


## Features

1. [**Header and Body**]. Disseminate documents may optionally contain a YAML
   header to configure a document and a body written in disseminate syntax.
2. [**Document Trees**]. Projects can be as simple as one document, or it can 
   be a book comprising multiple parts and chapters.
3. [**Uniform Language**]. All tags are written with a simple format
   and all tags are allowed. Certain tags have enhanced typesetting 
   functionality, and tags may optionally have attributes to format how a tag 
   is rendered. \
   *ex*: ``This is @b{my} sentence.`` or ``@img[width=40%]{src/figure-1.png}``.
4. [**Macros**]. Macros allow users to generate their own tags for repetitive
   code fragments. These are specified in the document header and are available
   to all sub-documents.
5. [**Templates and Typography**]. A top priority for Disseminate is the 
   production of documents that follow good typographical style. Templates are
   available for textbooks with Tufte formatting, books, novels, reports and
   articles.
6. [**Internal Labels**]. Labels to other documents, chapters, sections, 
   figures and tables are handled consistently and easily to create internal 
   links. The formatting of labels are either controlled by the template or, 
   optionally, defined by the user in document headers.
7. [**Multiple Target Formats**]. Disseminate projects can be rendered as 
   websites (``.html``), ``.pdf``, ``.epub``, ``.txt`` or ``.tex``.
8. [**Automatic Conversions**]. The Disseminate processor includes a customized 
   build automation system. This system creates build recipes for converting
   files in the correct formats, and it includes features similar to other
   build systems, like [Scons], to detect build changes based
   on source file signatures.
9. [**Inline Plots and Diagrams**]. Tags can handle raw data and code, which
   are then automatically rendered into images, figures and diagrams.
10. [**Equations**]. Tags for rendering equations in LaTeX format. \
    *ex*: ``This equation, @eq{y = mx + b}, is inline``
11. [**Webserver**]. A built-in webserver allows users to preview their 
    processed document projects.
12. **Version Control**. Document projects are stored in source code 
    repositories, which enable the tracking of changes, the contribution of
    multiple authors and the inclusion of raw data.

    
### Advanced Features

1. [**Document Inheritance**]. Entries in a document's header will impact how
   that document is rendered as well as how all of its sub-documents are
   rendered.
2. [**Target Attributes**]. Tag attributes may include target specifiers to
   change how a tag is rendered in different target formats. \
   *ex:* ```@img[width=80% width.html=40%]{figures/fig1.png}```
3. [**Label Formats**]. The rendering of label captions and reference links
   can be customized for a document or for a project in the root document.
4. [**Signals**]. Processing functions use a built-in ordered signals
   framework to easily insert processing steps and to create plug-ins. 


## Installation

Disseminate is current available for *MacOS* and *Linux* operating systems.

Disseminate can be  installed with [pip], [Homebrew] or as a github 
clone (Step 1). The base Disseminate installation can render documents 
in ```html```, ```txt``` and ```epub``` formats. 

*Optional*, additional dependencies may be installed (Step 2) to render
documents in ```pdf``` format and to include converters (builders) in 
different formats (Step 2).

The following installation options require an open terminal in MacOS or Linux.

### Step 1: Disseminate (Base Installation)

#### Option 1: Homebrew (MacOS and Linux)

```shell script
brew install dissemia/dissemia/disseminate
```

#### Option 2: Pip (MacOS and Linux)

```shell script
pip install disseminate
```

_(Optional)_ To render in ``pdf`` format, install either [MacTeX], [TeX Live]
or some other distribution. These and other dependencies can be installed with
a package manager like [Homebrew] or ```apt get install```.

#### Option 3: Github (MacOS and Linux)

The github repository can be installed in a python virtual environment. The
base Disseminate project can be used to render documents in ``html`` and
```epub``` formats. 

1. (*Optional*) Setup a virtual environment using python 3.7+
```shell script
mkvirtualenv -p python3.7 disseminate
```

2. Clone the github repository
```shell script
git clone https://github.com/dissemia/disseminate.git
```

3. Install disseminate
```shell script
cd disseminate/
make install  ## or python setup.py install
```

### Step 2: Additional Dependencies

#### LaTeX with Homebrew (MacOS and Linux)

Homebrew can be used to install a basic LaTeX distribution of [TeXLive].

```shell script
brew install --cask basictex
bash --login
```

After install ```basictex```, additional LaTeX packages are install with
TeX Live.

```shell script
sudo tlmgr update --self
sudo tlmgr install easylist enumitem tufte-latex
```

#### LaTeX with TeX Live (MacOS and Linux)

Alternatively, [TeXLive] can be installed from the [TeXLive] website. Once
installed, additional packages are installed as follows:

```shell script
sudo tlmgr update --self
sudo tlmgr install easylist enumitem tufte-latex
```

### Check External Dependencies

Disseminate uses a variety of external tools to convert files and render
documents. If these tools are available, the corresponding converter (Builder)
will be available as well. To view which external dependencies were found
by Disseminate, type the following command.

```shell script
dm setup --check
```

The output should be similar to the following:

```shell script
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

An entry with ```PASS``` indicates that the dependency was found. If a
dependency is missing, we recommend installing it with [Homebrew] or 
```apt install```.

### Usage

1. Create a project directory

```shell script
mkdir -p ~/Documents/Disseminate/test-project/src
cd ~/Documents/Disseminate/test-project
```

2. Create a root document

```shell script
echo "@chapter{My First Chapter}" > src/index.dm
```

3. Start the internal webserver

```shell script
dm preview
[2020-04-22 13:36:08 -0500] [58827] [INFO] Goin' Fast @ http://127.0.0.1:8899
[2020-04-22 13:36:08 -0500] [58827] [INFO] Starting worker [58827]
```

4. Go to ``http://localhost:8899``
   
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[Python 3]: https://www.python.org
[Scons]: https://scons.org
[documentation]: https://disseminate.dissemia.org
[MacTeX]: http://www.tug.org/mactex/
[TexLive]: https://www.tug.org/texlive/
[Pip]: https://pypi.org/project/pip/
[pip]: https://pypi.org/project/pip/
[Homebrew]: https://brew.sh
[**Header and Body**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-basic.html#header-and-body
[**Document Trees**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-basic.html#document-trees
[**Uniform Language**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-basic.html#uniform-language 
[**Macros**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-basic.html#macros
[**Templates and Typography**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-basic.html#templates-and-typography
[**Internal Labels**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-basic.html#internal-labels
[**Multiple Target Formats**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-basic.html#multiple-target-formats
[**Automatic Conversions**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-basic.html#automatic-conversions
[**Inline Plots and Diagrams**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-basic.html#inline-plots-and-diagrams
[**Equations**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-basic.html#equations
[**Webserver**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-advanced.html#webserver-preview
[**Document Inheritance**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-advanced.html#document-inheritance
[**Target Attributes**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-advanced.html#target-attributes
[**Label Formats**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-advanced.html#label-formats
[**Signals**]: https://docs.dissemia.org/projects/disseminate/en/latest/overview/features-advanced.html#signal-processing
