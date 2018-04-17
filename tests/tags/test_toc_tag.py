"""
Test the TOC tag.
"""
from lxml.html import etree
from lxml.builder import E

from disseminate import Document
from disseminate.tags.toc import Toc, process_context_toc
from disseminate.utils.tests import strip_leading_space


def test_process_toc(tmpdir):
    """Test the process_toc function"""
    # Setup paths
    target_root = str(tmpdir)

    # The 'tests/tags/toc_example1' directory contains one markup in the root
    # directory, file1.dm, and two files, file21.dm and file22.dm, in the
    # 'sub' sub-directory. file1.dm includes file21.dm and file22.dm
    doc = Document('tests/tags/toc_example1/file1.dm',
                   target_root=target_root)

    # Put a toc in the context for all documents collapsed
    doc.context['toc'] = 'all documents collapsed'

    # Load the html version of the toc
    context = dict(doc.context)
    process_context_toc(context=context, target='.html')

    key = """<ol class="toc-document">
  <li class="li-document-level-1">
    <a class="document-level-1-ref" href="/file1.html">tests/tags/toc_example1/file1</a>
  </li>
  <ol class="toc-level-2">
    <li class="li-document-level-2">
      <a class="document-level-2-ref" href="/sub/file21.html">tests/tags/toc_example1/sub/file21</a>
    </li>
    <li class="li-document-level-2">
      <a class="document-level-2-ref" href="/sub/file22.html">tests/tags/toc_example1/sub/file22</a>
    </li>
  </ol>
</ol>
"""
    assert key == context['toc']


def test_toc_heading_html(tmpdir):
    """Test the generation of tocs from headings for html"""
    # Setup paths
    target_root = str(tmpdir)

    # The 'tests/tags/toc_example1' directory contains one markup in the root
    # directory, file1.dm, and two files, file21.dm and file22.dm, in the
    # 'sub' sub-directory. file1.dm includes file21.dm and file22.dm
    doc = Document('tests/tags/toc_example1/file1.dm',
                   target_root=target_root)

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes=tuple(),
              context=doc.context)

    key = """<ol class="toc-heading">
  <li class="li-section">
    <a class="section-ref" href="/file1.html#section:heading-1">Heading 1</a>
  </li>
  <li class="li-section">
    <a class="section-ref" href="/file1.html#section:heading-2">Heading 2</a>
  </li>
  <ol class="toc-level-2">
    <li class="li-subsection">
      <a class="subsection-ref" href="/file1.html#subsection:sub-heading-2-1">sub-Heading 2.1</a>
    </li>
    <li class="li-subsection">
      <a class="subsection-ref" href="/file1.html#subsection:sub-heading-2-2">sub-Heading 2.2</a>
    </li>
    <ol class="toc-level-3">
      <li class="li-subsubsection">
        <a class="subsubsection-ref" href="/file1.html#subsubsection:sub-sub-header-2-2-1">sub-sub-Header 2.2.1</a>
      </li>
    </ol>
    <li class="li-subsection">
      <a class="subsection-ref" href="/file1.html#subsection:sub-heading-2-3">sub-Heading 2.3</a>
    </li>
  </ol>
  <li class="li-section">
    <a class="section-ref" href="/file1.html#section:heading-3">Heading 3</a>
  </li>
  <ol class="toc-level-2">
    <li class="li-subsubsection">
      <a class="subsubsection-ref" href="/file1.html#subsubsection:sub-sub-header-3-1-1">sub-sub-header 3.1.1</a>
    </li>
  </ol>
  <li class="li-section">
    <a class="section-ref" href="/file1.html#section:heading-4">Heading 4</a>
  </li>
</ol>
"""
    html = etree.tostring(toc.html(), pretty_print=True).decode('utf-8')
    assert key == html

    # The 'tests/tags/toc_example2' directory contains three markup files:
    # file1.dm, file2.dm and file3.dm. The 'file1.dm' includes 'file2.dm' and
    # 'file3.dm' The 'file2.dm' has a header and a sub-header.
    # This test has headers with id anchors specified.
    doc = Document('tests/tags/toc_example2/file1.dm',
                   target_root=target_root)

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes=tuple(),
              context=doc.context)

    key = """<ol class="toc-heading">
  <li class="li-section">
    <a class="section-ref" href="/file1.html#heading-1">Heading 1</a>
  </li>
  <li class="li-section">
    <a class="section-ref" href="/file2.html#heading-2">Heading 2</a>
  </li>
  <ol class="toc-level-2">
    <li class="li-subsection">
      <a class="subsection-ref" href="/file2.html#subheading-2">sub-Heading 2</a>
    </li>
  </ol>
  <li class="li-section">
    <a class="section-ref" href="/file3.html#heading-3">Heading 3</a>
  </li>
</ol>
"""
    html = etree.tostring(toc.html(), pretty_print=True).decode('utf-8')
    assert key == html

    # Create a toc for the root document, file1.dm, only.
    toc = Toc(name='toc', content='headings', attributes=tuple(),
              context=doc.context)

    key = """<ol class="toc-heading">
  <li class="li-section">
    <a class="section-ref" href="/file1.html#heading-1">Heading 1</a>
  </li>
</ol>
"""
    html = etree.tostring(toc.html(), pretty_print=True).decode('utf-8')
    assert key == html


def test_toc_header_html(tmpdir):
    """Test the creation of a chapter header for TOCs in html."""

    # Setup paths
    target_root = str(tmpdir)

    # The 'tests/tags/toc_example2' directory contains three markup files:
    # file1.dm, file2.dm and file3.dm. The 'file1.dm' includes 'file2.dm' and
    # 'file3.dm' The 'file2.dm' has a header and a sub-header.
    # This test has headers with id anchors specified.
    doc = Document('tests/tags/toc_example2/file1.dm',
                   target_root=target_root)

    # Create a toc for the root document, file1.dm, only.
    toc = Toc(name='toc', content='headings', attributes=tuple(),
              context=doc.context)

    key = """<ol class="toc-heading">
  <li class="li-section">
    <a class="section-ref" href="/file1.html#heading-1">Heading 1</a>
  </li>
</ol>
"""
    html = etree.tostring(toc.html(), pretty_print=True).decode('utf-8')
    assert key == html

    # Now try adding the header
    toc = Toc(name='toc', content='headings', attributes=('header'),
              context=doc.context)

    key = """<div>
  <h1>Table of Contents</h1>
  <ol class="toc-heading">
    <li class="li-section">
      <a class="section-ref" href="/file1.html#heading-1">Heading 1</a>
    </li>
  </ol>
</div>
"""
    e = E('div', *toc.html())
    html = etree.tostring(e, pretty_print=True).decode('utf-8')
    assert key == html

    # Make sure a label was not created for the heading
    label_manager = doc.context['label_manager']
    assert len(label_manager.get_labels(kinds='chapter')) == 0


def test_toc_heading_tex(tmpdir):
    """Test the generation of tocs from headings for tex"""
    # Setup paths
    target_root = str(tmpdir)

    # The 'tests/tags/toc_example1' directory contains one markup in the root
    # directory, file1.dm, and two files, file21.dm and file22.dm, in the
    # 'sub' sub-directory. file1.dm includes file21.dm and file22.dm
    # None of these files have explicit header ids, so generic ones are created.
    doc = Document('tests/tags/toc_example1/file1.dm',
                   target_root=target_root)

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes=tuple(),
              context=doc.context)

    key = """\\begin{toclist}
  \\item \\hyperref[section:heading-1]{Heading 1} \\dotfill \\makebox[5ex][r]{\\pageref{section:heading-1}}
  \\item \\hyperref[section:heading-2]{Heading 2} \\dotfill \\makebox[5ex][r]{\\pageref{section:heading-2}}
  \\begin{toclist}
    \\item \\hyperref[subsection:sub-heading-2-1]{sub-Heading 2.1} \\dotfill \\makebox[5ex][r]{\\pageref{subsection:sub-heading-2-1}}
    \\item \\hyperref[subsection:sub-heading-2-2]{sub-Heading 2.2} \\dotfill \\makebox[5ex][r]{\\pageref{subsection:sub-heading-2-2}}
    \\begin{toclist}
      \\item \\hyperref[subsubsection:sub-sub-header-2-2-1]{sub-sub-Header 2.2.1} \\dotfill \\makebox[5ex][r]{\\pageref{subsubsection:sub-sub-header-2-2-1}}
    \\end{toclist}
    \\item \\hyperref[subsection:sub-heading-2-3]{sub-Heading 2.3} \\dotfill \\makebox[5ex][r]{\\pageref{subsection:sub-heading-2-3}}
  \\end{toclist}
  \\item \\hyperref[section:heading-3]{Heading 3} \\dotfill \\makebox[5ex][r]{\\pageref{section:heading-3}}
  \\begin{toclist}
    \\item \\hyperref[subsubsection:sub-sub-header-3-1-1]{sub-sub-header 3.1.1} \\dotfill \\makebox[5ex][r]{\\pageref{subsubsection:sub-sub-header-3-1-1}}
  \\end{toclist}
  \\item \\hyperref[section:heading-4]{Heading 4} \\dotfill \\makebox[5ex][r]{\\pageref{section:heading-4}}
\\end{toclist}
"""
    assert key == toc.tex()

    # The 'tests/tags/toc_example2' directory contains three markup files:
    # file1.dm, file2.dm and file3.dm. The 'file1.dm' includes 'file2.dm' and
    # 'file3.dm' The 'file2.dm' has a header and a sub-header.
    # This test has headers with id anchors specified.
    doc = Document('tests/tags/toc_example2/file1.dm',
                   target_root=target_root)

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes=tuple(),
              context=doc.context)

    key = """\\begin{toclist}
  \\item \\hyperref[heading-1]{Heading 1} \\dotfill \\makebox[5ex][r]{\\pageref{heading-1}}
  \\item \\hyperref[heading-2]{Heading 2} \\dotfill \\makebox[5ex][r]{\\pageref{heading-2}}
  \\begin{toclist}
    \\item \\hyperref[subheading-2]{sub-Heading 2} \\dotfill \\makebox[5ex][r]{\\pageref{subheading-2}}
  \\end{toclist}
  \\item \\hyperref[heading-3]{Heading 3} \\dotfill \\makebox[5ex][r]{\\pageref{heading-3}}
\\end{toclist}
"""
    assert key == toc.tex()

    # Create a toc for the headings of file1.dm only.
    toc = Toc(name='toc', content='headings', attributes=tuple(),
              context=doc.context)

    key = """\\begin{toclist}
  \\item \\hyperref[heading-1]{Heading 1} \\dotfill \\makebox[5ex][r]{\\pageref{heading-1}}
\\end{toclist}
"""
    assert key == toc.tex()


def test_toc_header_tex(tmpdir):
    """Test the creation of a chapter header for TOCs in tex."""

    # Setup paths
    target_root = str(tmpdir)

    # The 'tests/tags/toc_example2' directory contains three markup files:
    # file1.dm, file2.dm and file3.dm. The 'file1.dm' includes 'file2.dm' and
    # 'file3.dm' The 'file2.dm' has a header and a sub-header.
    # This test has headers with id anchors specified.
    doc = Document('tests/tags/toc_example2/file1.dm',
                   target_root=target_root)

    # Create a toc for the root document, file1.dm, only.
    toc = Toc(name='toc', content='headings', attributes=tuple(),
              context=doc.context)

    key = """\\begin{toclist}
  \\item \\hyperref[heading-1]{Heading 1} \\dotfill \\makebox[5ex][r]{\\pageref{heading-1}}
\\end{toclist}
"""
    tex = toc.tex()
    assert key == tex

    # Now try adding the header
    toc = Toc(name='toc', content='headings', attributes=('header'),
              context=doc.context)

    key = """
\\chapter{Table of Contents}

\\begin{toclist}
  \\item \\hyperref[heading-1]{Heading 1} \\dotfill \\makebox[5ex][r]{\\pageref{heading-1}}
\\end{toclist}
"""
    tex = toc.tex()
    assert key == tex

    # Make sure a label was not created for the heading
    label_manager = doc.context['label_manager']
    assert len(label_manager.get_labels(kinds='chapter')) == 0


def test_toc_document_html(tmpdir):
    """Test the generation of tocs for documents in html."""
    # Setup paths
    target_root = str(tmpdir)

    # The 'tests/tags/toc_example1' directory contains three markup files:
    # file1.dm, in the root folder, and file21.dm and file2.dm in the 'sub'
    # folder. The 'file1.dm' includes 'file21.dm' and 'file22.dm'.
    doc = Document('tests/tags/toc_example1/file1.dm',
                   target_root=target_root)

    # Create the tag for document2
    toc = Toc(name='toc', content='all documents', attributes=tuple(),
              context=doc.context)

    # Match the default toc (format: 'collapsed')
    key = """<ol class="toc-document">
  <li class="li-document-level-1">
    <a class="document-level-1-ref" href="/file1.html">tests/tags/toc_example1/file1</a>
  </li>
  <ol class="toc-level-2">
    <li class="li-document-level-2">
      <a class="document-level-2-ref" href="/sub/file21.html">tests/tags/toc_example1/sub/file21</a>
    </li>
    <li class="li-document-level-2">
      <a class="document-level-2-ref" href="/sub/file22.html">tests/tags/toc_example1/sub/file22</a>
    </li>
  </ol>
</ol>
"""
    html = etree.tostring(toc.html(), pretty_print=True).decode('utf-8')
    assert key == html

    # Match the collapsed toc
    toc = Toc(name='toc', content='all documents collapsed', attributes=tuple(),
              context=doc.context)
    html = etree.tostring(toc.html(), pretty_print=True).decode('utf-8')
    assert key == html

    # Match the expanded toc
    toc = Toc(name='toc', content='all documents expanded', attributes=tuple(),
              context=doc.context)
    key = """<ol class="toc-document">
  <li class="li-document-level-1">
    <a class="document-level-1-ref" href="/file1.html">tests/tags/toc_example1/file1</a>
  </li>
  <ol class="toc-level-2">
    <li class="li-section">
      <a class="section-ref" href="/file1.html#section:heading-1">Heading 1</a>
    </li>
    <li class="li-section">
      <a class="section-ref" href="/file1.html#section:heading-2">Heading 2</a>
    </li>
    <ol class="toc-level-3">
      <li class="li-subsection">
        <a class="subsection-ref" href="/file1.html#subsection:sub-heading-2-1">sub-Heading 2.1</a>
      </li>
      <li class="li-subsection">
        <a class="subsection-ref" href="/file1.html#subsection:sub-heading-2-2">sub-Heading 2.2</a>
      </li>
      <ol class="toc-level-4">
        <li class="li-subsubsection">
          <a class="subsubsection-ref" href="/file1.html#subsubsection:sub-sub-header-2-2-1">sub-sub-Header 2.2.1</a>
        </li>
      </ol>
      <li class="li-subsection">
        <a class="subsection-ref" href="/file1.html#subsection:sub-heading-2-3">sub-Heading 2.3</a>
      </li>
    </ol>
    <li class="li-section">
      <a class="section-ref" href="/file1.html#section:heading-3">Heading 3</a>
    </li>
    <ol class="toc-level-3">
      <li class="li-subsubsection">
        <a class="subsubsection-ref" href="/file1.html#subsubsection:sub-sub-header-3-1-1">sub-sub-header 3.1.1</a>
      </li>
    </ol>
    <li class="li-section">
      <a class="section-ref" href="/file1.html#section:heading-4">Heading 4</a>
    </li>
  </ol>
  <li class="li-document-level-2">
    <a class="document-level-2-ref" href="/sub/file21.html">tests/tags/toc_example1/sub/file21</a>
  </li>
  <li class="li-document-level-2">
    <a class="document-level-2-ref" href="/sub/file22.html">tests/tags/toc_example1/sub/file22</a>
  </li>
</ol>
"""
    html = etree.tostring(toc.html(), pretty_print=True).decode('utf-8')
    assert key == html

    # Match the abbreviated toc
    toc = Toc(name='toc', content='all documents abbreviated',
              attributes=tuple(),
              context=doc.context)
    key = """<ol class="toc-document">
  <li class="li-document-level-1">
    <a class="document-level-1-ref" href="/file1.html">tests/tags/toc_example1/file1</a>
  </li>
  <ol class="toc-level-2">
    <li class="li-section">
      <a class="section-ref" href="/file1.html#section:heading-1">Heading 1</a>
    </li>
    <li class="li-section">
      <a class="section-ref" href="/file1.html#section:heading-2">Heading 2</a>
    </li>
    <ol class="toc-level-3">
      <li class="li-subsection">
        <a class="subsection-ref" href="/file1.html#subsection:sub-heading-2-1">sub-Heading 2.1</a>
      </li>
      <li class="li-subsection">
        <a class="subsection-ref" href="/file1.html#subsection:sub-heading-2-2">sub-Heading 2.2</a>
      </li>
      <ol class="toc-level-4">
        <li class="li-subsubsection">
          <a class="subsubsection-ref" href="/file1.html#subsubsection:sub-sub-header-2-2-1">sub-sub-Header 2.2.1</a>
        </li>
      </ol>
      <li class="li-subsection">
        <a class="subsection-ref" href="/file1.html#subsection:sub-heading-2-3">sub-Heading 2.3</a>
      </li>
    </ol>
    <li class="li-section">
      <a class="section-ref" href="/file1.html#section:heading-3">Heading 3</a>
    </li>
    <ol class="toc-level-3">
      <li class="li-subsubsection">
        <a class="subsubsection-ref" href="/file1.html#subsubsection:sub-sub-header-3-1-1">sub-sub-header 3.1.1</a>
      </li>
    </ol>
    <li class="li-section">
      <a class="section-ref" href="/file1.html#section:heading-4">Heading 4</a>
    </li>
  </ol>
  <li class="li-document-level-2">
    <a class="document-level-2-ref" href="/sub/file21.html">tests/tags/toc_example1/sub/file21</a>
  </li>
  <li class="li-document-level-2">
    <a class="document-level-2-ref" href="/sub/file22.html">tests/tags/toc_example1/sub/file22</a>
  </li>
</ol>
"""
    html = etree.tostring(toc.html(), pretty_print=True).decode('utf-8')
    assert key == html

    # Test the collapsed toc for only the root document
    toc = Toc(name='toc', content='documents', attributes=tuple(),
              context=doc.context)

    # Match the default toc (collapsed)
    key = """<ol class="toc-document">
  <li class="li-document-level-1">
    <a class="document-level-1-ref" href="/file1.html">tests/tags/toc_example1/file1</a>
  </li>
</ol>
"""
    html = etree.tostring(toc.html(), pretty_print=True).decode('utf-8')
    assert key == html


def test_toc_document_tex(tmpdir):
    """Test the generation of tocs for documents in latex."""
    # Setup paths
    target_root = str(tmpdir)

    # The 'tests/tags/toc_example1' directory contains three markup files:
    # file1.dm, in the root folder, and file21.dm and file2.dm in the 'sub'
    # folder. The 'file1.dm' includes 'file21.dm' and 'file22.dm'.
    doc = Document('tests/tags/toc_example1/file1.dm',
                   target_root=target_root)

    # Create the tag for document2
    toc = Toc(name='toc', content='all documents', attributes=tuple(),
              context=doc.context)

    key = """\\begin{toclist}
  \\item \\hyperref[doc:file1.dm]{tests/tags/toc_example1/file1} \\hfill \\makebox[5ex][r]{\\pageref{doc:file1.dm}}
  \\begin{toclist}
    \\item \\hyperref[doc:sub/file21.dm]{tests/tags/toc_example1/sub/file21} \\hfill \\makebox[5ex][r]{\\pageref{doc:sub/file21.dm}}
    \\item \\hyperref[doc:sub/file22.dm]{tests/tags/toc_example1/sub/file22} \\hfill \\makebox[5ex][r]{\\pageref{doc:sub/file22.dm}}
  \\end{toclist}
\\end{toclist}
"""
    assert key == toc.tex()


def test_toc_changes(tmpdir):
    """Test the generation of tocs when the label manager changes."""
    # Setup a test document
    src_path = tmpdir.join('src')
    src_path.mkdir()
    src_filepath = src_path.join('test.dm')

    markup = """
    ---
    title: my first file
    ---
    @section[id=heading1]{My first heading}
    """
    src_filepath.write(strip_leading_space(markup))

    # Create the document and render
    doc = Document(src_filepath=src_filepath, target_root=str(tmpdir))
    doc.render()

    # Match the abbreviated toc
    toc = Toc(name='toc', content='all documents abbreviated',
              attributes=tuple(),
              context=doc.context)
    key = """<ol class="toc-document">
  <li class="li-document-level-1">
    <a class="document-level-1-ref" href="/test.html">my first file</a>
  </li>
  <ol class="toc-level-2">
    <li class="li-section">
      <a class="section-ref" href="/test.html#heading1">My first heading</a>
    </li>
  </ol>
</ol>
"""
    html = etree.tostring(toc.html(), pretty_print=True).decode('utf-8')
    assert key == html

    # Change the document
    markup = """
    ---
    title: my first file
    ---
    @section[id=heading1]{My first heading}
    @subsection[id=subheading1]{My first sub-heading}
    """
    src_filepath.write(strip_leading_space(markup))
    doc.render()

    # Match the abbreviated toc
    toc = Toc(name='toc', content='all documents abbreviated',
              attributes=tuple(),
              context=doc.context)
    key = """<ol class="toc-document">
  <li class="li-document-level-1">
    <a class="document-level-1-ref" href="/test.html">my first file</a>
  </li>
  <ol class="toc-level-2">
    <li class="li-section">
      <a class="section-ref" href="/test.html#heading1">My first heading</a>
    </li>
    <ol class="toc-level-3">
      <li class="li-subsection">
        <a class="subsection-ref" href="/test.html#subheading1">My first sub-heading</a>
      </li>
    </ol>
  </ol>
</ol>
"""
    html = etree.tostring(toc.html(), pretty_print=True).decode('utf-8')
    assert key == html
