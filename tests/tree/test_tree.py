"""
Tests for the index tree
"""
import pytest

from disseminate import Tree
from disseminate.tree import TreeException


def test_basic_index():
    """Tests a basic index tree file."""
    tree = Tree()

    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory
    index = tree.find_index_files(subpath='tests/tree/examples1/')

    # The index should have one item because there's one index file.
    assert len(index) == 1

    # The index should have the index's file's directory as a key
    assert 'tests/tree/examples1/sub1' in index

    # The value for this key should be the markup files in that directory,
    # in order
    assert (index['tests/tree/examples1/sub1'] ==
            ['tests/tree/examples1/sub1/intro.dm',
             'tests/tree/examples1/sub1/appendix.dm'])


def test_duplicate_index():
    """Tests an index tree file with duplicate entries."""
    tree = Tree()

    # The 'examples2' directory contains an index.tree in the 'examples2/sub1'
    # directory with duplicate 'intro.dm'
    with pytest.raises(TreeException):
        index = tree.find_index_files(subpath='tests/tree/examples2/')


def test_missing_file():
    """Tests an index tree file with a missing entry."""
    tree = Tree()

    # The 'examples3' directory contains an index.tree in the 'examples3/sub1'
    # directory with a missing file 'missing.dm'
    with pytest.raises(TreeException):
        index = tree.find_index_files(subpath='tests/tree/examples3/')


def test_basic_document_search():
    """Tests the find_document_files method."""
    tree = Tree()

    # The 'examples1' directory contains document (markup) files in the root
    # directory and in the 'sub1' directory
    index = tree.find_document_files(subpath='tests/tree/examples1')

    # The 'examples1' directory has 3 document files. 1 in the root, and 2 in
    # the 'sub1' sub-directory
    assert len(index) == 2

    key1 = 'tests/tree/examples1'
    assert key1 in index
    assert len(index[key1]) == 1
    assert 'tests/tree/examples1/index.dm' in index[key1]

    key2 = 'tests/tree/examples1/sub1'
    assert key2 in index
    assert len(index[key2]) == 2
    assert 'tests/tree/examples1/sub1/intro.dm' in index[key2]
    assert 'tests/tree/examples1/sub1/appendix.dm' in index[key2]
