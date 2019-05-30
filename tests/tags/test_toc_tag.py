"""
Test the TOC tag.
"""
from disseminate.document import Document
from disseminate.paths import SourcePath, TargetPath
from disseminate.tags.toc import Toc
from disseminate.utils.tests import strip_leading_space


def test_toc_changes(doc):
    """Test the generation of tocs when the label manager changes."""

    # Setup a test document
    markup = """
    ---
    title: my first file
    relative_links: False
    ---
    @section[id=heading1]{My first heading}
    """
    doc.src_filepath.write_text(strip_leading_space(markup))

    # Create the document and render
    doc.render()

    # Make sure the 'base_url' entry matches a basic format.
    doc.context['base_url'] = '/{target}/{subpath}'

    # Match the abbreviated toc
    toc = Toc(name='toc', content='all documents abbreviated',
              attributes='', context=doc.context)

    key = """<ul class="toc-level-1">
  <li>
    <a href="#doc:test-dm" class="ref">my first file</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="#heading1" class="ref">My first heading</a>
    </li>
  </ul>
</ul>
"""
    assert toc.html == key

    # Change the document
    markup = """
    ---
    title: my first file
    relative_links: False
    ---
    @section[id=heading1]{My first heading}
    @subsection[id=subheading1]{My first sub-heading}
    """
    doc.src_filepath.write_text(strip_leading_space(markup))
    doc.render()

    # Match the abbreviated toc
    toc = Toc(name='toc', content='all documents abbreviated',
              attributes='', context=doc.context)
    key = """<ul class="toc-level-1">
  <li>
    <a href="#doc:test-dm" class="ref">my first file</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="#heading1" class="ref">My first heading</a>
    </li>
    <ul class="toc-level-3">
      <li>
        <a href="#subheading1" class="ref">My first sub-heading</a>
      </li>
    </ul>
  </ul>
</ul>
"""
    assert toc.html == key


def test_toc_absolute_and_relative_links(tmpdir):
    """Test the generation of TOCs with absolute and relative links."""

    # 1. Create 2 test documents. First test absolute links
    src_filepath1 = SourcePath(project_root=tmpdir, subpath='test1.dm')
    src_filepath2 = SourcePath(project_root=tmpdir, subpath='test2.dm')
    target_root = TargetPath(target_root=tmpdir)

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

    doc = Document(src_filepath1, target_root)
    toc = Toc(name='toc', content='all documents abbreviated',
              attributes='', context=doc.context)
    key = """<ul class="toc-level-1">
  <li>
    <a href="#doc:test1-dm" class="ref">test1</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="#ch:test1-dm-one" class="ref">one</a>
    </li>
  </ul>
  <li>
    <a href="/html/test2.html#doc:test2-dm" class="ref">test2</a>
  </li>
</ul>
"""
    assert toc.html == key

    # 2. Test with relative links
    src_filepath1.write_text("""
    ---
    include: test2.dm
    relative_links: True
    ---
    @chapter{one}
    """)
    doc.render()

    toc = Toc(name='toc', content='all documents abbreviated',
              attributes='', context=doc.context)
    key = """<ul class="toc-level-1">
  <li>
    <a href="#doc:test1-dm" class="ref">test1</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="#ch:test1-dm-one" class="ref">one</a>
    </li>
  </ul>
  <li>
    <a href="test2.html#doc:test2-dm" class="ref">test2</a>
  </li>
</ul>
"""
    assert toc.html == key

    # 3. The 'tests/tags/toc_example1' directory contains three markup files:
    #    ile1.dm, in the root folder, and file21.dm and file2.dm in the 'sub'
    #    folder. The 'file1.dm' includes 'file21.dm' and 'file22.dm'.
    #    Setup the paths
    #    First test with absolute links
    src_filepath = SourcePath(project_root='tests/tags/toc_example1',
                              subpath='file1.dm')
    target_root = TargetPath(tmpdir)
    doc = Document(src_filepath, target_root)

    # 4. Next, test with relative links
    doc.context['base_url'] = '/{target}/{subpath}'
    doc.context['relative_links'] = False

    # Create the toc tag
    toc = Toc(name='toc', content='all documents', attributes='',
              context=doc.context)

    # Match the default toc (format: 'collapsed')
    key = """<ul class="toc-level-1">
  <li>
    <a href="#doc:file1-dm" class="ref">file1</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="/html/sub/file21.html#doc:sub-file21-dm" class="ref">sub/file21</a>
    </li>
    <li>
      <a href="/html/sub/file22.html#doc:sub-file22-dm" class="ref">sub/file22</a>
    </li>
  </ul>
</ul>
"""
    assert toc.html == key

    # Make sure the 'base_url' entry matches a basic format.
    doc.context['base_url'] = '/{target}/{subpath}'
    doc.context['relative_links'] = True

    # Create the toc tag
    toc = Toc(name='toc', content='all documents', attributes='',
              context=doc.context)

    # Match the default toc (format: 'collapsed')
    key = """<ul class="toc-level-1">
  <li>
    <a href="#doc:file1-dm" class="ref">file1</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="sub/file21.html#doc:sub-file21-dm" class="ref">sub/file21</a>
    </li>
    <li>
      <a href="sub/file22.html#doc:sub-file22-dm" class="ref">sub/file22</a>
    </li>
  </ul>
</ul>
"""
    assert toc.html == key


# html tests

def test_toc_heading_html(tmpdir):
    """Test the generation of tocs from headings for html"""

    # 1. The 'tests/tags/toc_example1' directory contains one markup in the
    #    root directory, file1.dm, and two files, file21.dm and file22.dm, in
    #    the 'sub' sub-directory. file1.dm includes file21.dm and file22.dm
    # Setup paths
    src_filepath = SourcePath(project_root='tests/tags/toc_example1',
                              subpath='file1.dm')
    target_root = TargetPath(tmpdir)

    doc = Document(src_filepath, target_root)

    # Make sure the 'base_url' entry matches a basic format.
    doc.context['base_url'] = '/{target}/{subpath}'
    doc.context['relative_links'] = False

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = """<ul class="toc-level-1">
  <li>
    <a href="#sec:file1-dm-heading-1" class="ref">Heading 1</a>
  </li>
  <li>
    <a href="#sec:file1-dm-heading-2" class="ref">Heading 2</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="#subsec:file1-dm-sub-heading-2-1" class="ref">sub-Heading 2.1</a>
    </li>
    <li>
      <a href="#subsec:file1-dm-sub-heading-2-2" class="ref">sub-Heading 2.2</a>
    </li>
    <ul class="toc-level-3">
      <li>
        <a href="#subsubsec:file1-dm-sub-sub-header-2-2-1" class="ref">sub-sub-Header 2.2.1</a>
      </li>
    </ul>
    <li>
      <a href="#subsec:file1-dm-sub-heading-2-3" class="ref">sub-Heading 2.3</a>
    </li>
  </ul>
  <li>
    <a href="#sec:file1-dm-heading-3" class="ref">Heading 3</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="#subsubsec:file1-dm-sub-sub-header-3-1-1" class="ref">sub-sub-header 3.1.1</a>
    </li>
  </ul>
  <li>
    <a href="#sec:file1-dm-heading-4" class="ref">Heading 4</a>
  </li>
</ul>
"""
    assert toc.html == key

    # 2. The 'tests/tags/toc_example2' directory contains three markup files:
    #     file1.dm, file2.dm and file3.dm. The 'file1.dm' includes 'file2.dm'
    #     and 'file3.dm' The 'file2.dm' has a header and a sub-header.
    #     This test has headers with id anchors specified.
    src_filepath = SourcePath(project_root='tests/tags/toc_example2',
                              subpath='file1.dm')
    doc = Document(src_filepath, target_root)

    # Make sure the 'base_url' entry matches a basic format.
    doc.context['base_url'] = '/{target}/{subpath}'
    doc.context['relative_links'] = False

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = """<ul class="toc-level-1">
  <li>
    <a href="#heading-1" class="ref">Heading 1</a>
  </li>
  <li>
    <a href="/html/file2.html#heading-2" class="ref">Heading 2</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="/html/file2.html#subheading-2" class="ref">sub-Heading 2</a>
    </li>
  </ul>
  <li>
    <a href="/html/file3.html#heading-3" class="ref">Heading 3</a>
  </li>
</ul>
"""
    assert toc.html == key

    # Create a toc for the root document, file1.dm, only.
    toc = Toc(name='toc', content='headings', attributes='',
              context=doc.context)

    key = """<ul class="toc-level-1">
  <li>
    <a href="#heading-1" class="ref">Heading 1</a>
  </li>
</ul>
"""
    assert toc.html == key

    # 3. Test with relative links
    doc.context['relative_links'] = True
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = """<ul class="toc-level-1">
  <li>
    <a href="#heading-1" class="ref">Heading 1</a>
  </li>
  <li>
    <a href="file2.html#heading-2" class="ref">Heading 2</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="file2.html#subheading-2" class="ref">sub-Heading 2</a>
    </li>
  </ul>
  <li>
    <a href="file3.html#heading-3" class="ref">Heading 3</a>
  </li>
</ul>
"""
    assert toc.html == key


# def test_toc_header_html(tmpdir):
#     """Test the creation of a chapter header for TOCs in html."""
#
#     # The 'tests/tags/toc_example2' directory contains three markup files:
#     # file1.dm, file2.dm and file3.dm. The 'file1.dm' includes 'file2.dm' and
#     # 'file3.dm' The 'file2.dm' has a header and a sub-header.
#     # This test has headers with id anchors specified.
#     # Setup paths
#     src_filepath = SourcePath(project_root='tests/tags/toc_example2',
#                               subpath='file1.dm')
#     target_root = TargetPath(tmpdir)
#     doc = Document(src_filepath, target_root)
#
#     # Make sure the 'base_url' entry matches a basic format.
#     doc.context['base_url'] = '/{target}/{subpath}'
#     doc.context['relative_links'] = False
#
#     # Create a toc for the root document, file1.dm, only.
#     toc = Toc(name='toc', content='headings', attributes='',
#               context=doc.context)
#
#     key = """<ul class="toc-level-1">
#   <li>
#     <a href="#heading-1" class="ref">Heading 1</a>
#   </li>
# </ul>
# """
#     assert toc.html == key
#
#     # Now try adding the header
#     toc = Toc(name='toc', content='headings', attributes='header',
#               context=doc.context)
#
#     key = """<ul class="toc-level-1">
#   <li>
#     <span class="ref">
#       <a href="/html/file1.html#heading-1"><span class="number">1.</span> Heading 1</a>
#     </span>
#   </li>
# </ul>
# """
#     print(toc.html)
#     assert toc.html == key
#
#     # Make sure a label was not created for the heading
#     label_manager = doc.context['label_manager']
#     assert len(label_manager.get_labels(kinds='chapter')) == 0


def test_toc_document_html(tmpdir):
    """Test the generation of tocs for documents in html."""
    # The 'tests/tags/toc_example1' directory contains three markup files:
    # file1.dm, in the root folder, and file21.dm and file2.dm in the 'sub'
    # folder. The 'file1.dm' includes 'file21.dm' and 'file22.dm'.
    # Setup the paths
    src_filepath = SourcePath(project_root='tests/tags/toc_example1',
                              subpath='file1.dm')
    target_root = TargetPath(tmpdir)
    doc = Document(src_filepath, target_root)

    # Make sure the 'base_url' entry matches a basic format.
    doc.context['base_url'] = '/{target}/{subpath}'
    doc.context['relative_links'] = False

    # Create the tag for document2
    toc = Toc(name='toc', content='all documents', attributes='',
              context=doc.context)

    # Match the default toc (format: 'collapsed')
    key = """<ul class="toc-level-1">
  <li>
    <a href="#doc:file1-dm" class="ref">file1</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="/html/sub/file21.html#doc:sub-file21-dm" class="ref">sub/file21</a>
    </li>
    <li>
      <a href="/html/sub/file22.html#doc:sub-file22-dm" class="ref">sub/file22</a>
    </li>
  </ul>
</ul>
"""
    assert toc.html == key

    # Match the collapsed toc
    toc = Toc(name='toc', content='all documents collapsed', attributes='',
              context=doc.context)
    assert key == toc.html

    # Match the expanded toc
    toc = Toc(name='toc', content='all documents expanded', attributes='',
              context=doc.context)
    key = """<ul class="toc-level-1">
  <li>
    <a href="#doc:file1-dm" class="ref">file1</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="#sec:file1-dm-heading-1" class="ref">Heading 1</a>
    </li>
    <li>
      <a href="#sec:file1-dm-heading-2" class="ref">Heading 2</a>
    </li>
    <ul class="toc-level-3">
      <li>
        <a href="#subsec:file1-dm-sub-heading-2-1" class="ref">sub-Heading 2.1</a>
      </li>
      <li>
        <a href="#subsec:file1-dm-sub-heading-2-2" class="ref">sub-Heading 2.2</a>
      </li>
      <ul class="toc-level-4">
        <li>
          <a href="#subsubsec:file1-dm-sub-sub-header-2-2-1" class="ref">sub-sub-Header 2.2.1</a>
        </li>
      </ul>
      <li>
        <a href="#subsec:file1-dm-sub-heading-2-3" class="ref">sub-Heading 2.3</a>
      </li>
    </ul>
    <li>
      <a href="#sec:file1-dm-heading-3" class="ref">Heading 3</a>
    </li>
    <ul class="toc-level-3">
      <li>
        <a href="#subsubsec:file1-dm-sub-sub-header-3-1-1" class="ref">sub-sub-header 3.1.1</a>
      </li>
    </ul>
    <li>
      <a href="#sec:file1-dm-heading-4" class="ref">Heading 4</a>
    </li>
  </ul>
  <li>
    <a href="/html/sub/file21.html#doc:sub-file21-dm" class="ref">sub/file21</a>
  </li>
  <li>
    <a href="/html/sub/file22.html#doc:sub-file22-dm" class="ref">sub/file22</a>
  </li>
</ul>
"""
    assert toc.html == key

    # Match the abbreviated toc
    toc = Toc(name='toc', content='all documents abbreviated',
              attributes='', context=doc.context)

    key = """<ul class="toc-level-1">
  <li>
    <a href="#doc:file1-dm" class="ref">file1</a>
  </li>
  <ul class="toc-level-2">
    <li>
      <a href="#sec:file1-dm-heading-1" class="ref">Heading 1</a>
    </li>
    <li>
      <a href="#sec:file1-dm-heading-2" class="ref">Heading 2</a>
    </li>
    <ul class="toc-level-3">
      <li>
        <a href="#subsec:file1-dm-sub-heading-2-1" class="ref">sub-Heading 2.1</a>
      </li>
      <li>
        <a href="#subsec:file1-dm-sub-heading-2-2" class="ref">sub-Heading 2.2</a>
      </li>
      <ul class="toc-level-4">
        <li>
          <a href="#subsubsec:file1-dm-sub-sub-header-2-2-1" class="ref">sub-sub-Header 2.2.1</a>
        </li>
      </ul>
      <li>
        <a href="#subsec:file1-dm-sub-heading-2-3" class="ref">sub-Heading 2.3</a>
      </li>
    </ul>
    <li>
      <a href="#sec:file1-dm-heading-3" class="ref">Heading 3</a>
    </li>
    <ul class="toc-level-3">
      <li>
        <a href="#subsubsec:file1-dm-sub-sub-header-3-1-1" class="ref">sub-sub-header 3.1.1</a>
      </li>
    </ul>
    <li>
      <a href="#sec:file1-dm-heading-4" class="ref">Heading 4</a>
    </li>
  </ul>
  <li>
    <a href="/html/sub/file21.html#doc:sub-file21-dm" class="ref">sub/file21</a>
  </li>
  <li>
    <a href="/html/sub/file22.html#doc:sub-file22-dm" class="ref">sub/file22</a>
  </li>
</ul>
"""
    assert toc.html == key

    # Test the collapsed toc for only the root document
    toc = Toc(name='toc', content='documents', attributes='',
              context=doc.context)

    # Match the default toc (collapsed)
    key = """<ul class="toc-level-1">
  <li>
    <a href="#doc:file1-dm" class="ref">file1</a>
  </li>
</ul>
"""
    assert toc.html == key


# tex tests

def test_toc_heading_tex(tmpdir):
    """Test the generation of tocs from headings for tex"""
    # The 'tests/tags/toc_example1' directory contains one markup in the root
    # directory, file1.dm, and two files, file21.dm and file22.dm, in the
    # 'sub' sub-directory. file1.dm includes file21.dm and file22.dm
    # None of these files have explicit header ids, so generic ones are created.
    # Setup paths
    src_filepaths = SourcePath(project_root='tests/tags/toc_example1',
                               subpath='file1.dm')
    target_root = TargetPath(tmpdir)
    doc = Document(src_filepaths, target_root)

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = """
\\begin{toclist}
  \\item \\hyperref[sec:file1-dm-heading-1]{Heading 1} \\hfill \\pageref{sec:file1-dm-heading-1}
  \\item \\hyperref[sec:file1-dm-heading-2]{Heading 2} \\hfill \\pageref{sec:file1-dm-heading-2}
  \\begin{toclist}
    \\item \\hyperref[subsec:file1-dm-sub-heading-2-1]{sub-Heading 2.1} \\hfill \\pageref{subsec:file1-dm-sub-heading-2-1}
    \\item \\hyperref[subsec:file1-dm-sub-heading-2-2]{sub-Heading 2.2} \\hfill \\pageref{subsec:file1-dm-sub-heading-2-2}
    \\begin{toclist}
      \\item \\hyperref[subsubsec:file1-dm-sub-sub-header-2-2-1]{sub-sub-Header 2.2.1} \\hfill \\pageref{subsubsec:file1-dm-sub-sub-header-2-2-1}
    \\end{toclist}
    \\item \\hyperref[subsec:file1-dm-sub-heading-2-3]{sub-Heading 2.3} \\hfill \\pageref{subsec:file1-dm-sub-heading-2-3}
  \\end{toclist}
  \\item \\hyperref[sec:file1-dm-heading-3]{Heading 3} \\hfill \\pageref{sec:file1-dm-heading-3}
  \\begin{toclist}
    \\item \\hyperref[subsubsec:file1-dm-sub-sub-header-3-1-1]{sub-sub-header 3.1.1} \\hfill \\pageref{subsubsec:file1-dm-sub-sub-header-3-1-1}
  \\end{toclist}
  \\item \\hyperref[sec:file1-dm-heading-4]{Heading 4} \\hfill \\pageref{sec:file1-dm-heading-4}
\\end{toclist}
"""
    assert key == toc.tex

    # The 'tests/tags/toc_example2' directory contains three markup files:
    # file1.dm, file2.dm and file3.dm. The 'file1.dm' includes 'file2.dm' and
    # 'file3.dm' The 'file2.dm' has a header and a sub-header.
    # This test has headers with id anchors specified.
    # Setup paths
    src_filepaths = SourcePath(project_root='tests/tags/toc_example2',
                               subpath='file1.dm')
    doc = Document(src_filepaths, target_root)

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes='',
              context=doc.context)

    key = """
\\begin{toclist}
  \\item \\hyperref[heading-1]{Heading 1} \\hfill \\pageref{heading-1}
  \\item \\hyperref[heading-2]{Heading 2} \\hfill \\pageref{heading-2}
  \\begin{toclist}
    \\item \\hyperref[subheading-2]{sub-Heading 2} \\hfill \\pageref{subheading-2}
  \\end{toclist}
  \\item \\hyperref[heading-3]{Heading 3} \\hfill \\pageref{heading-3}
\\end{toclist}
"""
    assert key == toc.tex

    # Create a toc for the headings of file1.dm only.
    toc = Toc(name='toc', content='headings', attributes='',
              context=doc.context)

    key = """
\\begin{toclist}
  \\item \\hyperref[heading-1]{Heading 1} \\hfill \\pageref{heading-1}
\\end{toclist}
"""
    assert key == toc.tex


# def test_toc_header_tex(tmpdir):
#     """Test the creation of a chapter header for TOCs in tex."""
#     # The 'tests/tags/toc_example2' directory contains three markup files:
#     # file1.dm, file2.dm and file3.dm. The 'file1.dm' includes 'file2.dm' and
#     # 'file3.dm' The 'file2.dm' has a header and a sub-header.
#     # This test has headers with id anchors specified.
#     # Setup paths
#     src_filepath = SourcePath(project_root='tests/tags/toc_example2',
#                               subpath='file1.dm')
#     target_root = TargetPath(tmpdir)
#     doc = Document(src_filepath, target_root)
#
#     # Create a toc for the root document, file1.dm, only.
#     toc = Toc(name='toc', content='headings', attributes='',
#               context=doc.context)
#
#     key = """
# \\begin{toclist}
#   \\item \\hyperref[heading-1]{1. Heading 1} \\hfill \\pageref{heading-1}
# \\end{toclist}
# """
#     assert toc.tex == key
#
#     # Now try adding the header
#     toc = Toc(name='toc', content='headings', attributes='header',
#               context=doc.context)
#
#     key = """
# \\begin{toclist}
#   \\item \\hyperref[heading-1]{1. Heading 1} \\hfill \\pageref{heading-1}
# \\end{toclist}
# """
#     assert toc.tex == key
#
#     # Make sure a label was not created for the heading
#     label_manager = doc.context['label_manager']
#     assert len(label_manager.get_labels(kinds='chapter')) == 0


def test_toc_document_tex(tmpdir):
    """Test the generation of tocs for documents in latex."""
    # The 'tests/tags/toc_example1' directory contains three markup files:
    # file1.dm, in the root folder, and file21.dm and file2.dm in the 'sub'
    # folder. The 'file1.dm' includes 'file21.dm' and 'file22.dm'.
    # Setup paths
    src_filepath = SourcePath(project_root='tests/tags/toc_example1',
                              subpath='file1.dm')
    target_root = TargetPath(tmpdir)
    doc = Document(src_filepath, target_root)

    # Create the tag for document2
    toc = Toc(name='toc', content='all documents', attributes='',
              context=doc.context)

    key = """
\\begin{toclist}
  \\item \\hyperref[doc:file1-dm]{file1} \\hfill \\pageref{doc:file1-dm}
  \\begin{toclist}
    \\item \\hyperref[doc:sub-file21-dm]{sub/file21} \\hfill \\pageref{doc:sub-file21-dm}
    \\item \\hyperref[doc:sub-file22-dm]{sub/file22} \\hfill \\pageref{doc:sub-file22-dm}
  \\end{toclist}
\\end{toclist}
"""
    assert toc.tex == key
