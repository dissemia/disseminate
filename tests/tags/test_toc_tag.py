"""
Test the TOC tag.
"""
import pathlib

from disseminate.tags.toc import Toc

# setup example paths

# examples/toc_ex1
# ├── file1.dm
#    @section{Heading 1}
#    @section{Heading 2}
#    @subsection{sub-Heading 2.1}
#    @subsection{sub-Heading 2.2}
#    @subsubsection{sub-sub-Header 2.2.1}
#    @subsection{sub-Heading 2.3}
#    @section{Heading 3}
#    @subsubsection{sub-sub-header 3.1.1}
#    @section{Heading 4}
# └── sub
#     ├── file21.dm
#     └── file22.dm
ex1_root = pathlib.Path('tests') / 'tags' / 'examples' / 'toc_ex1'

# examples/toc_ex2
# ├── file1.dm
#    @section[id=heading-1]{Heading 1}
# ├── file2.dm
#    @section[id=heading-2]{Heading 2}
#    @subsection[id=subheading-2]{sub-Heading 2}
# └── file3.dm
#    @section[id=heading-3]{Heading 3}
ex2_root = pathlib.Path('tests') / 'tags' / 'examples' / 'toc_ex2'


# Tests for methods

def test_toc_get_labels(load_example):
    """Test the get_labels_by_kind method."""

    # 1. The 'tests/tags/examples/toc_ex2' directory contains three markup
    # files:
    #     file1.dm, file2.dm and file3.dm. The 'file1.dm' includes
    #     'file2.dm' and 'file3.dm'. Each file has 1 section, and file2.dm
    #     also has a subsection.
    doc = load_example(ex2_root / 'file1.dm')

    # 1.a. Test a full listing of headings
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    # There should be 4 labels: 1 for file1.dm, file3.dm and 2 for file2.dm
    labels = toc.get_labels()
    assert len(labels) == 4
    assert labels[0].kind == ('heading', 'section')
    assert labels[0].order == (1, 1)
    assert labels[1].kind == ('heading', 'section')
    assert labels[1].order == (2, 2)
    assert labels[2].kind == ('heading', 'subsection')
    assert labels[2].order == (3, 1)
    assert labels[3].kind == ('heading', 'section')
    assert labels[3].order == (4, 3)

    # 1.a. Test an abbreviated listing of headings. It should include all
    #      headings for the main document (file1.dm) and only 1 heading for
    #      each of the other documents.
    toc = Toc(name='toc', content='all headings abbreviated', attributes='',
              context=doc.context)

    # There should be 3 labels: 1 for each file
    labels = toc.get_labels()
    assert len(labels) == 3
    assert labels[0].kind == ('heading', 'section')
    assert labels[0].order == (1, 1)
    assert labels[1].kind == ('heading', 'section')
    assert labels[1].order == (2, 2)
    assert labels[2].kind == ('heading', 'section')
    assert labels[2].order == (4, 3)


def test_toc_reference_tags(load_example):
    """Test the get_labels_by_kind method."""

    # 1. The 'tests/tags/examples/toc_ex2' directory contains three markup
    #    files:
    #     file1.dm, file2.dm and file3.dm. The 'file1.dm' includes
    #     'file2.dm' and 'file3.dm'. Each file has 1 section, and file2.dm
    #     also has a subsection.
    doc = load_example(ex2_root / 'file1.dm')

    # 1.a. Test a full listing of headings
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    # There should be 4 labels: 1 for file1.dm, file3.dm and 2 for file2.dm
    tags = toc.reference_tags
    assert len(tags) == 4
    assert tags[0].name == 'toc-section'
    assert tags[0].attributes['level'] == 3  # section
    assert tags[1].name == 'toc-section'
    assert tags[1].attributes['level'] == 3  # section
    assert tags[2].name == 'toc-subsection'
    assert tags[2].attributes['level'] == 4  # section
    assert tags[3].name == 'toc-section'
    assert tags[3].attributes['level'] == 3  # section


# tex target

def test_toc_heading_tex(load_example):
    """Test the generation of tocs from headings for tex"""
    # 1. Test the ex1.
    #    Since all the headings are all in the same file, external links to
    #    pdfs are not needed
    doc = load_example(ex1_root / 'file1.dm')
    assert '.tex' in doc.targets

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = """
\\begin{easylist}[booktoc]
\\ListProperties(Hide=2)
§§§ \\href{#sec:file1-dm-heading-1}{Heading 1}
§§§ \\href{#sec:file1-dm-heading-2}{Heading 2}
§§§§ \\href{#subsec:file1-dm-sub-heading-2-1}{sub-Heading 2.1}
§§§§ \\href{#subsec:file1-dm-sub-heading-2-2}{sub-Heading 2.2}
§§§§§ \\href{#subsubsec:file1-dm-sub-sub-header-2-2-1}{sub-sub-Header 2.2.1}
§§§§ \\href{#subsec:file1-dm-sub-heading-2-3}{sub-Heading 2.3}
§§§ \\href{#sec:file1-dm-heading-3}{Heading 3}
§§§§§ \\href{#subsubsec:file1-dm-sub-sub-header-3-1-1}{sub-sub-header 3.1.1}
§§§ \\href{#sec:file1-dm-heading-4}{Heading 4}
\\end{easylist}
"""
    assert key == toc.tex

    # 1. Test the ex2.
    #    Since all the headings are in different files, external links to pdfs
    #    are needed
    doc = load_example(ex2_root / 'file1.dm')
    assert '.tex' in doc.targets
    assert '.pdf' in doc.targets

    # pdfs must be in the targets, since the TOC will make reference to
    # external pdf files compiled from tex files

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = """
\\begin{easylist}[booktoc]
\\ListProperties(Hide=2)
§§§ \\href{#heading-1}{Heading 1}
§§§ \\href{file2.pdf#heading-2}{Heading 2}
§§§§ \\href{file2.pdf#subheading-2}{sub-Heading 2}
§§§ \\href{file3.pdf#heading-3}{Heading 3}
\\end{easylist}
"""
    assert key == toc.tex

    # Create a toc for the headings of file1.dm only.
    toc = Toc(name='toc', content='headings', attributes='',
              context=doc.context)

    key = """
\\begin{easylist}[booktoc]
\\ListProperties(Hide=2)
§§§ \\href{#heading-1}{Heading 1}
\\end{easylist}
"""
    assert key == toc.tex


def test_toc_document_tex(load_example):
    """Test the generation of tocs for documents in latex."""
    # 1. Test the ex1.
    #    Since all the headings are all in the same file, external links to
    #    pdfs are not needed
    doc = load_example(ex1_root / 'file1.dm')
    assert '.tex' in doc.targets

    # Create the tag for document2
    toc = Toc(name='toc', content='all documents', attributes='',
              context=doc.context)

    key = """
\\begin{easylist}[booktoc]
\\ListProperties(Hide=2)
§ file1
§ \\href{sub/file21.pdf}{sub/file21}
§ \\href{sub/file22.pdf}{sub/file22}
\\end{easylist}
"""
    assert key == toc.tex


# html target

def test_toc_absolute_and_relative_links_html(load_example):
    """Test the generation of TOCs with absolute and relative links with
    xhtml."""

    # 1.1. Test examples/toc_ex1 with absolute links (only headings in
    #      file1.dm)
    doc = load_example(ex1_root / 'file1.dm')
    doc.context['relative_links'] = False
    assert '.html' in doc.targets

    toc = Toc(name='toc', content='all headings abbreviated',
              attributes='', context=doc.context)
    key = ('<ol class="toc">\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-1" class="ref">Heading 1</a></li>\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-2" class="ref">Heading 2</a></li>\n'
           '<ol>\n'
           '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-1" class="ref">sub-Heading 2.1</a></li>\n'
           '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-2" class="ref">sub-Heading 2.2</a></li>\n'
           '<ol>'
           '<li class="toc-level-5"><a href="#subsubsec:file1-dm-sub-sub-header-2-2-1" class="ref">sub-sub-Header 2.2.1</a></li>'
           '</ol>\n'
           '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-3" class="ref">sub-Heading 2.3</a></li>\n'
           '</ol>\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-3" class="ref">Heading 3</a></li>\n'
           '<ol>'
           '<li class="toc-level-5"><a href="#subsubsec:file1-dm-sub-sub-header-3-1-1" class="ref">sub-sub-header 3.1.1</a></li>'
           '</ol>\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-4" class="ref">Heading 4</a></li>\n'
           '</ol>\n')
    assert toc.html == key

    # 1.2. Test examples/toc_ex1 with relative links (only headings in file1.dm)
    doc.context['relative_links'] = True

    toc = Toc(name='toc', content='all headings abbreviated',
              attributes='', context=doc.context)
    key = ('<ol class="toc">\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-1" class="ref">Heading 1</a></li>\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-2" class="ref">Heading 2</a></li>\n'
           '<ol>\n'
           '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-1" class="ref">sub-Heading 2.1</a></li>\n'
           '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-2" class="ref">sub-Heading 2.2</a></li>\n'
           '<ol>'
           '<li class="toc-level-5"><a href="#subsubsec:file1-dm-sub-sub-header-2-2-1" class="ref">sub-sub-Header 2.2.1</a></li>'
           '</ol>\n'
           '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-3" class="ref">sub-Heading 2.3</a></li>\n'
           '</ol>\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-3" class="ref">Heading 3</a></li>\n'
           '<ol>'
           '<li class="toc-level-5"><a href="#subsubsec:file1-dm-sub-sub-header-3-1-1" class="ref">sub-sub-header 3.1.1</a></li>'
           '</ol>\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-4" class="ref">Heading 4</a></li>\n'
           '</ol>\n')
    assert toc.html == key

    # 2.1. Test examples/toc_ex2 with absolute links (over multiple files)
    doc = load_example(ex2_root / 'file1.dm')
    doc.context['relative_links'] = False
    assert '.html' in doc.targets

    toc = Toc(name='toc', content='all headings abbreviated',
              attributes='', context=doc.context)
    key = ('<ol class="toc">\n'
           '<li class="toc-level-3"><a href="#heading-1" class="ref">Heading 1</a></li>\n'
           '<li class="toc-level-3"><a href="/html/file2.html#heading-2" class="ref">Heading 2</a></li>\n'
           '<li class="toc-level-3"><a href="/html/file3.html#heading-3" class="ref">Heading 3</a></li>\n'
           '</ol>\n')
    assert toc.html == key

    # 2.2. Test examples/toc_ex2 with relative links (over multiple files)
    doc.context['relative_links'] = True

    toc = Toc(name='toc', content='all headings abbreviated',
              attributes='', context=doc.context)
    key = ('<ol class="toc">\n'
           '<li class="toc-level-3"><a href="#heading-1" class="ref">Heading 1</a></li>\n'
           '<li class="toc-level-3"><a href="file2.html#heading-2" class="ref">Heading 2</a></li>\n'
           '<li class="toc-level-3"><a href="file3.html#heading-3" class="ref">Heading 3</a></li>\n'
           '</ol>\n')
    assert toc.html == key


def test_toc_heading_html(load_example):
    """Test the generation of tocs from headings for html"""

    # 1. Test examples/toc_ex1 (only headings in file1.dm)
    doc = load_example(ex1_root / 'file1.dm')
    assert '.html' in doc.targets

    # 1.1. Try 'all headings'
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = ('<ol class="toc">\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-1" class="ref">Heading 1</a></li>\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-2" class="ref">Heading 2</a></li>\n'
           '<ol>\n'
           '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-1" class="ref">sub-Heading 2.1</a></li>\n'
           '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-2" class="ref">sub-Heading 2.2</a></li>\n'
           '<ol>'
           '<li class="toc-level-5"><a href="#subsubsec:file1-dm-sub-sub-header-2-2-1" class="ref">sub-sub-Header 2.2.1</a></li>'
           '</ol>\n'
           '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-3" class="ref">sub-Heading 2.3</a></li>\n'
           '</ol>\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-3" class="ref">Heading 3</a></li>\n'
           '<ol>'
           '<li class="toc-level-5"><a href="#subsubsec:file1-dm-sub-sub-header-3-1-1" class="ref">sub-sub-header 3.1.1</a></li>'
           '</ol>\n'
           '<li class="toc-level-3"><a href="#sec:file1-dm-heading-4" class="ref">Heading 4</a></li>\n'
           '</ol>\n')
    assert toc.html == key

    # 2. Test examples/toc_ex2 (headings in file1.dm, file2.dm and file3.dm)
    doc = load_example(ex2_root / 'file1.dm')
    assert '.html' in doc.targets

    # 2.1. Test 'all headings'
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = ('<ol class="toc">\n'
           '<li class="toc-level-3"><a href="#heading-1" class="ref">Heading 1</a></li>\n'
           '<li class="toc-level-3"><a href="file2.html#heading-2" class="ref">Heading 2</a></li>\n'
           '<ol>'
           '<li class="toc-level-4"><a href="file2.html#subheading-2" class="ref">sub-Heading 2</a></li>'
           '</ol>\n'
           '<li class="toc-level-3"><a href="file3.html#heading-3" class="ref">Heading 3</a></li>\n'
           '</ol>\n')
    assert toc.html == key

    # 2.2. Test 'all headings abbreviated'
    toc = Toc(name='toc', content='all headings abbreviated', attributes='',
              context=doc.context)

    key = ('<ol class="toc">\n'
           '<li class="toc-level-3"><a href="#heading-1" class="ref">Heading 1</a></li>\n'
           '<li class="toc-level-3"><a href="file2.html#heading-2" class="ref">Heading 2</a></li>\n'
           '<li class="toc-level-3"><a href="file3.html#heading-3" class="ref">Heading 3</a></li>\n'
           '</ol>\n')
    assert toc.html == key


# xhtml target

def test_toc_absolute_and_relative_links_xhtml(load_example):
    """Test the generation of TOCs with absolute and relative links with
    xhtml."""

    # 2.1. Test examples/toc_ex2 with absolute links (over multiple files)
    doc = load_example(ex2_root / 'file1.dm')
    doc.context['relative_links'] = False
    assert '.xhtml' in doc.targets

    toc = Toc(name='toc', content='all headings abbreviated',
              attributes='', context=doc.context)
    key = ('<ol class="toc">\n'
           '  <li class="toc-level-3">\n'
           '  <a href="#heading-1" class="ref">Heading 1</a>\n'
           '</li>\n'
           '  <li class="toc-level-3">\n'
           '  <a href="/xhtml/file2.xhtml#heading-2" class="ref">Heading 2</a>\n'
           '</li>\n'
           '  <li class="toc-level-3">\n'
           '  <a href="/xhtml/file3.xhtml#heading-3" class="ref">Heading 3</a>\n'
           '</li>\n'
           '</ol>\n')
    assert toc.xhtml == key

    # 2.2. Test examples/toc_ex2 with relative links (over multiple files)
    doc.context['relative_links'] = True

    toc = Toc(name='toc', content='all headings abbreviated',
              attributes='', context=doc.context)
    key = ('<ol class="toc">\n'
           '  <li class="toc-level-3">\n'
           '  <a href="#heading-1" class="ref">Heading 1</a>\n'
           '</li>\n'
           '  <li class="toc-level-3">\n'
           '  <a href="file2.xhtml#heading-2" class="ref">Heading 2</a>\n'
           '</li>\n'
           '  <li class="toc-level-3">\n'
           '  <a href="file3.xhtml#heading-3" class="ref">Heading 3</a>\n'
           '</li>\n'
           '</ol>\n')
    assert toc.xhtml == key
