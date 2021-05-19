# Contributing to Disseminate

The following lists the guidelines for contributing to the Disseminate community
and for contributing source code to the project.

## Where to Start?

Do you want to contribute to Disseminate, but you're unsure where to start?
Here are a few suggestions:

1. **Code Contributions**. We welcome [Pull Requests](#pull-requests) for the
   following:

    1. **Documentation**. We aim to have [documentation] that is easy to read,
       complete and accurate.
   
    2. **Templates**. Our templates should be clean, easy to use and follow
       good typographical style.
       
    3. **UI**. The User Interface should be simple, clean and easy to use.    
       
    4. **Core Code**. New features are implemented by coding them.
    
2. **Sponsorship**

## Code of Conduct

Members of the community are expected to follow the 
[Disseminate Code of Conduct], which is modeled against the 
[Contributor Code of Conduct v2.0]. Please report unacceptable behavior to
codeofconduct {at} dissemia {dot} org.

## Project Organization

### Branches

1. **``master``**. The ``master`` branch is used for releases. It should always 
   be in a stable state and pass all tests.
   
2. **``development``**. The ``development`` branch is used for pre-releases. It 
   should always pass all [pytest], [tox] and CI tests.
    
3. **git flow**. Additional branches should follow the [git flow] branching 
   model with ``feature/``, ``release/`` and ``hotfix`` prefixes. When all new 
   and old tests pass, these may be merged into the ``development`` branch 
   before being merged to the ``master`` branch.

### Feature Requests

The community is open to all feature requests. However, the following 
considerations will be evaluated in deciding whether a feature is
integrated into the project.

1. **Dependencies**. Disseminate has many external dependencies. The following
   factors impact their inclusion: 

   1. **Javascript**. Javascript should not be _required_ to view and properly
      render documents. Do not expect users to have javascript enabled. 
      Javacript can be used to *enhance* functionality on rendered 
      webpages.
      
   2. **Accessible**. The external dependency should be easy to install with
      Disseminate or small enough to be statically linked or included in 
      Disseminate packages.
      
   3, **Open**. External dependencies should use an open source license.
   
2. **Typesetting**. A major objective for Disseminate products is to follow
   proper typographic style and to produce highly readable and clean rendered
   documents. For template authors and contributors, we recommend reading 
   [Elements of Typographic Style]. 
   
   General guidelines:
   
   1. No auto-play animations or graphics
   
   2. The document UI must be unobtrusively. The objective is to have all 
      UI elements contained within the menu so that the document only
      presents information pertinent to the document.
   
   3. Maintain the vertical phase within text sections--_i.e._ do not
      change the line height within a text section
      
   4. Maintain line lengths of 70-90 characters and line heights of 120-140%
      the font height
      
   5. Font families and sizes should not change within a text. Exceptions
      include headings, captions, equations, code blocks and quotes.
      
   6. Indentation should by consistent and use a consistent typographical
      unit--_e.g._ 2_em_.
      
   7. Paragraphs can be indented if there is no line spacing between paragraphs.
      Otherwise, a line spacing of 1 line height is placed between paragraphs.
   
   8. Multicolumn formats are outdated. These formats were developed to
      generate a high print density on pages that were expensive to print
      while only moderately compromising on readability. In the digital age,
      print density is no longer an issue. 
   
3. **Consistency**. A major objective of the Disseminate language is to make
   usage intuitive, simple and powerful. 
   
   1. Documents headers impact the document's metadata or the rendering
      elements of a document and its subdocuments
      
   2. If a feature can be implemented as a tag, it should be
   
   3. All tags follow the ``@tag`` format with an optional 
   attribute--_e.g._ ``@tag[attr=True]{My Tag}``
   
   4. Tag contents dictate _what_ is displayed
   
   5. Tag attributes dictate _how_ something is displayed
   
4. **Static Content**. Vector graphics and formats (``.svg``, ``.pdf``) are 
   more desirable than raster formats (``.png``, ``.jpg``, ``.gif``).
   This is because these can be rendered at arbitrary resolutions.

5. **Secure**. Code should not introduce vulnerabilities to users or to
   consumers--_i.e._ those that read documents produced by disseminate.
   
6. **Fast**. Compilation times for disseminate documents should be fast
   enough to quickly view changes in a rendered document.

## Issues and Questions

Feature requests, usability enhancements and bug reports should be reported
on the Github [issue tracker]. We have provided the following issue templates
to speed up the resolution of issues:

  1. [Feature Requests]
  2. [Bug Report]

Usage questions should be posted on the [disseminate-usage] group.

## Pull Requests

Pull requests are the mechanism used to integrate changes into the Disseminate
code.

  1. Make [pull requests from forks] of the Disseminate source code
  
  2. Pull requests should be implemented on a new branch with a unique name
  
  3. Pull requests that close [issues](#issues-and-questions) should reference
     the issue in the commit message. _e.g._ Closes #42
     
  4. Commit messages should include actions words in the present tense.
     _e.g._ Implement tag aliases and closes #42
     
  5. Pull requests should include new tests for new features or changes to
     tests. Pull requests that break tests will not be merged into development
     if they break tests.
     
  6. Pull requests should follow the [coding style](#coding-style) guidelines

## Coding Style

1. **PEP8 and flake8**. Code should follow the [PEP8] style guide and pass
   flake8 tests (``tox -e flake8``)

2. **Line length**. Line length is limited to a maximum of 79 characters

3. **Numpy docstrings**. Docstrings follow the [numpy docstring format] with
   docstring types written using Python 3 annotations.

### Exceptions for Tests

Tests follow the same guidelines but the following exceptions are allowed:

1. **Line length**. Line length may be longer than 79 characters if needed.
   This is helpful for checking against output strings in formats like html
   (Flake8 E501 error)
   
2. **Code Complexity**. Code complexity is limited to a value of 10 by default.
   Some tests may have an increased complexity from this limit (Flake8 C901
   error)

## Versions

Releases are identified using [semantic versioning] with the format
``MAJOR.MINOR.PATCH[.dev#|a#|b#|rc#]``. Version updates includes the following
steps:

1. Update the ``VERSION`` variable in ``src/__version__.py``

2. Tag a commit with the new version. _e.g._ v2.3


[documentation]: https://www.dissemia.dev/docs/disseminate/index.html
[Disseminate Code of Conduct]: https://github.com/jlorieau/disseminate/blob/master/CODE_OF_CONDUCT.md
[Contributor Code of Conduct v2.0]: https://www.contributor-covenant.org/version/2/0/code_of_conduct.html
[pytest]: https://pypi.org/project/pytest/
[tox]: https://tox.readthedocs.io/en/latest/
[git flow]: https://nvie.com/posts/a-successful-git-branching-model/
[Elements of Typographic Style]: https://en.wikipedia.org/wiki/The_Elements_of_Typographic_Style
[issue tracker]: https://github.com/jlorieau/disseminate/issues
[Feature Requests]: https://github.com/jlorieau/disseminate/issues/new?assignees=&labels=&template=feature_request.md&title=
[Bug Report]: https://github.com/jlorieau/disseminate/issues/new?assignees=&labels=&template=bug_report.md&title=
[disseminate-usage]: https://groups.google.com/g/disseminate-usage
[pull requests from forks]: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork
[PEP8]: https://www.python.org/dev/peps/pep-0008/
[numpy docstring format]: ttps://numpydoc.readthedocs.io/en/latest/format.html
[semantic versioning]: https://semver.org
