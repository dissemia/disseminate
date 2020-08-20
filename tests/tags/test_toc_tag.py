"""
Test the TOC tag.
"""
from disseminate.document import Document
from disseminate.paths import SourcePath
from disseminate.tags.toc import Toc
from disseminate.utils.tests import strip_leading_space


# Tests for methods

def test_toc_get_labels(env):
    """Test the get_labels_by_kind method."""

    # 1. The 'tests/tags/toc_example2' directory contains three markup
    # files:
    #     file1.dm, file2.dm and file3.dm. The 'file1.dm' includes
    #     'file2.dm' and 'file3.dm'. Each file has 1 section, and file2.dm
    #     also has a subsection.
    src_filepath = SourcePath(project_root='tests/tags/toc_example2',
                              subpath='file1.dm')
    doc = Document(src_filepath, environment=env)

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


def test_toc_reference_tags(env):
    """Test the get_labels_by_kind method."""

    # 1. The 'tests/tags/toc_example2' directory contains three markup
    # files:
    #     file1.dm, file2.dm and file3.dm. The 'file1.dm' includes
    #     'file2.dm' and 'file3.dm'. Each file has 1 section, and file2.dm
    #     also has a subsection.
    src_filepath = SourcePath(project_root='tests/tags/toc_example2',
                              subpath='file1.dm')
    doc = Document(src_filepath, environment=env)

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


def test_toc_absolute_and_relative_links(doctree):
    """Test the generation of TOCs with absolute and relative links."""
    env = doctree.context['environment']

    # 1. Create 2 test documents. First test absolute links
    doc1 = doctree
    doc2, doc3 = doc1.documents_list(only_subdocuments=True)
    src_filepath1 = doc1.src_filepath
    src_filepath2 =doc2.src_filepath

    src_filepath2.write_text("""
    @chapter{two}
    """)
    src_filepath1.write_text("""
    ---
    include: test2.dm
    relative_links: False
    ---
    @chapter{one}
    """)

    doc1.load()
    toc = Toc(name='toc', content='all headings abbreviated',
              attributes='', context=doc1.context)
    key = ('<ul class="toc">\n'
             '<li class="toc-level-2"><a href="#ch:test-dm-one" class="ref">Chapter 1. one</a></li>\n'
             '<li class="toc-level-2"><a href="/html/test2.html#ch:test2-dm-two" class="ref">Chapter 2. two</a></li>\n'
           '</ul>\n')
    assert toc.html == key

    # 2. Test with relative links
    src_filepath1.write_text("""
    ---
    include: test2.dm
    relative_links: True
    ---
    @chapter{one}
    """)
    assert doc1.build() == ['done']

    toc = Toc(name='toc', content='all headings abbreviated',
              attributes='', context=doc1.context)
    key = ('<ul class="toc">\n'
             '<li class="toc-level-2"><a href="#ch:test-dm-one" class="ref">Chapter 1. one</a></li>\n'
             '<li class="toc-level-2"><a href="test2.html#ch:test2-dm-two" class="ref">Chapter 2. two</a></li>\n'
           '</ul>\n')
    assert toc.html == key

    # 3. The 'tests/tags/toc_example1' directory contains three markup files:
    #    file1.dm, in the root folder, and file21.dm and file2.dm in the 'sub'
    #    folder. The 'file1.dm' includes 'file21.dm' and 'file22.dm'.
    #    Setup the paths
    #    First test with absolute links
    src_filepath = SourcePath(project_root='tests/tags/toc_example1',
                              subpath='file1.dm')
    doc = Document(src_filepath, environment=env)

    # 4. Next, test with relative links
    doc.context['base_url'] = '/{target}/{subpath}'
    doc.context['relative_links'] = False

    # Create the toc tag
    toc = Toc(name='toc', content='all documents', attributes='',
              context=doc.context)

    # Match the default toc (format: 'collapsed')
    key = ('<ul class="toc">\n'
             '<li class="toc-level-1"><a href="" class="ref">file1</a></li>\n'
             '<li class="toc-level-1"><a href="/html/sub/file21.html" class="ref">sub/file21</a></li>\n'
             '<li class="toc-level-1"><a href="/html/sub/file22.html" class="ref">sub/file22</a></li>\n'
           '</ul>\n')
    assert toc.html == key

    # Make sure the 'base_url' entry matches a basic format.
    doc.context['base_url'] = '/{target}/{subpath}'
    doc.context['relative_links'] = True

    # Create the toc tag
    toc = Toc(name='toc', content='all documents', attributes='',
              context=doc.context)

    # Match the default toc (format: 'collapsed')
    key = ('<ul class="toc">\n'
             '<li class="toc-level-1"><a href="" class="ref">file1</a></li>\n'
             '<li class="toc-level-1"><a href="sub/file21.html" class="ref">sub/file21</a></li>\n'
             '<li class="toc-level-1"><a href="sub/file22.html" class="ref">sub/file22</a></li>\n'
           '</ul>\n')
    assert toc.html == key


# html target

def test_toc_levels_html(doc):
    """Test the correct assignment of toc-levels."""

    # 1. Setup a test document with a @toc tag in the body
    markup = """
    ---
    title: my first file
    relative_links: True
    ---
    @title
    @chapter{My first chapter}
    @section[id=section1]{My first section}
    @subsection{My first sub-section}
    @subsubsection{My first sub-sub-section}
    
    @toc{all headings expanded}
    """
    doc.src_filepath.write_text(strip_leading_space(markup))

    # Create the document and build in html
    assert doc.build() == ['done']

    # Retrieve the rendered file and check its contents
    html_filepath = doc.targets['.html']
    html = html_filepath.read_text()

    # Check the toc
    key = ('<ul class="toc">\n'
             '<li class="toc-level-0"><a href="#title:test-dm-my-first-file" class="ref">my first file</a></li>\n'
             '<ul>\n'
               '<li class="toc-level-2"><a href="#ch:test-dm-my-first-chapter" class="ref">Chapter 1. My first chapter</a></li>\n'
               '<ul>\n'
                 '<li class="toc-level-3"><a href="#section1" class="ref">My first section</a></li>\n'
                 '<ul>\n'
                   '<li class="toc-level-4"><a href="#subsec:test-dm-my-first-sub-section" class="ref">My first sub-section</a></li>\n'
                   '<ul>'
                     '<li class="toc-level-5"><a href="#subsubsec:test-dm-my-first-sub-sub-section" class="ref">My first sub-sub-section</a></li>'
                   '</ul>\n'
                 '</ul>\n'
               '</ul>\n'
             '</ul>\n'
           '</ul>\n')
    print(html)
    assert key in html


# html tests

def test_toc_heading_html(env):
    """Test the generation of tocs from headings for html"""

    # 1. The 'tests/tags/toc_example1' directory contains one markup in the
    #    root directory, file1.dm, and two files, file21.dm and file22.dm, in
    #    the 'sub' sub-directory. file1.dm includes file21.dm and file22.dm
    # Setup paths
    src_filepath = SourcePath(project_root='tests/tags/toc_example1',
                              subpath='file1.dm')
    doc = Document(src_filepath, environment=env)

    # Make sure the 'base_url' entry matches a basic format.
    doc.context['base_url'] = '/{target}/{subpath}'
    doc.context['relative_links'] = False

    # Create a toc for all headings and doc1
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = ('<ul class="toc">\n'
             '<li class="toc-level-3"><a href="#sec:file1-dm-heading-1" class="ref">Heading 1</a></li>\n'
             '<li class="toc-level-3"><a href="#sec:file1-dm-heading-2" class="ref">Heading 2</a></li>\n'
             '<ul>\n'
               '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-1" class="ref">sub-Heading 2.1</a></li>\n'
               '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-2" class="ref">sub-Heading 2.2</a></li>\n'
               '<ul>'
                 '<li class="toc-level-5"><a href="#subsubsec:file1-dm-sub-sub-header-2-2-1" class="ref">sub-sub-Header 2.2.1</a></li>'
               '</ul>\n'
               '<li class="toc-level-4"><a href="#subsec:file1-dm-sub-heading-2-3" class="ref">sub-Heading 2.3</a></li>\n'
             '</ul>\n'
             '<li class="toc-level-3"><a href="#sec:file1-dm-heading-3" class="ref">Heading 3</a></li>\n'
             '<ul>'
               '<li class="toc-level-5"><a href="#subsubsec:file1-dm-sub-sub-header-3-1-1" class="ref">sub-sub-header 3.1.1</a></li>'
             '</ul>\n'
             '<li class="toc-level-3"><a href="#sec:file1-dm-heading-4" class="ref">Heading 4</a></li>\n'
           '</ul>\n')
    assert toc.html == key

    # 2. The 'tests/tags/toc_example2' directory contains three markup files:
    #     file1.dm, file2.dm and file3.dm. The 'file1.dm' includes 'file2.dm'
    #     and 'file3.dm' The 'file2.dm' has a header and a sub-header.
    #     This test has headers with id anchors specified.
    src_filepath = SourcePath(project_root='tests/tags/toc_example2',
                              subpath='file1.dm')
    doc = Document(src_filepath, environment=env)
    doc2, doc3 = doc.documents_list(only_subdocuments=True)

    # Make sure the 'base_url' entry matches a basic format.
    doc.context['base_url'] = '/{target}/{subpath}'
    doc.context['relative_links'] = False

    # Create a toc for all headings and doc (the first document)
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = ('<ul class="toc">\n'
             '<li class="toc-level-3"><a href="#heading-1" class="ref">Heading 1</a></li>\n'
             '<li class="toc-level-3"><a href="/html/file2.html#heading-2" class="ref">Heading 2</a></li>\n'
             '<ul>'
               '<li class="toc-level-4"><a href="/html/file2.html#subheading-2" class="ref">sub-Heading 2</a></li>'
             '</ul>\n'
             '<li class="toc-level-3"><a href="/html/file3.html#heading-3" class="ref">Heading 3</a></li>\n'
           '</ul>\n')
    assert toc.html == key

    # Create a toc for the root document, file1.dm, only.
    toc = Toc(name='toc', content='headings', attributes='',
              context=doc.context)

    key = ('<ul class="toc">'
           '<li class="toc-level-3"><a href="#heading-1" class="ref">Heading 1</a></li>'
           '</ul>\n')
    assert toc.html == key

    # Create a toc for all headings and doc2
    # Make sure the 'base_url' entry matches a basic format.
    doc2.context['base_url'] = '/{target}/{subpath}'
    doc2.context['relative_links'] = False

    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc2.context)

    key = ('<ul class="toc">\n'
             '<li class="toc-level-3"><a href="/html/file1.html#heading-1" class="ref">Heading 1</a></li>\n'
             '<li class="toc-level-3"><a href="#heading-2" class="ref">Heading 2</a></li>\n'
             '<ul>'
               '<li class="toc-level-4"><a href="#subheading-2" class="ref">sub-Heading 2</a></li>'
             '</ul>\n'
             '<li class="toc-level-3"><a href="/html/file3.html#heading-3" class="ref">Heading 3</a></li>\n'
           '</ul>\n')
    assert toc.html == key

    # 3. Test with relative links and doc1
    doc.context['relative_links'] = True
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = ('<ul class="toc">\n'
             '<li class="toc-level-3"><a href="#heading-1" class="ref">Heading 1</a></li>\n'
             '<li class="toc-level-3"><a href="file2.html#heading-2" class="ref">Heading 2</a></li>\n'
             '<ul>'
               '<li class="toc-level-4"><a href="file2.html#subheading-2" class="ref">sub-Heading 2</a></li>'
             '</ul>\n'
             '<li class="toc-level-3"><a href="file3.html#heading-3" class="ref">Heading 3</a></li>\n'
           '</ul>\n')
    assert toc.html == key

    # Test with relative links and doc2
    doc2.context['relative_links'] = True
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc2.context)
    key = ('<ul class="toc">\n'
             '<li class="toc-level-3"><a href="file1.html#heading-1" class="ref">Heading 1</a></li>\n'
             '<li class="toc-level-3"><a href="#heading-2" class="ref">Heading 2</a></li>\n'
             '<ul>'
               '<li class="toc-level-4"><a href="#subheading-2" class="ref">sub-Heading 2</a></li>'
             '</ul>\n'
             '<li class="toc-level-3"><a href="file3.html#heading-3" class="ref">Heading 3</a></li>\n'
           '</ul>\n')
    assert toc.html == key


# tex target

def test_toc_heading_tex(env):
    """Test the generation of tocs from headings for tex"""
    # The 'tests/tags/toc_example1' directory contains one markup in the root
    # directory, file1.dm, and two files, file21.dm and file22.dm, in the
    # 'sub' sub-directory. file1.dm includes file21.dm and file22.dm
    # None of these files have explicit header ids, so generic ones are created.
    # Setup paths
    src_filepaths = SourcePath(project_root='tests/tags/toc_example1',
                               subpath='file1.dm')
    doc = Document(src_filepaths, environment=env)

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

    # The 'tests/tags/toc_example2' directory contains three markup files:
    # file1.dm, file2.dm and file3.dm. The 'file1.dm' includes 'file2.dm' and
    # 'file3.dm' The 'file2.dm' has a header and a sub-header.
    # This test has headers with id anchors specified.
    # Setup paths
    src_filepaths = SourcePath(project_root='tests/tags/toc_example2',
                               subpath='file1.dm')
    doc = Document(src_filepaths, environment=env)

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = """
\\begin{easylist}[booktoc]
\\ListProperties(Hide=2)
§§§ \\href{#heading-1}{Heading 1}
§§§ Heading 2
§§§§ sub-Heading 2
§§§ Heading 3
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


def test_toc_document_tex(env):
    """Test the generation of tocs for documents in latex."""
    # The 'tests/tags/toc_example1' directory contains three markup files:
    # file1.dm, in the root folder, and file21.dm and file2.dm in the 'sub'
    # folder. The 'file1.dm' includes 'file21.dm' and 'file22.dm'.
    # Setup paths
    src_filepath = SourcePath(project_root='tests/tags/toc_example1',
                              subpath='file1.dm')
    doc = Document(src_filepath, environment=env)

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
