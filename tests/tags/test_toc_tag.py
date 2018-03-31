"""
Test the TOC tag.
"""
from disseminate import Document
from disseminate.tags.toc import Toc, process_context_toc


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
    process_context_toc(context=doc.context)

    key = """<ol class="toc-document">
  <li>
    <a class="document-level-1-ref" href="/file1.html">tests/tags/toc_example1/file1</a>
  </li>
  <ol>
    <li>
      <a class="document-level-2-ref" href="/file21.html">tests/tags/toc_example1/sub/file21</a>
    </li>
    <li>
      <a class="document-level-2-ref" href="/file22.html">tests/tags/toc_example1/sub/file22</a>
    </li>
  </ol>
</ol>
"""
    assert key == doc.context['toc']['.html']


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
  <li>
    <a class="section-ref" href="/file1.html#">Heading 1</a>
  </li>
  <li>
    <a class="section-ref" href="/file1.html#">Heading 2</a>
  </li>
  <ol>
    <li>
      <a class="subsection-ref" href="/file1.html#">sub-Heading 2.1</a>
    </li>
    <li>
      <a class="subsection-ref" href="/file1.html#">sub-Heading 2.2</a>
    </li>
    <ol>
      <li>
        <a class="subsubsection-ref" href="/file1.html#">sub-sub-Header 2.2.1</a>
      </li>
    </ol>
    <li>
      <a class="subsection-ref" href="/file1.html#">sub-Heading 2.3</a>
    </li>
  </ol>
  <li>
    <a class="section-ref" href="/file1.html#">Heading 3</a>
  </li>
  <ol>
    <li>
      <a class="subsubsection-ref" href="/file1.html#">sub-sub-header 3.1.1</a>
    </li>
  </ol>
  <li>
    <a class="section-ref" href="/file1.html#">Heading 4</a>
  </li>
</ol>
"""
    assert key == toc.html()

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
  <li>
    <a class="section-ref" href="/file1.html#heading-1">Heading 1</a>
  </li>
  <li>
    <a class="section-ref" href="/file2.html#heading-2">Heading 2</a>
  </li>
  <ol>
    <li>
      <a class="subsection-ref" href="/file2.html#subheading-2">sub-Heading 2</a>
    </li>
  </ol>
  <li>
    <a class="section-ref" href="/file3.html#heading-3">Heading 3</a>
  </li>
</ol>
"""
    assert key == toc.html()

    # Create a toc for the root document, file1.dm, only.
    toc = Toc(name='toc', content='headings', attributes=tuple(),
              context=doc.context)

    key = """<ol class="toc-heading">
  <li>
    <a class="section-ref" href="/file1.html#heading-1">Heading 1</a>
  </li>
</ol>
"""
    assert key == toc.html()


def test_toc_heading_tex(tmpdir):
    """Test the generation of tocs from headings for tex"""
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

    key = """\\begin{enumerate}
  \\item Heading 1
  \\item Heading 2
  \\begin{enumerate}
    \\item sub-Heading 2.1
    \\item sub-Heading 2.2
    \\begin{enumerate}
      \\item sub-sub-Header 2.2.1
    \\end{enumerate}
    \\item sub-Heading 2.3
  \\end{enumerate}
  \\item Heading 3
  \\begin{enumerate}
    \\item sub-sub-header 3.1.1
  \\end{enumerate}
  \\item Heading 4
\\end{enumerate}
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

    key = """\\begin{enumerate}
  \\item \\hyperlink{heading-1}{Heading 1}
  \\item \\hyperlink{heading-2}{Heading 2}
  \\begin{enumerate}
    \\item \\hyperlink{subheading-2}{sub-Heading 2}
  \\end{enumerate}
  \\item \\hyperlink{heading-3}{Heading 3}
\\end{enumerate}
"""
    assert key == toc.tex()

    # Create a toc for the headings of file1.dm only.
    toc = Toc(name='toc', content='headings', attributes=tuple(),
              context=doc.context)

    key = """\\begin{enumerate}
  \\item \\hyperlink{heading-1}{Heading 1}
\\end{enumerate}
"""
    assert key == toc.tex()


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
  <li>
    <a class="document-level-1-ref" href="/file1.html">tests/tags/toc_example1/file1</a>
  </li>
  <ol>
    <li>
      <a class="document-level-2-ref" href="/file21.html">tests/tags/toc_example1/sub/file21</a>
    </li>
    <li>
      <a class="document-level-2-ref" href="/file22.html">tests/tags/toc_example1/sub/file22</a>
    </li>
  </ol>
</ol>
"""
    assert toc.html() == key

    # Match the collapsed toc
    toc = Toc(name='toc', content='all documents collapsed', attributes=tuple(),
              context=doc.context)
    assert toc.html() == key

    # Match the expanded toc
    toc = Toc(name='toc', content='all documents expanded', attributes=tuple(),
              context=doc.context)
    key = """<ol class="toc-document">
  <li>
    <a class="document-level-1-ref" href="/file1.html">tests/tags/toc_example1/file1</a>
  </li>
  <ol>
    <li>
      <a class="section-ref" href="/file1.html#">Heading 1</a>
    </li>
    <li>
      <a class="section-ref" href="/file1.html#">Heading 2</a>
    </li>
    <ol>
      <li>
        <a class="subsection-ref" href="/file1.html#">sub-Heading 2.1</a>
      </li>
      <li>
        <a class="subsection-ref" href="/file1.html#">sub-Heading 2.2</a>
      </li>
      <ol>
        <li>
          <a class="subsubsection-ref" href="/file1.html#">sub-sub-Header 2.2.1</a>
        </li>
      </ol>
      <li>
        <a class="subsection-ref" href="/file1.html#">sub-Heading 2.3</a>
      </li>
    </ol>
    <li>
      <a class="section-ref" href="/file1.html#">Heading 3</a>
    </li>
    <ol>
      <li>
        <a class="subsubsection-ref" href="/file1.html#">sub-sub-header 3.1.1</a>
      </li>
    </ol>
    <li>
      <a class="section-ref" href="/file1.html#">Heading 4</a>
    </li>
  </ol>
  <li>
    <a class="document-level-2-ref" href="/file21.html">tests/tags/toc_example1/sub/file21</a>
  </li>
  <li>
    <a class="document-level-2-ref" href="/file22.html">tests/tags/toc_example1/sub/file22</a>
  </li>
</ol>
"""
    assert toc.html() == key

    # Match the abbreviated toc
    toc = Toc(name='toc', content='all documents abbreviated',
              attributes=tuple(),
              context=doc.context)
    key = """<ol class="toc-document">
  <li>
    <a class="document-level-1-ref" href="/file1.html">tests/tags/toc_example1/file1</a>
  </li>
  <ol>
    <li>
      <a class="section-ref" href="/file1.html#">Heading 1</a>
    </li>
    <li>
      <a class="section-ref" href="/file1.html#">Heading 2</a>
    </li>
    <ol>
      <li>
        <a class="subsection-ref" href="/file1.html#">sub-Heading 2.1</a>
      </li>
      <li>
        <a class="subsection-ref" href="/file1.html#">sub-Heading 2.2</a>
      </li>
      <ol>
        <li>
          <a class="subsubsection-ref" href="/file1.html#">sub-sub-Header 2.2.1</a>
        </li>
      </ol>
      <li>
        <a class="subsection-ref" href="/file1.html#">sub-Heading 2.3</a>
      </li>
    </ol>
    <li>
      <a class="section-ref" href="/file1.html#">Heading 3</a>
    </li>
    <ol>
      <li>
        <a class="subsubsection-ref" href="/file1.html#">sub-sub-header 3.1.1</a>
      </li>
    </ol>
    <li>
      <a class="section-ref" href="/file1.html#">Heading 4</a>
    </li>
  </ol>
  <li>
    <a class="document-level-2-ref" href="/file21.html">tests/tags/toc_example1/sub/file21</a>
  </li>
  <li>
    <a class="document-level-2-ref" href="/file22.html">tests/tags/toc_example1/sub/file22</a>
  </li>
</ol>
"""
    assert toc.html() == key

    # Test the collapsed toc for only the root document
    toc = Toc(name='toc', content='documents', attributes=tuple(),
              context=doc.context)

    # Match the default toc (collapsed)
    key = """<ol class="toc-document">
  <li>
    <a class="document-level-1-ref" href="/file1.html">tests/tags/toc_example1/file1</a>
  </li>
</ol>
"""
    assert key == toc.html()


def test_toc_document_tex(tmpdir):
    """Test the generation of tocs for documents in latex."""
