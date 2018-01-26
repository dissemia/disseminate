"""
Tests for the index tree
"""
import pytest
import os.path

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


def test_basic_index():
    """Tests a basic index tree file."""
    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory with two document files
    tree1 = Tree(subpath='tests/tree/examples1')
    tree1.find_documents_in_indexes()

    # The tree's documents should have 2 documents (markup source files)
    assert len(tree1.src_filepaths) == 2
    assert tree1.src_filepaths[0] == 'tests/tree/examples1/sub1/intro.dm'
    assert tree1.src_filepaths[1] == 'tests/tree/examples1/sub1/appendix.dm'

    # The 'examples5' directory contains an index.tree file in the root
    # directory (tests/tree/examples5). This file includes a pointer to
    # the index.tree files in 'sub1' and 'sub2' but not 'sub3'. The index.tree
    # files point to a single document file in sub1, but it points to a document
    # and an index.tree in sub2.
    tree5 = Tree(subpath='tests/tree/examples5')
    tree5.find_documents_in_indexes()

    # The tree should have 4 documents from the root, sub1 and sub2 directories
    # (but not sub3)
    assert len(tree5.src_filepaths) == 4
    assert tree5.src_filepaths[0] == 'tests/tree/examples5/index.dm'
    assert tree5.src_filepaths[1] == 'tests/tree/examples5/sub2/index.dm'
    assert tree5.src_filepaths[2] == 'tests/tree/examples5/sub2/subsub2/index.dm'
    assert tree5.src_filepaths[3] == 'tests/tree/examples5/sub1/index.dm'

    # The 'examples6' directory contains an index.tree file in the 'sub1' and
    # 'sub2' directories but not 'sub3'. The documents read in from the tree
    # index files should include those listed in 'sub1' (1 file), 'sub2'
    # (1 file) but not 'sub3'
    tree6 = Tree(subpath='tests/tree/examples6')
    tree6.find_documents_in_indexes()

    # The tree should have 2 documents, one from each sub1 and sub2.
    assert len(tree6.src_filepaths) == 2
    assert tree6.src_filepaths[0] == 'tests/tree/examples6/sub1/index.dm'
    assert tree6.src_filepaths[1] == 'tests/tree/examples6/sub2/index.dm'


def test_duplicate_index():
    """Tests an index tree file with duplicate entries."""
    tree = Tree()

    # The 'examples2' directory contains an index.tree in the
    # 'examples2/sub1' directory with duplicate 'intro.dm'
    subpath = 'tests/tree/examples2/'
    with pytest.raises(TreeException):
        tree.find_documents_in_indexes(subpath=subpath)

def test_missing_file():
    """Tests an index tree file with a missing entry."""
    tree = Tree()

    # The 'examples3' directory contains an index.tree in the 'examples3/sub1'
    # directory with a missing file 'missing.dm'
    with pytest.raises(TreeException):
        tree.find_documents_in_indexes(subpath='tests/tree/examples3/')

def test_unmanaged_dirs():
    """Tests the loading of unmanaged directories."""

    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory and no index.tree in the root directory 'examples1'.
    # Consequently, 'examples1/sub' is considered managed and 'examples1' is
    # not. The 'examples1/' directory only contains on document (source markup)
    # file.
    tree1 = Tree(subpath="tests/tree/examples1")
    tree1.find_documents_by_type()

    # There should only be 1 unmanaged document
    assert len(tree1.src_filepaths) == 1
    assert tree1.src_filepaths[0] == 'tests/tree/examples1/index.dm'

    # The 'examples5' directory has an index.tree file in the root 'examples5'
    # directory.
    # Consequently, it should not have any unmanaged files.
    tree5 = Tree()
    tree5.find_documents_by_type('tests/tree/examples5')

    # There should be no unmanaged documents
    assert len(tree5.src_filepaths) == 0

    # The 'examples6' directory has an index.tree file in the 'sub1' and 'sub2'
    # directories. The root 'examples6' directory, which contains 1 source file,
    # and the sub3 sub-directory, which contains 1 source file, are not managed
    # by index.tree files.
    tree6 = Tree(subpath='tests/tree/examples6')
    tree6.find_documents_by_type()

    # There should be 2 unmanaged documents. The root file comes first.
    assert len(tree6.src_filepaths) == 2
    assert tree6.src_filepaths[0] == 'tests/tree/examples6/index.dm'
    assert tree6.src_filepaths[1] == 'tests/tree/examples6/sub3/index.dm'

def test_find_documents():
    """Tests the find_documents method to locate files from tree index files
    and unmanaged directories together."""

    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory and no index.tree in the root directory 'examples1'.
    # Consequently, 'examples1/sub' is considered managed and 'examples1' is
    # not. The 'examples1/' directory only contains on document (source markup)
    # file.
    tree1 = Tree(subpath="tests/tree/examples1")
    tree1.find_documents()

    # There should by 2 managed documents in 'sub1' and 1 unmanaged document
    # in the root. The unmanaged document comes last.
    assert len(tree1.src_filepaths) == 3
    assert tree1.src_filepaths[0] == 'tests/tree/examples1/sub1/intro.dm'
    assert tree1.src_filepaths[1] == 'tests/tree/examples1/sub1/appendix.dm'
    assert tree1.src_filepaths[2] == 'tests/tree/examples1/index.dm'

    # The 'examples5' directory contains an index.tree file in the root
    # directory (tests/tree/examples5). This file includes a pointer to
    # the index.tree files in 'sub1' and 'sub2' but not 'sub3'. The index.tree
    # files point to a single document file in sub1, but it points to a document
    # and an index.tree in sub2. However, 'sub3' is managed, so it shouldn't
    # show up in the results of documents.
    tree5 = Tree(subpath='tests/tree/examples5')
    tree5.find_documents()

    # The tree should have 4 documents from the root, sub1 and sub2 directories
    # (but not sub3)
    assert len(tree5.src_filepaths) == 4
    assert tree5.src_filepaths[0] == 'tests/tree/examples5/index.dm'
    assert tree5.src_filepaths[1] == 'tests/tree/examples5/sub2/index.dm'
    assert tree5.src_filepaths[2] == ('tests/tree/examples5/sub2/subsub2/'
                                      'index.dm')
    assert tree5.src_filepaths[3] == 'tests/tree/examples5/sub1/index.dm'

    # The 'examples6' directory contains an index.tree file in the 'sub1' and
    # 'sub2' directories but not 'sub3'. The documents read in from the tree
    # index files should include those listed in the the 'sub1' directory
    # (1 file), and the 'sub2' directory (1 file). The unmanaged directories,
    # the root directory and 'sub3', each contain 1 file and they will be
    # included last.
    tree6 = Tree(subpath='tests/tree/examples6')
    tree6.find_documents()

    # The tree should have 2 documents, one from each sub1 and sub2.
    assert len(tree6.src_filepaths) == 4
    assert tree6.src_filepaths[0] == 'tests/tree/examples6/sub1/index.dm'
    assert tree6.src_filepaths[1] == 'tests/tree/examples6/sub2/index.dm'
    assert tree6.src_filepaths[2] == 'tests/tree/examples6/index.dm'
    assert tree6.src_filepaths[3] == 'tests/tree/examples6/sub3/index.dm'

    # The 'éxample 7' directory contains a unicode character and a space.
    # In the root folder, it has an index.tree file pointing to an index.dm
    # file
    tree7 = Tree(subpath='tests/tree/éxample 7')
    tree7.find_documents()

    # The tree should have 1 documents in the root
    assert len(tree7.src_filepaths) == 1
    assert tree7.src_filepaths[0] == 'tests/tree/éxample 7/index.dm'


def test_project_root():
    """Tests that the project root path is correctly identified."""

    # The 'examples1' directory contains files in the root directory and
    # in sub1. By using find_documents, we find both kinds.
    tree1 = Tree(subpath="tests/tree/examples1")
    tree1.find_documents()

    project_root = tree1.project_root()
    assert project_root == 'tests/tree/examples1'


    # The 'examples1' directory contains a tree index file only in the 'sub1'
    # directory. Therefore, if we only search for tree index files, the project
    # root should be the path with 'sub1'
    tree1 = Tree(subpath="tests/tree/examples1")
    tree1.find_documents_in_indexes()

    project_root = tree1.project_root()
    assert project_root == 'tests/tree/examples1/sub1'

    # The 'éxample\ 7" directory contains a space and a unicode character.
    # It contains an index.tree file.
    # See if this path is properly recognized.
    tree7 = Tree(subpath="tests/tree/éxample 7")
    tree7.find_documents()

    project_root = tree7.project_root()
    assert project_root == 'tests/tree/éxample 7'


def test_target_paths():
    """Tests the the target paths are correctly set."""

    # First we try getting paths without the segregate_targets option

    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory and no index.tree in the root directory 'examples1'.
    # Consequently, 'examples1/sub' is considered managed and 'examples1' is
    # not. The 'examples1/' directory only contains on document (source markup)
    # file.
    tree1 = Tree(subpath="tests/tree/examples1")
    tree1.find_documents()

    # There should be 3 src_filepath files. The following target_filepaths are:
    target_filepaths = ('sub1/intro.html',
                        'sub1/appendix.html',
                        'index.html')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_filepaths):
        converted_path = tree1.convert_target_path(src_filepath,
                                                   segregate_target=False)
        assert converted_path == target_filepath

    # This time we'll try the same thing, but with a '.tex' target
    tree1 = Tree(subpath="tests/tree/examples1", target='tex')
    tree1.find_documents()

    # There should be 3 target_path files, relative to the project root
    # 'tests/tree/examples/'
    target_filepaths = ('sub1/intro.tex',
                        'sub1/appendix.tex',
                        'index.tex')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_filepaths):
        converted_path = tree1.convert_target_path(src_filepath,
                                                   segregate_target=False)
        assert converted_path == target_filepath

    # Next we try the same thing, but with the segregated_target option

    # examples1
    tree1 = Tree(subpath="tests/tree/examples1")
    tree1.find_documents()

    # There should be 3 src_filepath files. The following target_filepaths are:
    target_filepaths = ('html/sub1/intro.html',
                        'html/sub1/appendix.html',
                        'html/index.html')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_filepaths):
        converted_path = tree1.convert_target_path(src_filepath,
                                                   segregate_target=True)
        assert converted_path == target_filepath

    # This time we'll try the same thing, but with a '.tex' target
    tree1 = Tree(subpath="tests/tree/examples1", target='tex')
    tree1.find_documents()

    # There should be 3 target_path files, relative to the project root
    # 'tests/tree/examples/'
    target_filepaths = ('tex/sub1/intro.tex',
                        'tex/sub1/appendix.tex',
                        'tex/index.tex')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_filepaths):
        converted_path = tree1.convert_target_path(src_filepath,
                                                   segregate_target=True)
        assert converted_path == target_filepath

    # Now test a customized output directory without target segregation
    tree1 = Tree(subpath="tests/tree/examples1",
                 output_dir="tests/tree/examples1")
    tree1.find_documents()

    # There should be 3 src_filepath files. The following target_filepaths are:
    target_filepaths = ('tests/tree/examples1/sub1/intro.html',
                        'tests/tree/examples1/sub1/appendix.html',
                        'tests/tree/examples1/index.html')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_filepaths):
        converted_path = tree1.convert_target_path(src_filepath,
                                                   segregate_target=False)
        assert converted_path == target_filepath

    # And test a customized output directory with target segregation
    tree1 = Tree(subpath="tests/tree/examples1",
                 output_dir="tests/tree/examples1")
    tree1.find_documents()

    # There should be 3 src_filepath files. The following target_filepaths are:
    target_filepaths = ('tests/tree/examples1/html/sub1/intro.html',
                        'tests/tree/examples1/html/sub1/appendix.html',
                        'tests/tree/examples1/html/index.html')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_filepaths):
        converted_path = tree1.convert_target_path(src_filepath,
                                                   segregate_target=True)
        assert converted_path == target_filepath


def test_render(tmpdir):
    """Tests the render method."""
    output_dir = tmpdir.realpath()

    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory and no index.tree in the root directory 'examples1'.
    # Consequently, 'examples1/sub' is considered managed and 'examples1' is
    # not. The 'examples1/' directory only contains on document (source markup)
    # file.
    subpath = "tests/tree/examples1"
    tree1 = Tree(subpath=subpath, output_dir=output_dir)
    tree1.find_documents()
    tree1.render()

    # Check to see that the targets were all rendered
    target_filepaths = (output_dir + '/html/sub1/intro.html',
                        output_dir + '/html/sub1/appendix.html',
                        output_dir + '/html/index.html')
    for path1, path2 in zip(tree1.target_filepaths, target_filepaths):
        assert path1 == path2
        assert os.path.isfile(path1)
