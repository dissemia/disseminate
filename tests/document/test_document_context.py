"""
Tests the DocumentContext class.
"""
from pathlib import Path

from disseminate import SourcePath, TargetPath
from disseminate.document import DocumentContext
from disseminate.tags import TagFactory


# Setup example paths
ex4_root = Path("tests") / "document" / "examples" / "ex4" / "src"
ex4_subpath = Path("file.dm")
ex7_root = Path("tests") / "document" / "examples" / "ex7" / "src"
ex7_subpath = Path("file1.dm")


# A DummyDocument class
class DummyDocument(object):
    src_filepath = SourcePath()
    project_root = SourcePath()
    target_root = TargetPath()


def test_document_context_basic_inheritence(context_cls, tmpdir):
    """Test the proper inheritence of the document context."""
    class Mock(object):
        """Mock object without a 'copy' method."""
        pass

    # Create a DocumentContext with one entry in the class's 'do_not_inherit'
    # class attribute and one not in 'do_not_inherit'
    parent_context = {'paths': [],
                      'src_filepath': SourcePath('tests/document/example1',
                                                 'dummy.dm'),
                      'project_root': SourcePath('tests/document/example1'),
                      'target_root': TargetPath(tmpdir),
                      'label_manager': Mock(),
                      }
    parent_context = context_cls(**parent_context)

    doc = DummyDocument()
    context = DocumentContext(document=doc, parent_context=parent_context,
                              doc_id='dummy.dm', mtime=1)

    def test_context_entries(context):
        # Check the entries that should be inherited by the parent
        assert context['src_filepath'] != parent_context['src_filepath']
        assert context['src_filepath'] == SourcePath('')
        assert context['doc_id'] == 'dummy.dm'
        assert isinstance(context['mtime'], float)
        assert context['project_root'] == parent_context['project_root']
        assert context['target_root'] == parent_context['target_root']
        assert context['document']() == doc  # dereference weakref
        assert context['label_manager'] == parent_context['label_manager']

        # Check that the persistent objects, like the label_manager, are the
        # *same* object
        assert (id(context['label_manager']) ==
                id(parent_context['label_manager']))

        # Check items that *should not* be inherited
        assert 'paths' in context.do_not_inherit

        assert 'paths' in context
        assert context['paths'] == [SourcePath('.'),
                                    SourcePath('tests/document/example1')]

        # The 'paths' list itself should not have been inherited
        assert id(parent_context['paths']) != id(context['paths'])

    # Test that the attributes were properly setup
    test_context_entries(context)

    # Now reset the context and make sure the parent_context entries are still
    # in place
    context.reset()
    test_context_entries(context)


def test_document_context_simple_documents(load_example):
    """Test the preservation of the parent context with subdocuments."""
    # Load example4. It has a main document (file.dm)
    doc = load_example(ex4_root / ex4_subpath)
    label_manager = doc.label_manager

    assert label_manager is not None

    def test_context_entries(doc):
        context = doc.context
        # Check the entries that should be inherited by the parent
        assert context['src_filepath'] == doc.src_filepath
        assert context['project_root'] == doc.src_filepath.project_root
        assert context['target_root'] == doc.target_root
        assert context['document']() == doc  # dereference weakref
        assert context['root_document']() == doc  # dereference weakref
        assert context['doc_id'] == doc.doc_id
        assert context['label_manager'] == label_manager

        # Check that the persistent objects, like the label_manager, are the
        # *same* object
        assert id(context['label_manager']) == id(label_manager)

        # Check items that *should not* be inherited
        assert 'paths' in context.do_not_inherit

        assert 'paths' in context
        assert doc.src_filepath.project_root in context['paths']

    # Test the context
    test_context_entries(doc)

    # Reset the context, and test again
    doc.context.reset()
    test_context_entries(doc)

    # Load example7. It has a main document (file1.dm) and 1 subdocuments
    # (sub1/file11.dm), which has its own subdocument (subsub1/file111.dm)
    doc = load_example(ex7_root / ex7_subpath)
    label_manager = doc.label_manager

    assert label_manager is not None

    def test_context_entries(doc):
        context = doc.context
        # Check the entries that should be inherited by the parent
        assert context['src_filepath'] == doc.src_filepath
        assert context['project_root'] == doc.src_filepath.project_root
        assert context['target_root'] == doc.target_root
        assert context['document']() == doc  # dereference weakref
        assert context['root_document']() == doc  # dereference weakref

        assert context['label_manager'] == label_manager

        # Check that the persistent objects, like the label_manager, are the
        # *same* object
        assert id(context['label_manager']) == id(label_manager)

        # Check items that *should not* be inherited
        assert 'paths' in context.do_not_inherit

        assert 'paths' in context
        assert doc.src_filepath.project_root in context['paths']

        # Test the subdocuments
        subdocs = doc.documents_list(only_subdocuments=True, recursive=True)

        assert len(subdocs) == 2
        src_filepath1 = SourcePath(project_root=ex7_root,
                                   subpath=Path('sub1') / 'file11.dm')
        src_filepath2 = SourcePath(project_root=ex7_root,
                                   subpath=(Path('sub1') / 'subsub1' /
                                            'file111.dm'))
        assert subdocs[0].src_filepath == src_filepath1
        assert subdocs[1].src_filepath == src_filepath2

    # Test the context
    test_context_entries(doc)

    # Reset the context, and test again
    doc.context.reset()
    test_context_entries(doc)


def test_document_context_nested_load(doc):
    """Test the DocumentContext with header entries with nested values."""

    # Write a sample header and re-load the file
    doc.src_filepath.write_text("""
    ---
    label_fmts:
      heading: "My heading @label.title "
    ---
    """)
    doc.load()

    # Check updated label
    assert doc.context['label_fmts']['heading'] == "My heading @label.title "


def test_document_context_is_valid(load_example):
    """Test the is_valid method for document contexts."""

    # Load example4. It has a main document (file.dm)
    doc = load_example(ex4_root / ex4_subpath)
    context = doc.context

    # The initial context is valid.
    assert context.is_valid()

    # Now remove the mtime key and this should invalidate the context
    del context['mtime']
    assert not context.is_valid()


def test_document_context_includes(doc):
    """Test the DocumentContext includes property."""

    src_filepath = SourcePath(project_root='.',)
    context = doc.context
    context['include'] = "  sub/file1.dm\n  sub/file2.dm"
    context['src_filepath'] = src_filepath
    paths = context.includes
    assert paths == [SourcePath('sub/file1.dm'),
                     SourcePath('sub/file2.dm')]

    # With spaces in filename
    context['include'] = "  sub/file 1.dm\n  sub/file 2.dm "
    paths = context.includes
    assert paths == [SourcePath('sub/file 1.dm'),
                     SourcePath('sub/file 2.dm')]

    # With spaces in filename and extra newlines
    context['include'] = ("  sub/file 1.dm\n  "
                          "\nsub/file 2.dm ")
    paths = context.includes
    assert paths == [SourcePath('sub/file 1.dm'),
                     SourcePath('sub/file 2.dm')]

    # Tests with a src_filepath that is not the current directory
    src_filepath = SourcePath(project_root='src', subpath='main.dm')
    context['src_filepath'] = src_filepath
    context['include'] = "  sub/file1.dm\n  sub/file2.dm"
    paths = context.includes
    assert paths == [SourcePath('src/sub/file1.dm'),
                     SourcePath('src/sub/file2.dm')]
    assert ([p.project_root for p in paths] ==
            [SourcePath('src'), SourcePath('src')])
    assert ([p.subpath for p in paths] ==
            [SourcePath('sub/file1.dm'), SourcePath('sub/file2.dm')])

    # Test and empty include
    context['include'] = ""
    assert context.includes == []

    del context['include']
    assert context.includes == []


def test_document_context_tag_inheritance(context_cls):
    """Test tag inheritance for contexts."""

    # Create a parent context with a toc tag
    parent = context_cls()
    toc = TagFactory.tag(tag_name='toc', tag_content='heading collapsed',
                         tag_attributes='', context=parent)
    parent['toc'] = toc

    # Now create a child context with a toc entry that is a string. It should
    # be converted to a toc tag
    child = context_cls(toc='heading expanded', parent_context=parent)

    assert id(child['toc']) != id(toc)  # a new tag was created
    assert type(child['toc']) == type(toc)  # of the same type
    assert child['toc'].content == 'heading expanded'  # different contents
