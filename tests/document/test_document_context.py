"""
Tests the DocumentContext class.
"""
from disseminate import SourcePath, TargetPath
from disseminate.document import DocumentContext, Document


# A DummyDocument class
class DummyDocument(object):
    src_filepath = SourcePath()
    project_root = SourcePath()
    target_root = TargetPath()


def test_document_context_basic_inheritence(context_cls, tmpdir):
    """Test the proper inheritence of the document context."""
    # Create a DocumentContext with one entry in the class's 'do_not_inherit'
    # class attribute and one not in 'do_not_inherit'
    parent_context = {'paths': [],
                      'src_filepath': SourcePath('tests/document/example1',
                                                 'dummy.dm'),
                      'project_root': SourcePath('tests/document/example1'),
                      'target_root': TargetPath(tmpdir),
                      'label_manager': dict(),
                      'dependency_manager': dict(),
                      }
    parent_context = context_cls(**parent_context)

    doc = DummyDocument()
    context = DocumentContext(document=doc, parent_context=parent_context,
                              doc_id='dummy.dm', mtime=1)

    def test_context_entries(context):
        # Check the entries that should be inherited by the parent
        assert context['src_filepath'] != parent_context['src_filepath']  # Not inherited
        assert context['src_filepath'] == SourcePath('')
        assert context['doc_id'] == 'dummy.dm'
        assert isinstance(context['mtime'], float)
        assert context['project_root'] == parent_context['project_root']
        assert context['target_root'] == parent_context['target_root']
        assert context['document']() == doc  # dereference weakref
        assert context['label_manager'] == parent_context['label_manager']
        assert (context['dependency_manager'] ==
                parent_context['dependency_manager'])

        # Check that the persistent objects, like the label_manager, are the
        # *same* object
        assert (id(context['label_manager']) ==
                id(parent_context['label_manager']))
        assert (id(context['dependency_manager']) ==
                id(parent_context['dependency_manager']))

        # Check items that *should not* be inherited
        assert 'paths' in context.do_not_inherit

        assert 'paths' in context
        assert context['paths'] == [SourcePath('tests/document/example1')]

        # The 'paths' list itself should not have been inherited
        assert id(parent_context['paths']) != id(context['paths'])

    # Test that the attributes were properly setup
    test_context_entries(context)

    # Now reset the context and make sure the parent_context entries are still
    # in place
    context.reset()
    test_context_entries(context)


def test_document_context_simple_documents(tmpdir):
    """Test the preservation of the parent context with subdocuments."""
    src_filepath = SourcePath(project_root='tests/document/example4/src',
                              subpath='file.dm')
    target_root = TargetPath(target_root=tmpdir)

    # Load example4. It has a main document (file.dm)
    doc = Document(src_filepath, target_root)
    label_manager = doc.label_manager
    dependency_manager = doc.dependency_manager

    assert label_manager is not None
    assert dependency_manager is not None

    def test_context_entries(doc):
        context = doc.context
        # Check the entries that should be inherited by the parent
        assert context['src_filepath'] == src_filepath
        assert context['project_root'] == src_filepath.project_root
        assert context['target_root'] == target_root
        assert context['document']() == doc  # dereference weakref
        assert context['root_document']() == doc  # dereference weakref
        assert context['doc_id'] == doc.doc_id

        assert context['label_manager'] == label_manager
        assert context['dependency_manager'] == dependency_manager

        # Check that the persistent objects, like the label_manager, are the
        # *same* object
        assert (id(context['label_manager']) ==
                id(label_manager))
        assert (id(context['dependency_manager']) ==
                id(dependency_manager))

        # Check items that *should not* be inherited
        assert 'paths' in context.do_not_inherit

        assert 'paths' in context
        assert src_filepath.project_root in context['paths']

    # Test the context
    test_context_entries(doc)

    # Reset the context, and test again
    doc.reset_contexts()
    test_context_entries(doc)

    # Load example7. It has a main document (file1.dm) and 1 subdocuments
    # (sub1/file11.dm), which has its own subdocument (subsub1/file111.dm)
    src_filepath = SourcePath(project_root='tests/document/example7/src',
                              subpath='file1.dm')
    target_root = TargetPath(tmpdir)
    doc = Document(src_filepath, target_root)
    label_manager = doc.label_manager
    dependency_manager = doc.dependency_manager

    assert label_manager is not None
    assert dependency_manager is not None

    def test_context_entries(doc):
        context = doc.context
        # Check the entries that should be inherited by the parent
        assert context['src_filepath'] == src_filepath
        assert context['project_root'] == src_filepath.project_root
        assert context['target_root'] == target_root
        assert context['document']() == doc  # dereference weakref
        assert context['root_document']() == doc  # dereference weakref

        assert context['label_manager'] == label_manager
        assert context['dependency_manager'] == dependency_manager

        # Check that the persistent objects, like the label_manager, are the
        # *same* object
        assert (id(context['label_manager']) ==
                id(label_manager))
        assert (id(context['dependency_manager']) ==
                id(dependency_manager))

        # Check items that *should not* be inherited
        assert 'paths' in context.do_not_inherit

        assert 'paths' in context
        assert src_filepath.project_root in context['paths']

        # Test the subdocuments
        subdocs = doc.documents_list(only_subdocuments=True, recursive=True)

        assert len(subdocs) == 2
        src_filepath1 = SourcePath(project_root='tests/document/example7/src',
                                   subpath='sub1/file11.dm')
        src_filepath2 = SourcePath(project_root='tests/document/example7/src',
                                   subpath='sub1/subsub1/file111.dm')
        assert subdocs[0].src_filepath == src_filepath1
        assert subdocs[1].src_filepath == src_filepath2

    # Test the context
    test_context_entries(doc)

    # Reset the context, and test again
    doc.reset_contexts()
    test_context_entries(doc)


def test_document_context_is_valid(tmpdir):
    """Test the is_valid method for document contexts."""
    src_filepath = SourcePath(project_root='tests/document/example4/src',
                              subpath='file.dm')
    target_root = TargetPath(target_root=tmpdir)

    # Load example4. It has a main document (file.dm)
    doc = Document(src_filepath, target_root)
    context = doc.context

    # The initial context is valid.
    assert context.is_valid()

    # Now remove the mtime key and this should invalidate the context
    del context['mtime']
    assert not context.is_valid()
