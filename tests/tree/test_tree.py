"""
Tests for the index tree
"""
import pytest

from disseminate import Tree
from disseminate.tree import TreeException, load_index_files


def test_find_managed_dirs():
    """Tests that the managed directories are correctly found."""
    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory with two document files. Therefore the sub1 directory is
    # considered managed
    tree1 = Tree(subpath="tests/tree/examples1")
    tree1.find_managed_dirs()

    assert isinstance(tree1.managed_dirs, dict)
    assert len(tree1.managed_dirs) == 1
    key1 = 'tests/tree/examples1/sub1'
    assert key1 in tree1.managed_dirs
    assert tree1.managed_dirs[key1] == 'tests/tree/examples1/sub1/index.tree'

    # The 'examples5' directory contains an index.tree file in the root
    # directory (tests/tree/examples5) and an index.tree file in each of the
    # 'sub1', 'sub2', 'sub2/subsub2' and 'sub3' sub-directories.
    # However, the root index.tree file manages all of the sub-directories.
    # The managed_dirs attribute should have 5 directories (root and 4
    # sub-directories) all pointing to the same index.tree in the root
    # directory.
    tree5 = Tree(subpath="tests/tree/examples5")
    tree5.find_managed_dirs()

    assert isinstance(tree5.managed_dirs, dict)
    assert len(tree5.managed_dirs) == 5

    index_file = 'tests/tree/examples5/index.tree'
    for key in ('tests/tree/examples5',
                'tests/tree/examples5/sub1',
                'tests/tree/examples5/sub2',
                'tests/tree/examples5/sub2/subsub2',
                'tests/tree/examples5/sub3'):
        assert key in tree5.managed_dirs
        assert tree5.managed_dirs[key] == index_file


def test_load_index_files():
    """Tests that the tree index files are properly read."""
    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory with two document files.
    documents = load_index_files('tests/tree/examples1/sub1/index.tree')

    # The documents list should have two items for the two document (markup
    # source files) identified in the index.tree
    assert len(documents) == 2
    assert documents[0] == 'tests/tree/examples1/sub1/intro.dm'
    assert documents[1] == 'tests/tree/examples1/sub1/appendix.dm'

    # The 'examples5' directory contains an index.tree file in the root
    # directory (tests/tree/examples5). This file includes a pointer to
    # the index.tree files in 'sub1' and 'sub2' but not 'sub3'. The index.tree
    # files point to a single document file in sub1, but it points to a document
    # and an index.tree in sub2.
    documents = load_index_files('tests/tree/examples5/index.tree')

    # The documents list should have four items: one index.dm in the project
    # root, and one in each of 'sub1', 'sub2' and 'sub2/subsub2'.
    # The sub2 file is listed before sub1

    assert len(documents) == 4
    assert documents[0] == 'tests/tree/examples5/index.dm'
    assert documents[1] == 'tests/tree/examples5/sub2/index.dm'
    assert documents[2] == 'tests/tree/examples5/sub2/subsub2/index.dm'
    assert documents[3] == 'tests/tree/examples5/sub1/index.dm'


#
# def test_basic_index():
#     """Tests a basic index tree file."""
#     tree = Tree()
#
#     # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
#     # directory with two document files
#     index = tree.find_index_files(subpath='tests/tree/examples1/')
#
#     # The index should have two items, one for each document in the index tree
#     # file.
#     assert len(index) == 2
#
#     # The index should have the index's file's directory as a key
#     assert index[0] == ('tests/tree/examples1/sub1', 'intro.dm')
#     assert index[1] == ('tests/tree/examples1/sub1', 'appendix.dm')
#
#
# def test_duplicate_index():
#     """Tests an index tree file with duplicate entries."""
#     tree = Tree()
#
#     # The 'examples2' directory contains an index.tree in the 'examples2/sub1'
#     # directory with duplicate 'intro.dm'
#     with pytest.raises(TreeException):
#         index = tree.find_index_files(subpath='tests/tree/examples2/')
#
#
# def test_missing_file():
#     """Tests an index tree file with a missing entry."""
#     tree = Tree()
#
#     # The 'examples3' directory contains an index.tree in the 'examples3/sub1'
#     # directory with a missing file 'missing.dm'
#     with pytest.raises(TreeException):
#         index = tree.find_index_files(subpath='tests/tree/examples3/')
#
#
# def test_subdirectories_index():
#     """Tests an index tree that refers to files in a subdirectory."""
#     tree = Tree()
#
#     # The 'examples4' directory contains an index.tree in the 'examples4/sub1'
#     # directory with 3 document files: 'intro.dm', 'appendix.dm' and
#     # 'subsub1/intro.dm'
#     index = tree.find_index_files(subpath='tests/tree/examples4/')
#
#     # The index should have three directory entries
#     assert len(index) == 3
#
#     assert index[0] == ('tests/tree/examples4/sub1', 'intro.dm')
#     assert index[1] == ('tests/tree/examples4/sub1', 'appendix.dm')
#     assert index[2] == ('tests/tree/examples4/sub1/subsub1', 'intro.dm')
#
# def test_nested_indexes()
#     """Tests index tree files with index tree files within them."""
#
#
# def test_basic_document_search():
#     """Tests the find_document_files method."""
#     tree = Tree()
#
#     # The 'examples1' directory contains document (markup) files in the root
#     # directory and in the 'sub1' directory
#     index = tree.find_document_files(subpath='tests/tree/examples1')
#
#     # The 'examples1' directory has 3 document files. 1 in the root, and 2 in
#     # the 'sub1' sub-directory
#     assert len(index) == 2
#
#     key1 = 'tests/tree/examples1'
#     assert key1 in index
#     assert len(index[key1]) == 1
#     assert 'tests/tree/examples1/index.dm' in index[key1]
#
#     key2 = 'tests/tree/examples1/sub1'
#     assert key2 in index
#     assert len(index[key2]) == 2
#     assert 'tests/tree/examples1/sub1/intro.dm' in index[key2]
#     assert 'tests/tree/examples1/sub1/appendix.dm' in index[key2]
