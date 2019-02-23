"""
Test the utility functions for contexts.
"""
from disseminate.context.utils import context_includes, set_context_attribute
from disseminate.paths import SourcePath
from copy import deepcopy


def test_context_includes(context_cls):
    """Test the context_includes function."""
    context_cls.validation_types = {'src_filepath': SourcePath}

    src_filepath = SourcePath(project_root='.',)
    src_filepath = deepcopy(src_filepath)
    context = context_cls(include="  sub/file1.dm\n  sub/file2.dm",
                          src_filepath=src_filepath)
    paths = context_includes(context)
    assert paths == [SourcePath('sub/file1.dm'),
                     SourcePath('sub/file2.dm')]

    # With spaces in filename
    context = context_cls(include="  sub/file 1.dm\n  sub/file 2.dm ",
                          src_filepath=src_filepath)
    paths = context_includes(context)
    assert paths == [SourcePath('sub/file 1.dm'),
                     SourcePath('sub/file 2.dm')]

    # With spaces in filename and extra newlines
    context = context_cls(include="  sub/file 1.dm\n  \nsub/file 2.dm ",
                          src_filepath=src_filepath)
    paths = context_includes(context)
    assert paths == [SourcePath('sub/file 1.dm'),
                     SourcePath('sub/file 2.dm')]

    # Tests with a src_filepath that is not the current directory
    src_filepath=SourcePath(project_root='src', subpath='main.dm')
    context = context_cls(include="  sub/file1.dm\n  sub/file2.dm",
                          src_filepath=src_filepath)
    paths = context_includes(context)
    assert paths == [SourcePath('src/sub/file1.dm'),
                     SourcePath('src/sub/file2.dm')]
    assert ([p.project_root for p in paths] ==
            [SourcePath('src'), SourcePath('src')])
    assert ([p.subpath for p in paths] ==
            [SourcePath('sub/file1.dm'), SourcePath('sub/file2.dm')])

    # Test and empty include
    context = context_cls(include="",
                          src_filepath=src_filepath)
    assert context_includes(context) == []

    context = context_cls(src_filepath=src_filepath)
    assert context_includes(context) == []


def test_set_context_attribute():
    """Test the set_context_attribution function."""

    context = {}

    class A(object):
        context = None

    a = A()

    # 1. Try a single object
    set_context_attribute(element=a, new_context=context)
    assert id(context) == id(a.context)

    # 2. Try an object in a list
    a.context = None
    set_context_attribute(element=[1, 'a', a], new_context=context)
    assert id(context) == id(a.context)

    # 3. Try an object in a nested list
    a.context = None
    set_context_attribute(element=[1, 'a', [1, 2, a]], new_context=context)
    assert id(context) == id(a.context)
