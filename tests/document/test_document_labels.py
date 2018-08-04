"""
Tests the management of labels with documents.
"""
from disseminate.document import Document
from disseminate import SourcePath, TargetPath


def test_document_labels(tmpdir, context_cls):
    """Test the correct assignment of labels for a document."""
    # Setup the paths
    project_root = SourcePath(project_root=tmpdir, subpath='src')
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')
    project_root.mkdir()
    src_filepath.touch()

    context_cls.validation_types = {'src_filepath': SourcePath,
                                    'paths': list}
    paths = [project_root]
    context = context_cls(src_filepath=src_filepath, paths=paths)

    # Create a document
    doc = Document(src_filepath, target_root)

    # 1. Test the label when the '_project_root' value is not assigned in the
    #    global_context. In this case, the label is identified by the document's
    #    src_filepath

    # The label should have been created on document creation
    man = doc.context['label_manager']
    label = man.get_label(id="doc:test.dm")  # Registers labels
    assert len(man.labels) == 1
    assert label.id == "doc:test.dm"
    assert label.kind == ('document', 'document-level-1')


def test_document_toc(tmpdir):
    """Test the generation of a toc from the header of a document."""
    # Setup the paths
    src_filepath = SourcePath(project_root='tests/document/example4/src',
                              subpath='file.dm')
    target_root = TargetPath(target_root=tmpdir)

    # Load example4, which has a file.dm with a 'toc' entry in the heading
    # for documents.
    doc = Document(src_filepath, target_root)

    # Setup the base_url
    doc.context['base_url'] = '/{target}/{subpath}'

    # Render the doc
    doc.render()

    # Make sure the 'toc' context entry is correct
    toc_tag = doc.context['toc']
    assert toc_tag.name == 'toc'
    key = """<span class="toc">
  <ul class="toc-level-2">
    <li>
      <a href="/html/file.html">
        <span class="label">My first title</span>
      </a>
    </li>
  </ul>
</span>
"""
    assert key == toc_tag.html


def test_document_tree_updates_document_labels(tmpdir):
    """Test the updates to the document tree and labels."""
    # Create a document tree.
    src_path = SourcePath(tmpdir, 'src')
    src_path.mkdir()
    target_root = TargetPath(tmpdir)

    src_filepath1 = SourcePath(src_path, 'file1.dm')
    src_filepath2 = SourcePath(src_path, 'file2.dm')
    src_filepath3 = SourcePath(src_path, 'file3.dm')

    src_filepath1.write_text("""---
    include:
      file2.dm
      file3.dm
    ---""")
    src_filepath2.touch()
    src_filepath3.touch()

    # 1. Load the root document
    doc = Document(src_filepath=src_filepath1, target_root=target_root)
    label_manager = doc.context['label_manager']

    # There should now be 3 total documents and 3 sets of labels, one for each
    # document. Check the ordering of documents
    doc_list = doc.documents_list()
    assert len(doc_list) == 3
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath2
    assert doc_list[2].src_filepath == src_filepath3

    # There should be 3 labels, one for each document. However, they haven't
    # been registered yet since this is done when we get labels
    assert len(label_manager.collected_labels) == 3
    assert len(label_manager.labels) == 0

    # Get the labels, and register them
    label_list = label_manager.get_labels()  # registers labels
    assert len(label_manager.collected_labels) == 0
    assert len(label_manager.labels) == 3

    assert label_list[0].id == 'doc:file1.dm'
    assert label_list[1].id == 'doc:file2.dm'
    assert label_list[2].id == 'doc:file3.dm'

    # 2. Now change the order of the sub-documents and reload the document
    src_filepath1.write_text("""---
    include:
      file3.dm
      file2.dm
    ---""")
    doc.load_document()

    # Check the ordering of documents
    doc_list = doc.documents_list()
    assert len(doc_list) == 3

    # There should be 3 labels, one for each document. However, they haven't
    # been registered yet since this is done when we get labels. The only
    # document whose ast has been reloaded and the labels have been reset is
    # document 1 so there should only be collected labels for this document.
    assert len(label_manager.collected_labels) == 1

    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath3
    assert doc_list[2].src_filepath == src_filepath2

    # Check the ordering of labels
    label_list = label_manager.get_labels()  # register labels
    assert len(label_manager.labels) == 3
    assert label_list[0].id == 'doc:file1.dm'
    assert label_list[1].id == 'doc:file3.dm'
    assert label_list[2].id == 'doc:file2.dm'

    # 3. Now remove one document
    src_filepath1.write_text("""---
    include:
      file2.dm
    ---""")

    # The documents shouldn't change until the ast is reloaded
    doc_list = doc.documents_list()
    assert len(doc_list) == 3

    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath3
    assert doc_list[2].src_filepath == src_filepath2

    # Reload the document
    doc.load_document()

    doc_list = doc.documents_list()
    assert len(doc_list) == 2
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath2

    label_list = label_manager.get_labels()  # register labels
    assert len(label_manager.labels) == 2
    assert label_list[0].id == 'doc:file1.dm'
    assert label_list[1].id == 'doc:file2.dm'

    # 4. Now add the document back
    src_filepath1.write_text("""---
    include:
      file2.dm
      file3.dm
    ---""")

    # Reload the document
    doc.load_document()
    doc_list = doc.documents_list()
    assert len(doc_list) == 3
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath2
    assert doc_list[2].src_filepath == src_filepath3

    label_list = label_manager.get_labels()
    assert len(label_list) == 3
    assert label_list[0].id == 'doc:file1.dm'
    assert label_list[1].id == 'doc:file2.dm'
    assert label_list[2].id == 'doc:file3.dm'


def test_document_tree_updates_with_section_labels(tmpdir):
    """Test how updating the document tree impacts the numbering of labels."""

    # Create a document tree.
    src_path = SourcePath(tmpdir, 'src')
    src_path.mkdir()
    target_root = TargetPath(tmpdir)

    src_filepath1 = SourcePath(src_path, 'file1.dm')
    src_filepath2 = SourcePath(src_path, 'file2.dm')
    src_filepath3 = SourcePath(src_path, 'file3.dm')

    src_filepath1.write_text("""
    ---
    include:
      file2.dm
      file3.dm
    targets: html
    ---
    @chapter{file1}
    """)
    src_filepath2.write_text("""
    @chapter{file2}
    """)
    src_filepath3.write_text("""
    @chapter{file3}
    """)

    # 1. Load the root document
    doc = Document(src_filepath=src_filepath1, target_root=target_root)

    # Check the order of the documents
    doc_list = doc.documents_list(only_subdocuments=False, recursive=True)
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[0].number == 1
    assert doc_list[1].src_filepath == src_filepath2
    assert doc_list[1].number == 2
    assert doc_list[2].src_filepath == src_filepath3
    assert doc_list[2].number == 3

    # Check the ordering of labels
    label_manager = doc.context['label_manager']
    labels = label_manager.get_labels()
    title_labels = label_manager.get_labels(kinds='heading')

    # Check the number of labels: 3 for documents, 3 for chapters
    assert len(labels) == 6
    assert len(title_labels) == 3  # one for each file
    assert title_labels[0].id == 'br:file1'
    assert title_labels[1].id == 'br:file2'
    assert title_labels[2].id == 'br:file3'

    # Render the files and check their mtimes
    doc.render()
    target_filepath1 = doc_list[0].target_filepath('.html')
    target_filepath2 = doc_list[1].target_filepath('.html')
    target_filepath3 = doc_list[2].target_filepath('.html')
    mtime1 = target_filepath1.stat().st_mtime
    mtime2 = target_filepath2.stat().st_mtime
    mtime3 = target_filepath3.stat().st_mtime

    # Now try reordering the files and see if the labels are reordered
    src_filepath1.write_text("""
    ---
    include:
      file3.dm
      file2.dm
    ---
    @chapter{file1}
    """)
    doc.load_document()  # reload the file

    # Check the order of the documents
    doc_list = doc.documents_list(only_subdocuments=False, recursive=True)
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[0].number == 1
    assert doc_list[1].src_filepath == src_filepath3
    assert doc_list[1].number == 2
    assert doc_list[2].src_filepath == src_filepath2
    assert doc_list[2].number == 3

    title_labels = label_manager.get_labels(kinds='heading')  # register labels

    # Check the number of labels: 3 for documents, 3 for chapters
    assert len(label_manager.labels) == 6
    assert len(title_labels) == 3  # one for each file
    assert title_labels[0].id == 'br:file1'
    assert title_labels[1].id == 'br:file3'
    assert title_labels[2].id == 'br:file2'

    # A render should be required since the labels have changed
    doc1, doc2, doc3 = doc.documents_list(only_subdocuments=False,
                                          recursive=True)

    assert doc1.render_required(target_filepath1)
    assert doc2.render_required(target_filepath2)
    assert doc3.render_required(target_filepath3)

    # The files have therefore been updated
    doc.render()
    assert mtime1 != target_filepath1.stat().st_mtime
    assert mtime2 != target_filepath2.stat().st_mtime
    assert mtime3 != target_filepath3.stat().st_mtime
