"""
Tests the management of labels with documents.
"""
from disseminate.document import Document


def test_document_labels(tmpdir):
    """Test the correct assignment of labels for a document."""

    # Setup the project_root in a temp directory
    project_root = tmpdir.join('src')
    project_root.mkdir()
    target_root = tmpdir

    # Make a document source file
    src_filepath = project_root.join('test.dm')
    src_filepath.ensure(file=True)  # touch the file

    # Create a document
    doc = Document(str(src_filepath), str(target_root))

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
    # Load example4, which has a file.dm with a 'toc' entry in the heading
    # for documents.
    doc = Document('tests/document/example4/src/file.dm',
                   target_root=str(tmpdir))

    # Render the doc
    doc.render()

    # Make sure the 'toc' context entry is correct
    toc_tag = doc.context['toc']
    assert toc_tag.name == 'toc'
    assert toc_tag.content == 'documents'

    key = """<ul class="toc-level-1">
  <li>
    <a href="/file.html">
      <span class="label">My first title</span>
    </a>
  </li>
</ul>
"""
    assert key == toc_tag.html()


def test_document_tree_updates_document_labels(tmpdir):
    """Test the updates to the document tree and labels."""
    # Create a document tree.
    src_path = tmpdir.join('src')
    src_path.mkdir()

    src_filepath1 = src_path.join('file1.dm')
    src_filepath2 = src_path.join('file2.dm')
    src_filepath3 = src_path.join('file3.dm')

    src_filepath1.write("""---
    include:
      file2.dm
      file3.dm
    ---""")
    src_filepath2.ensure()
    src_filepath3.ensure()

    # 1. Load the root document
    doc = Document(src_filepath=src_filepath1, target_root=str(tmpdir))
    label_manager = doc.context['label_manager']

    # There should now be 3 total documents and 3 sets of labels, one for each
    # document. Check the ordering of documents
    doc_list = doc.documents_list()
    assert len(doc_list) == 3
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath2)
    assert doc_list[2].src_filepath == str(src_filepath3)

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

    # 2. Now change the order of the sub-documents and reload the ast
    src_filepath1.write("""---
    include:
      file3.dm
      file2.dm
    ---""")
    doc.get_ast()

    # Check the ordering of documents
    doc_list = doc.documents_list()
    assert len(doc_list) == 3

    # There should be 3 labels, one for each document. However, they haven't
    # been registered yet since this is done when we get labels. The only
    # document whose ast has been reloaded and the labels have been reset is
    # document 1 so there should only be collected labels for this document.
    assert len(label_manager.collected_labels) == 1

    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath3)
    assert doc_list[2].src_filepath == str(src_filepath2)

    # Check the ordering of labels
    label_list = label_manager.get_labels()  # register labels
    assert len(label_manager.labels) == 3
    assert label_list[0].id == 'doc:file1.dm'
    assert label_list[1].id == 'doc:file3.dm'
    assert label_list[2].id == 'doc:file2.dm'

    # 3. Now remove one document
    src_filepath1.write("""---
    include:
      file2.dm
    ---""")

    # The documents shouldn't change until the ast is reloaded
    doc_list = doc.documents_list()
    assert len(doc_list) == 3

    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath3)
    assert doc_list[2].src_filepath == str(src_filepath2)

    # Reload the ast
    doc.get_ast()

    doc_list = doc.documents_list()
    assert len(doc_list) == 2
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath2)

    label_list = label_manager.get_labels()  # register labels
    assert len(label_manager.labels) == 2
    assert label_list[0].id == 'doc:file1.dm'
    assert label_list[1].id == 'doc:file2.dm'

    # 4. Now add the document back
    src_filepath1.write("""---
    include:
      file2.dm
      file3.dm
    ---""")

    # Reload the ast
    doc.get_ast()
    doc_list = doc.documents_list()
    assert len(doc_list) == 3
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath2)
    assert doc_list[2].src_filepath == str(src_filepath3)

    label_list = label_manager.get_labels()
    assert len(label_list) == 3
    assert label_list[0].id == 'doc:file1.dm'
    assert label_list[1].id == 'doc:file2.dm'
    assert label_list[2].id == 'doc:file3.dm'


def test_document_tree_updates_with_section_labels(tmpdir):
    """Test how updating the document tree impacts the numbering of labels."""

    # Create a document tree.
    src_path = tmpdir.join('src')
    src_path.mkdir()

    src_filepath1 = src_path.join('file1.dm')
    src_filepath2 = src_path.join('file2.dm')
    src_filepath3 = src_path.join('file3.dm')

    src_filepath1.write("""
    ---
    include:
      file2.dm
      file3.dm
    targets: html
    ---
    @chapter{file1}
    """)
    src_filepath2.write("""
    @chapter{file2}
    """)
    src_filepath3.write("""
    @chapter{file3}
    """)

    # 1. Load the root document
    doc = Document(src_filepath=src_filepath1, target_root=str(tmpdir))

    # Check the order of the documents
    doc_list = doc.documents_list(only_subdocuments=False, recursive=True)
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[0].number == 1
    assert doc_list[1].src_filepath == str(src_filepath2)
    assert doc_list[1].number == 2
    assert doc_list[2].src_filepath == str(src_filepath3)
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
    mtime1 = tmpdir.join('html').join('file1.html').mtime()
    mtime2 = tmpdir.join('html').join('file2.html').mtime()
    mtime3 = tmpdir.join('html').join('file3.html').mtime()

    # Now try reordering the files and see if the labels are reordered
    src_filepath1.write("""
    ---
    include:
      file3.dm
      file2.dm
    ---
    @chapter{file1}
    """)
    doc.get_ast()  # reload the file

    # Check the order of the documents
    doc_list = doc.documents_list(only_subdocuments=False, recursive=True)
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[0].number == 1
    assert doc_list[1].src_filepath == str(src_filepath3)
    assert doc_list[1].number == 2
    assert doc_list[2].src_filepath == str(src_filepath2)
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

    assert doc1.render_required(str(tmpdir.join('html').join('file1.html')))
    assert doc2.render_required(str(tmpdir.join('html').join('file2.html')))
    assert doc3.render_required(str(tmpdir.join('html').join('file3.html')))

    # The files have therefore been updated
    doc.render()
    assert mtime1 != tmpdir.join('html').join('file1.html').mtime()
    assert mtime2 != tmpdir.join('html').join('file2.html').mtime()
    assert mtime3 != tmpdir.join('html').join('file3.html').mtime()
