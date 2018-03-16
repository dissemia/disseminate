"""
Test the TOC tag.
"""
from disseminate import Tree, Document
from disseminate.tags.toc import Toc


def test_toc_document(tmpdir):
    """Test the generation of tocs for documents."""
    # Setup paths
    target_root = str(tmpdir)

    # The 'tests/tags/toc_example1' directory contains three markup files:
    # file1.dm, file2.dm and file3.dm. Only file2.dm and file3.dm have titles
    # in their header
    tree = Tree(project_root='tests/tags/toc_example1', target_root=target_root,
                segregate_targets=True, target_list=['.html'])
    tree.render()
    docs = tree.get_documents()

    # Create the tag for document2
    toc = Toc(name='toc', content='all documents', attributes=tuple(),
              local_context=docs[1].local_context,
              global_context=tree.global_context)

    # Match the default toc (format: 'collapsed')
    key = '\n'.join(('<ol class="toc-document">',
                     '  <li><a href="file1.html">file1</a></li>',
                     '  <li>My second document</li>',
                     '  <li><a href="file3.html">The third document</a></li>',
                     '</ol>\n'))
    assert toc.html() == key

    toc.attributes = (('format', 'collapsed'),)
    assert toc.html() == key

    # Match the expanded toc (format: 'expanded')
    toc.attributes = (('format', 'expanded'),)
    key = '\n'.join(('<ol class="toc-document">',
                     '  <li>',
                     '    <a href="file1.html">file1</a>',
                     '    <ol class="toc-heading">',
                     '      <li>',
                     '        <a href="file1.html">section</a>',
                     '      </li>',
                     '    </ol>',
                     '  </li>',
                     '  <li>My second document'
                     '<ol class="toc-heading">'
                     '<li>subsection</li><li>section</li></ol></li>',
                     '  <li>',
                     '    <a href="file3.html">The third document</a>',
                     '    <ol class="toc-heading">',
                     '      <li>',
                     '        <a href="file3.html">section</a>',
                     '      </li>',
                     '    </ol>',
                     '  </li>',
                     '</ol>\n'))
    assert toc.html() == key

    # Match the abbreviated toc (format: 'abbreviated')
    toc.attributes = (('format', 'abbreviated'),)
    key = '\n'.join(('<ol class="toc-document">',
                     '  <li><a href="file1.html">file1</a></li>',
                     '  <li>My second document'
                     '<ol class="toc-heading">'
                     '<li>subsection</li><li>section</li></ol></li>',
                     '  <li><a href="file3.html">The third document</a></li>',
                     '</ol>\n'))
    assert toc.html() == key
