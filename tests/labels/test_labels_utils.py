"""
Test the utility functions
"""
from disseminate import Document
from disseminate.labels.utils import label_latest_mtime


def test_label_latest_mtime(tmpdir):
    """Test the label_latest_mtime function."""
    # Setup a document with 3 chapters
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

    assert len(label_manager.labels) == 4

    # The label with the highest modification time should be the last one.
    # The 'get_ast' method invokation reloads the ast.
    latest_mtime = label_latest_mtime(ast=doc.get_ast(), context=doc.context)
    assert label_manager.labels[0].mtime < latest_mtime  # document label
    assert label_manager.labels[1].mtime < latest_mtime  # chapter 1 label
    assert label_manager.labels[2].mtime < latest_mtime  # chapter 2 label
    assert label_manager.labels[3].mtime == latest_mtime  # chapter 3 label

    mtimes = dict()
    for count, label in enumerate(label_manager.labels):
        mtimes[count] = label.mtime

    # Change the first chapter and it should have the latest mtime.
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

    # Check the label modification times
    latest_mtime = label_latest_mtime(ast=doc.get_ast(), context=doc.context)
    assert label_manager.labels[0].mtime < latest_mtime  # document label
    assert label_manager.labels[1].mtime == latest_mtime  # chapter 1 label
    assert label_manager.labels[2].mtime < latest_mtime  # chapter 2 label
    assert label_manager.labels[3].mtime < latest_mtime  # chapter 3 label

    # Test changes in the label string itself
    # Test changes in the reference string
