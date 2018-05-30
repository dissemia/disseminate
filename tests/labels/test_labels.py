"""
Tests the label manager and label classes.
"""
from disseminate import Document


def test_basic_labels(tmpdir):
    """Tests the basic functionality of labels."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("")

    doc = Document(str(src_filepath), str(tmpdir))

    # Get the label manager
    label_man = doc.context['label_manager']

    # Generate a couple of generic labels. These have no id and cannot be
    # fetched
    label_man.add_label(document=doc, kind='figure')
    label_man.add_label(document=doc, kind='figure')

    # These are collected labels right now, and aren't registered. Labels
    # have to be retrieved with get_labels to register them.
    assert len(label_man.labels) == 0
    assert len(label_man.collected_labels[doc.src_filepath]) == 3

    # Getting labels returns only the document label
    labels = label_man.get_labels(document=doc)  # register labels
    assert len(labels) == 3

    label1 = labels[0]  # document label
    label2 = labels[1]  # figure label
    label3 = labels[2]  # figure label

    assert label1.kind == ('document', 'document-level-1')
    assert label2.kind == ('figure',)
    assert label3.kind == ('figure',)

    assert label1.local_order == (1, 1)
    assert label1.global_order == (1, 1)
    assert label2.local_order == (1,)
    assert label2.global_order == (1,)
    assert label3.local_order == (2,)
    assert label3.global_order == (2,)

    # Generate a couple of specific labels
    label_man.add_label(document=doc, kind='figure', id='fig:image1')
    label_man.add_label(document=doc, kind='figure', id='fig:image2')

    # Getting the labels will register the new labels, removing the old labels,
    # and leaving the 2 new labels
    labels = label_man.get_labels(document=doc)  # registers labels
    assert len(labels) == 2
    labels = label_man.get_labels(document=doc)
    assert len(labels) == 2

    label3 = label_man.get_label('fig:image1')
    label4 = label_man.get_label('fig:image2')

    assert labels == [label3, label4]

    # Get the labels and make sure they match
    assert label3 == label_man.get_label('fig:image1')
    assert label3.local_order == (1,)
    assert label3.global_order == (1,)
    assert label4 == label_man.get_label('fig:image2')
    assert label4.local_order == (2,)
    assert label4.global_order == (2,)


def test_get_labels(tmpdir):
    """Test the get_labels method."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("")

    doc = Document(str(src_filepath), str(tmpdir))

    # Get the label manager
    label_man = doc.context['label_manager']

    # Generate a couple of generic labels. These have no id and cannot be
    # fetched
    label_man.add_label(document=doc, kind='figure')
    label_man.add_label(document=doc, kind='figure')

    # Get all labels and register them. There should only be 3 registered
    # labels: the document's label and the 3 figure labels
    labels = label_man.get_labels()
    assert len(labels) == 3

    # Get labels for this document
    labels = label_man.get_labels(document=doc)
    assert len(labels) == 3

    # Get labels for another document (a string is used since the type is not
    # checked)
    labels = label_man.get_labels(document='other')
    assert labels == []

    # Filter by kind
    labels = label_man.get_labels(kinds='figure')
    assert len(labels) == 2
    assert labels[0].kind == ('figure',)
    assert labels[1].kind == ('figure',)

    labels = label_man.get_labels(kinds=['figure', 'h1'])
    assert len(labels) == 2
    assert labels[0].kind == ('figure',)
    assert labels[1].kind == ('figure',)

    labels = label_man.get_labels(kinds=['h1'])
    assert len(labels) == 0


def test_label_reordering(tmpdir):
    """Tests the reordering of labels when labels are registered."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("")

    # Create a sub-document
    src_filepath.write("""---
    include:
      tmp2.dm
      ---""")
    src_filepath2 = tmpdir.join('src').join('tmp2.dm')
    src_filepath2.write("")

    doc = Document(str(src_filepath), str(tmpdir))
    doc2 = list(doc.subdocuments.values())[0]

    # Get the label manager
    label_man = doc.context['label_manager']

    # Generate a couple of short labels
    label_man.add_label(document=doc, kind='figure')
    label_man.add_label(document=doc, kind='figure')

    # Generate a couple of short labels for the sub-document
    label_man.add_label(document=doc2, kind='figure')
    label_man.add_label(document=doc2, kind='figure')

    # Get and register the labels. This will include 2 document labels and 4
    # figure labels
    for i in range(2):
        labels = label_man.get_labels()
        assert len(labels) == 6

        label1, label2, label3, label4, label5, label6 = labels

        # Check the numbers and kind
        assert label1.kind == ('document', 'document-level-1')
        assert label1.local_order == (1, 1)
        assert label1.global_order == (1, 1)

        assert label2.kind == ('figure',)
        assert label2.local_order == (1,)
        assert label2.global_order == (1,)

        assert label3.kind == ('figure',)
        assert label3.local_order == (2,)
        assert label3.global_order == (2,)

        assert label4.kind == ('document', 'document-level-2')
        assert label4.local_order == (1, 1)
        assert label4.global_order == (2, 1)

        assert label5.kind == ('figure',)
        assert label5.local_order == (1,)
        assert label5.global_order == (3,)

        assert label6.kind == ('figure',)
        assert label6.local_order == (2,)
        assert label6.global_order == (4,)

    # Now reset the labels for the first document. The
    # corresponding labels should also disappear, leaving 3 labels.
    label_man.reset(document=doc)

    labels = label_man.get_labels()
    assert len(labels) == 3
    label4, label5, label6 = labels

    # Check the labels
    assert label4.kind == ('document', 'document-level-2')
    assert label4.local_order == (1, 1)
    assert label4.global_order == (1, 1)

    assert label5.kind == ('figure',)
    assert label5.local_order == (1,)
    assert label5.global_order == (1,)

    assert label6.kind == ('figure',)
    assert label6.local_order == (2,)
    assert label6.global_order == (2,)

    # Now delete the 2nd document and the labels should be removed too.
    doc2 = None
    doc.subdocuments.clear()
    assert len(label_man.get_labels()) == 0


def test_label_title(tmpdir):
    """Test the generation of titles for labels."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("""
    ---
    targets: html, txt
    ---
    @chapter{First Chapter}
    @section{My First Section. It has periods.}
    @subsection{My First SubSection, and
      it has multiple lines.}
    """)

    doc = Document(str(src_filepath), str(tmpdir))

    # Check the labels
    label_man = doc.context['label_manager']

    # There should be 4 labels: 1 for the document, 1 for chapter,
    # 1 for section and 1 for subsection
    labels = label_man.get_labels()
    assert len(labels) == 4

    # Get the heading labels
    heading_labels = label_man.get_labels(kinds='heading')
    assert len(heading_labels) == 3

    assert heading_labels[0].title == 'First Chapter'
    assert heading_labels[1].title == 'My First Section'
    assert heading_labels[2].title == ('My First SubSection, '
                                       'and it has multiple lines')


def test_label_number(tmpdir):
    """Test the number properties for labels."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("""
    ---
    targets: html, txt
    ---
    @chapter{First Chapter}
    @section{My First Section. It has periods.}
    @subsection{My First SubSection, and
      it has multiple lines.}
    """)

    doc = Document(str(src_filepath), str(tmpdir))

    # Check the labels
    label_man = doc.context['label_manager']

    # There should be 4 labels: 1 for the document, 1 for chapter,
    # 1 for section and 1 for subsection
    labels = label_man.get_labels()
    assert len(labels) == 4

    # Get the heading labels
    heading_labels = label_man.get_labels(kinds='heading')
    assert len(heading_labels) == 3

    assert heading_labels[0].number == 1
    assert heading_labels[1].number == 1
    assert heading_labels[2].number == 1

    assert heading_labels[0].tree_number == '1'
    assert heading_labels[1].tree_number == '1.1'
    assert heading_labels[2].tree_number == '1.1.1'


def test_label_mtime(tmpdir):
    """Test the label mtime method."""
    # 1. Setup a document with 3 chapters
    tmpdir.join('src').mkdir()
    src_filepath = tmpdir.join('src').join('test.dm')

    src_filepath.write("""
    ---
    targets: html
    ---
    @chapter[id=chapter-1]{Chapter 1}
    @ref{chapter-3}
    @chapter[id=chapter-2]{Chapter 2}
    @chapter[id=chapter-3]{Chapter 3}
    """)

    # Load the document
    doc = Document(str(src_filepath), str(tmpdir))
    doc.render()

    # Check that the labels were correctly loaded: 1 for the document and 1
    # for each of the 3 chapters.
    label_manager = doc.context['label_manager']

    labels = label_manager.get_labels()
    assert len(labels) == 4

    # The labels should all have the same modification time as the document
    doc_mtime = src_filepath.mtime()
    assert doc.context['mtime'] == doc_mtime
    assert label_manager.labels[0].mtime == doc_mtime  # document label
    assert label_manager.labels[1].mtime == doc_mtime  # chapter 1 label
    assert label_manager.labels[2].mtime == doc_mtime  # chapter 2 label
    assert label_manager.labels[3].mtime == doc_mtime  # chapter 3 label

    for label in label_manager.labels:
        assert label.document == doc

    # Determine the ids for the labels
    ids = [id(label) for label in label_manager.labels]

    # Change the first chapter. The labels should all now have an updated mtime
    src_filepath.write("""
    ---
    targets: html
    ---
    @chapter[id=chapter-1-intro]{Chapter 1}
    @ref{chapter-3}
    @chapter[id=chapter-2]{Chapter 2}
    @chapter[id=chapter-3]{Chapter 3}
    """)

    # Reload the AST
    doc.get_ast()

    # Check to see which labels have been created new.
    # The get_labels method registers the label changes.
    # The label.id for chapter 1 has changed, so a new label object should
    # have been created
    new_ids = [id(label) for label in label_manager.get_labels()]
    assert ids[0] == new_ids[0]  # document label
    assert ids[1] != new_ids[1]  # chapter 1 label
    assert ids[2] == new_ids[2]  # chapter 2 label
    assert ids[3] == new_ids[3]  # chapter 3 label

    # Check the label modification times. The labels were updated after the
    # original document's modification time.
    assert label_manager.labels[0].mtime > doc_mtime  # document label
    assert label_manager.labels[1].mtime > doc_mtime  # chapter 1 label
    assert label_manager.labels[2].mtime > doc_mtime  # chapter 2 label
    assert label_manager.labels[3].mtime > doc_mtime  # chapter 3 label

    # Check the label modification times. The labels were updated after the
    # last modification (i.e. when doc.get_ast() was issues).
    doc_mtime = src_filepath.mtime()
    assert doc.context['mtime'] == doc_mtime

    for label in label_manager.labels:
        assert label.document == doc

    # The label modification times should now match the new document's
    # modification time
    assert label_manager.labels[0].mtime == doc_mtime  # document label
    assert label_manager.labels[1].mtime == doc_mtime  # chapter 1 label
    assert label_manager.labels[2].mtime == doc_mtime  # chapter 2 label
    assert label_manager.labels[3].mtime == doc_mtime  # chapter 3 label
