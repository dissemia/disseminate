"""
Test the TOC tag.
"""
from disseminate import Tree
from disseminate.tags.toc import Toc

def test_process_toc(tmpdir):
    """Test the process_toc function"""


def test_toc_heading_html(tmpdir):
    """Test the generation of tocs from headings for html"""
    # Setup paths
    target_root = str(tmpdir)

    # The 'tests/tags/toc_example1' directory contains one markup file with
    # many headings: 'file1.dm'
    tree = Tree(project_root='tests/tags/toc_example1', target_root=target_root,
                segregate_targets=True, target_list=['.html'])
    tree.render()
    docs = tree.get_documents()

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes=tuple(),
              local_context=docs[0].local_context,
              global_context=tree.global_context)
    key = """<ol class="toc-heading">
  <li>
    <a class="section-ref" href="/file1.html">Heading 1</a>
  </li>
  <li>
    <a class="section-ref" href="/file1.html">Heading 2</a>
  </li>
  <ol>
    <li>
      <a class="subsection-ref" href="/file1.html">sub-Heading 2.1</a>
    </li>
    <li>
      <a class="subsection-ref" href="/file1.html">sub-Heading 2.2</a>
    </li>
    <ol>
      <li>
        <a class="subsubsection-ref" href="/file1.html">sub-sub-Header 2.2.1</a>
      </li>
    </ol>
    <li>
      <a class="subsection-ref" href="/file1.html">sub-Heading 2.3</a>
    </li>
  </ol>
  <li>
    <a class="section-ref" href="/file1.html">Heading 3</a>
  </li>
  <ol>
    <ol>
      <li>
        <a class="subsubsection-ref" href="/file1.html">sub-sub-header 3.1.1</a>
      </li>
    </ol>
  </ol>
  <li>
    <a class="section-ref" href="/file1.html">Heading 4</a>
  </li>
</ol>
"""
    assert key == toc.html()

    # The 'tests/tags/toc_example2' directory contains three markup files:
    # file1.dm, file2.dm and file3.dm. The 'file2.dm' has a header and a sub-
    # header.
    tree = Tree(project_root='tests/tags/toc_example2', target_root=target_root,
                segregate_targets=True, target_list=['.html'])
    tree.render()
    docs = tree.get_documents()

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes=tuple(),
              local_context=docs[1].local_context,
              global_context=tree.global_context)

    key = """<ol class="toc-heading">
  <li>
    <a class="section-ref" href="/file1.html">Heading 1</a>
  </li>
  <li>
    <a class="section-ref" href="/file2.html">Heading 2</a>
  </li>
  <ol>
    <li>
      <a class="subsection-ref" href="/file2.html">sub-Heading 2</a>
    </li>
  </ol>
  <li>
    <a class="section-ref" href="/file3.html">Heading 3</a>
  </li>
</ol>
"""
    assert key == toc.html()


def test_toc_heading_tex(tmpdir):
    """Test the generation of tocs from headings for tex"""
    # Setup paths
    target_root = str(tmpdir)

    # The 'tests/tags/toc_example1' directory contains one markup file with
    # many headings: 'file1.dm'
    tree = Tree(project_root='tests/tags/toc_example1', target_root=target_root,
                segregate_targets=True, target_list=['.tex'])
    tree.render()
    docs = tree.get_documents()

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes=tuple(),
              local_context=docs[0].local_context,
              global_context=tree.global_context)

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
    \\begin{enumerate}
      \\item sub-sub-header 3.1.1
    \\end{enumerate}
  \\end{enumerate}
  \\item Heading 4
\\end{enumerate}
"""
    assert key == toc.tex()

    # The 'tests/tags/toc_example2' directory contains three markup files:
    # file1.dm, file2.dm and file3.dm. The 'file2.dm' has a header and a sub-
    # header.
    tree = Tree(project_root='tests/tags/toc_example2', target_root=target_root,
                segregate_targets=True, target_list=['.tex'])
    tree.render()
    docs = tree.get_documents()

    # Create a toc for all headings
    toc = Toc(name='toc', content='all headings', attributes=tuple(),
              local_context=docs[1].local_context,
              global_context=tree.global_context)

    key = """\\begin{enumerate}
  \\item Heading 1
  \\item Heading 2
  \\begin{enumerate}
    \\item sub-Heading 2
  \\end{enumerate}
  \\item Heading 3
\\end{enumerate}
"""
    assert key == toc.tex()


def test_toc_document(tmpdir):
    """Test the generation of tocs for documents."""
    # Setup paths
    target_root = str(tmpdir)

    # The 'tests/tags/toc_example2' directory contains three markup files:
    # file1.dm, file2.dm and file3.dm. Only file2.dm and file3.dm have titles
    # in their header
    tree = Tree(project_root='tests/tags/toc_example2', target_root=target_root,
                segregate_targets=True, target_list=['.html'])
    tree.render()
    docs = tree.get_documents()

    # Create the tag for document2
    toc = Toc(name='toc', content='all documents', attributes=tuple(),
              local_context=docs[1].local_context,
              global_context=tree.global_context)

    # Match the default toc (format: 'collapsed')
    key = """<ol class="toc-document">
  <li>
    <a class="document-ref" href="/file1.html">file1</a>
  </li>
  <li>
    <a class="document-ref" href="/file2.html">My second document</a>
  </li>
  <li>
    <a class="document-ref" href="/file3.html">The third document</a>
  </li>
</ol>
"""
    assert toc.html() == key

    # Match the collapsed toc
    toc = Toc(name='toc', content='all documents collapsed', attributes=tuple(),
              local_context=docs[1].local_context,
              global_context=tree.global_context)
    assert toc.html() == key

    # Match the expanded toc
    toc = Toc(name='toc', content='all documents expanded', attributes=tuple(),
              local_context=docs[1].local_context,
              global_context=tree.global_context)
    key = """<ol class="toc-document">
  <li>
    <a class="document-ref" href="/file1.html">file1</a>
  </li>
  <ol>
    <li>
      <a class="section-ref" href="/file1.html">Heading 1</a>
    </li>
  </ol>
  <li>
    <a class="document-ref" href="/file2.html">My second document</a>
  </li>
  <ol>
    <li>
      <a class="section-ref" href="/file2.html">Heading 2</a>
    </li>
    <ol>
      <li>
        <a class="subsection-ref" href="/file2.html">sub-Heading 2</a>
      </li>
    </ol>
  </ol>
  <li>
    <a class="document-ref" href="/file3.html">The third document</a>
  </li>
  <ol>
    <li>
      <a class="section-ref" href="/file3.html">Heading 3</a>
    </li>
  </ol>
</ol>
"""
    assert toc.html() == key

    # Match the abbreviated toc
    toc = Toc(name='toc', content='all documents abbreviated',
              attributes=tuple(),
              local_context=docs[1].local_context,
              global_context=tree.global_context)
    key = """<ol class="toc-document">
  <li>
    <a class="document-ref" href="/file1.html">file1</a>
  </li>
  <li>
    <a class="document-ref" href="/file2.html">My second document</a>
  </li>
  <ol>
    <li>
      <a class="section-ref" href="/file2.html">Heading 2</a>
    </li>
    <ol>
      <li>
        <a class="subsection-ref" href="/file2.html">sub-Heading 2</a>
      </li>
    </ol>
  </ol>
  <li>
    <a class="document-ref" href="/file3.html">The third document</a>
  </li>
</ol>
"""
    assert toc.html() == key
