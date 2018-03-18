"""
Test the TOC tag.
"""
from disseminate import Tree
from disseminate.tags.toc import Toc

def test_process_toc(tmpdir):
    """Test the process_toc function"""



def test_toc_heading(tmpdir):
    """Test the generation of tocs from headings"""
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

    key = '\n'.join(('<ol class="toc-heading">',
                     '  <li>Heading 1</li>',
                     '  <li>Heading 2</li>',
                     '  <ol>',
                     '    <li>sub-Heading 2.1</li>',
                     '    <li>sub-Heading 2.2</li>',
                     '    <ol>',
                     '      <li>sub-sub-Header 2.2.1</li>',
                     '    </ol>',
                     '    <li>sub-Heading 2.3</li>',
                     '  </ol>',
                     '  <li>Heading 3</li>',
                     '  <ol>',
                     '    <ol>',
                     '      <li>sub-sub-header 3.1.1</li>',
                     '    </ol>',
                     '  </ol>',
                     '  <li>Heading 4</li>',
                     '</ol>\n'))
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

    key = '\n'.join(('<ol class="toc-heading">',
                     '  <li>',
                     '    <a href="/file1.html">Heading 1</a>',
                     '  </li>',
                     '  <li>Heading 2</li>',
                     '  <ol>',
                     '    <li>sub-Heading 2</li>',
                     '  </ol>',
                     '  <li>',
                     '    <a href="/file3.html">Heading 3</a>',
                     '  </li>',
                     '</ol>\n'))
    assert key == toc.html()


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
    key = '\n'.join(('<ol class="toc-document">',
                     '  <li><a href="/file1.html">file1</a></li>',
                     '  <li>My second document</li>',
                     '  <li><a href="/file3.html">The third document</a></li>',
                     '</ol>\n'))
    assert toc.html() == key

    toc.attributes = (('format', 'collapsed'),)
    assert toc.html() == key

    # Match the expanded toc (format: 'expanded')
    toc.attributes = (('format', 'expanded'),)
    key = '\n'.join(('<ol class="toc-document">',
                     '  <li>',
                     '    <a href="/file1.html">file1</a>',
                     '    <ol class="toc-heading">',
                     '      <li>',
                     '        <a href="/file1.html">Heading 1</a>',
                     '      </li>',
                     '    </ol>',
                     '  </li>',
                     '  <li>My second document'
                     '<ol class="toc-heading">'
                     '<li>Heading 2</li>'
                     '<ol><li>sub-Heading 2</li></ol></ol></li>',
                     '  <li>',
                     '    <a href="/file3.html">The third document</a>',
                     '    <ol class="toc-heading">',
                     '      <li>',
                     '        <a href="/file3.html">Heading 3</a>',
                     '      </li>',
                     '    </ol>',
                     '  </li>',
                     '</ol>\n'))
    assert toc.html() == key

    # Match the abbreviated toc (format: 'abbreviated')
    toc.attributes = (('format', 'abbreviated'),)
    key = '\n'.join(('<ol class="toc-document">',
                     '  <li><a href="/file1.html">file1</a></li>',
                     '  <li>My second document<ol class="toc-heading">'
                     '<li>Heading 2</li>'
                     '<ol><li>sub-Heading 2</li></ol></ol></li>',
                     '  <li><a href="/file3.html">The third document</a></li>',
                     '</ol>\n'))
    assert toc.html() == key
