"""
Tests the management of labels with documents.
"""
from pathlib import Path

from disseminate.document import Document
from disseminate import SourcePath, TargetPath
from disseminate import settings

# Setup example paths
ex4_root = Path("tests") / "document" / "examples" / "ex4" / "src"
ex4_subpath = Path("file.dm")


def test_document_labels(env):
    """Test the correct assignment of labels for a document."""
    # Setup the paths
    tmpdir = env.project_root
    project_root = SourcePath(project_root=tmpdir, subpath='src')
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')
    project_root.mkdir()
    src_filepath.touch()

    # Create a document
    doc = Document(src_filepath, environment=env)

    # 1. Test the label when the '_project_root' value is not assigned in the
    #    global_context. In this case, the label is identified by the document's
    #    src_filepath

    # The label should have been created on document creation
    man = doc.context['label_manager']
    label = man.get_label(id="doc:test-dm")  # Registers labels
    assert len(man.labels) == 1
    assert label.id == "doc:test-dm"
    assert label.kind == ('document', 'document-level-1')


def test_document_toc(env):
    """Test the generation of a toc from the header of a document."""
    # Setup the paths
    tmpdir = env.project_root
    src_filepath = SourcePath(project_root=ex4_root, subpath=ex4_subpath)
    target_root = TargetPath(target_root=tmpdir)

    # Load example4, which has a file.dm with a 'toc' entry in the heading
    # for documents.
    doc = Document(src_filepath, environment=env)

    # Setup the settings in the context
    context = doc.context
    context['base_url'] = '/{target}/{subpath}'
    context['process_context_tags'] = {'toc'}
    context['relative_links'] = False

    # build the doc for the html target
    assert doc.build() == ['done']

    # Make sure the 'toc' context entry is correct
    toc_tag = doc.context['toc']
    assert toc_tag.name == 'toc'
    key = ('<ul class="toc">'
             '<li class="toc-level-1"><a href="" class="ref">My first title</a></li>'
           '</ul>\n')
    assert toc_tag.html == key


def test_document_tree_updates_document_labels(env, wait):
    """Test the updates to the document tree and labels."""
    # Create a document tree.
    tmpdir = env.project_root
    project_root = tmpdir / 'src'
    project_root.mkdir()
    target_root = TargetPath(tmpdir)

    src_filepath1 = SourcePath(project_root=project_root, subpath='file1.dm')
    src_filepath2 = SourcePath(project_root=project_root, subpath='file2.dm')
    src_filepath3 = SourcePath(project_root=project_root, subpath='file3.dm')

    src_filepath1.write_text("""---
    include:
      file2.dm
      file3.dm
    ---""")
    wait()  # sleep time offset needed for different mtimes
    src_filepath2.touch()
    wait()  # sleep time offset needed for different mtimes
    src_filepath3.touch()

    # 1. Load the root document
    doc = Document(src_filepath=src_filepath1, environment=env)
    label_manager = doc.context['label_manager']

    # There should now be 3 total documents and 3 sets of labels, one for each
    # document. Check the ordering of documents
    doc_list = doc.documents_list()
    assert len(doc_list) == 3
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath2
    assert doc_list[2].src_filepath == src_filepath3

    # There should be 3 labels, one for each document
    assert len(label_manager.labels) == 3

    # Get the labels, and register them
    label_list = list(label_manager.get_labels_by_kind())

    assert label_list[0].id == 'doc:file1-dm'
    assert label_list[1].id == 'doc:file2-dm'
    assert label_list[2].id == 'doc:file3-dm'

    # 2. Now change the order of the sub-documents and reload the document
    src_filepath1.write_text("""---
    include:
      file3.dm
      file2.dm
    ---""")
    doc.load()

    # Check the ordering of documents
    doc_list = doc.documents_list()
    assert len(doc_list) == 3

    # There should be 3 labels, one for each document. Changing the root
    # document reloads all documents
    assert len(label_manager.labels) == 3

    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath3
    assert doc_list[2].src_filepath == src_filepath2

    # Check the ordering of labels
    label_list = list(label_manager.get_labels_by_kind())  # register labels
    assert len(label_list) == 3
    assert label_list[0].id == 'doc:file1-dm'
    assert label_list[1].id == 'doc:file3-dm'
    assert label_list[2].id == 'doc:file2-dm'

    # 3. Now remove one document
    wait()  # sleep time offset needed for different mtimes
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
    doc.load()

    doc_list = doc.documents_list()
    assert len(doc_list) == 2
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath2

    label_list = list(label_manager.get_labels_by_kind())  # register labels
    assert len(label_manager.labels) == 2
    assert label_list[0].id == 'doc:file1-dm'
    assert label_list[1].id == 'doc:file2-dm'

    # 4. Now add the document back
    wait()  # sleep time offset needed for different mtimes
    src_filepath1.write_text("""---
    include:
      file2.dm
      file3.dm
    ---""")

    # Reload the document
    doc.load()
    doc_list = doc.documents_list()
    assert len(doc_list) == 3
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath2
    assert doc_list[2].src_filepath == src_filepath3

    label_list = list(label_manager.get_labels_by_kind())
    assert len(label_list) == 3
    assert label_list[0].id == 'doc:file1-dm'
    assert label_list[1].id == 'doc:file2-dm'
    assert label_list[2].id == 'doc:file3-dm'


def test_document_tree_updates_with_section_labels(env, wait):
    """Test how updating the document tree impacts the numbering of labels."""

    # 1. First, test decoupled documents

    # Create a document tree.
    tmpdir = env.project_root
    project_root = tmpdir / 'src'
    project_root.mkdir()
    target_root = TargetPath(tmpdir)

    src_filepath1 = SourcePath(project_root=project_root, subpath='file1.dm')
    src_filepath2 = SourcePath(project_root=project_root, subpath='file2.dm')
    src_filepath3 = SourcePath(project_root=project_root, subpath='file3.dm')

    src_filepath1.write_text("""
    ---
    include:
      file2.dm
      file3.dm
    targets: html
    ---
    @chapter{file1}
    """)
    wait()  # sleep time offset needed for different mtimes

    src_filepath2.write_text("""
    @chapter{file2}
    """)
    wait()  # sleep time offset needed for different mtimes

    src_filepath3.write_text("""
    @chapter{file3}
    """)
    wait()  # sleep time offset needed for different mtimes

    # Load the root document
    doc = Document(src_filepath=src_filepath1, environment=env)

    # Check the order of the documents
    doc_list = doc.documents_list(only_subdocuments=False, recursive=True)
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath2
    assert doc_list[2].src_filepath == src_filepath3

    # Check the ordering of labels
    label_manager = doc.context['label_manager']
    labels = label_manager.get_labels_by_kind()
    title_labels = label_manager.get_labels_by_kind(kinds='chapter')

    # Check the number of labels: 3 for documents, 3 for chapters
    assert len(labels) == 6
    assert len(title_labels) == 3  # one for each file
    assert title_labels[0].id == 'ch:file1-dm-file1'
    assert title_labels[1].id == 'ch:file2-dm-file2'
    assert title_labels[2].id == 'ch:file3-dm-file3'

    # Build the files for the html target
    assert doc.build() == ['done']
    target_filepath1 = doc_list[0].target_filepath('.html')
    target_filepath2 = doc_list[1].target_filepath('.html')
    target_filepath3 = doc_list[2].target_filepath('.html')
    mtime1 = target_filepath1.stat().st_mtime
    mtime2 = target_filepath2.stat().st_mtime
    mtime3 = target_filepath3.stat().st_mtime

    # Now try reordering the files and see if the labels are reordered
    wait()  # sleep time offset needed for different mtimes
    src_filepath1.write_text("""
    ---
    include:
      file3.dm
      file2.dm
    ---
    @chapter{file1}
    """)
    doc.load()  # reload the file

    # Check the order of the documents
    doc_list = doc.documents_list(only_subdocuments=False, recursive=True)
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath3
    assert doc_list[2].src_filepath == src_filepath2

    # register labels
    title_labels = label_manager.get_labels_by_kind(kinds='chapter')

    # Check the number of labels: 3 for documents, 3 for chapters
    assert len(label_manager.labels) == 6
    assert len(title_labels) == 3  # one for each file
    assert title_labels[0].id == 'ch:file1-dm-file1'
    assert title_labels[1].id == 'ch:file3-dm-file3'
    assert title_labels[2].id == 'ch:file2-dm-file2'

    # A render should be required for file1.dm. This will also trigger
    # a load required for its subdocuments
    doc1, doc2, doc3 = doc.documents_list(only_subdocuments=False,
                                          recursive=True)

    assert doc1.build_needed()
    assert doc2.build_needed()
    assert doc3.build_needed()

    # The files have therefore been updated
    assert doc.build() == ['done']
    assert mtime1 < target_filepath1.stat().st_mtime  # reloaded
    assert mtime2 < target_filepath2.stat().st_mtime  # reloaded
    assert mtime3 < target_filepath3.stat().st_mtime  # reloaded

    # 2. Test coupled documents

    # First, test decoupled documents
    wait()  # sleep time offset needed for different mtimes
    src_filepath1.write_text("""
        ---
        include:
          file2.dm
        targets: html
        ---
        @chapter{file1}
        @ref{ch:file2-dm-file2}
        """)

    wait()  # sleep time offset needed for different mtimes
    src_filepath2.write_text("""
        @chapter{file2}
        """)

    # 1. Load the root document
    doc = Document(src_filepath=src_filepath1, environment=env)

    # Check the order of the documents
    doc_list = doc.documents_list(only_subdocuments=False, recursive=True)
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath2

    # Render the documents
    assert doc.build() == ['done']
    assert not doc_list[0].build_needed()
    assert not doc_list[1].build_needed()

    # Now touch the second document. doc2 will need a new render, since it's
    # updated, and doc1 will need a render since it depends on doc2
    wait()  # sleep time offset needed for different mtimes
    src_filepath2.touch()

    assert doc_list[0].build_needed()
    assert doc_list[1].build_needed()
