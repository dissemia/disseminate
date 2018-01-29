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


def test_convert_src_filepath():
    """Tests the conversion of src_filepaths to target_filepaths."""

    target_list = ['.html', ".tex"]
    # First we try getting paths without the segregate_targets option

    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory and no index.tree in the root directory 'examples1'.
    # Consequently, 'examples1/sub' is considered managed and 'examples1' is
    # not. The 'examples1/' directory only contains on document (source markup)
    # file.
    tree1 = Tree(subpath="tests/tree/examples1", target_list=target_list)
    tree1.find_documents()

    # There should be 3 src_filepath files. The following target_filepaths are:
    target_paths = ('tests/tree/examples1/sub1/intro.html',
                    'tests/tree/examples1/sub1/appendix.html',
                    'tests/tree/examples1/index.html')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_paths):
        targets = tree1.convert_src_filepath(src_filepath,
                                             target_list=['.html'],
                                             segregate_target=False)
        converted_path = targets['.html']
        assert converted_path == target_filepath

    # This time we'll try the same thing, but with a '.tex' target
    tree1 = Tree(subpath="tests/tree/examples1", target_list=target_list)
    tree1.find_documents()

    # There should be 3 target_path files, relative to the project root
    # 'tests/tree/examples/'
    target_filepaths = ('tests/tree/examples1/sub1/intro.tex',
                        'tests/tree/examples1/sub1/appendix.tex',
                        'tests/tree/examples1/index.tex')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_filepaths):
        targets = tree1.convert_src_filepath(src_filepath,
                                             target_list=['.tex'],
                                             segregate_target=False)
        converted_path = targets['.tex']
        assert converted_path == target_filepath

    # Next we try the same thing, but with the segregated_target option

    # examples1
    tree1 = Tree(subpath="tests/tree/examples1", target_list=target_list)
    tree1.find_documents()

    # There should be 3 src_filepath files. The following target_filepaths are:
    target_filepaths = ('tests/tree/examples1/html/sub1/intro.html',
                        'tests/tree/examples1/html/sub1/appendix.html',
                        'tests/tree/examples1/html/index.html')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_filepaths):
        targets = tree1.convert_src_filepath(src_filepath,
                                             target_list=['.html'],
                                             segregate_target=True)
        converted_path = targets['.html']
        assert converted_path == target_filepath

    # This time we'll try the same thing, but with a '.tex' target
    tree1 = Tree(subpath="tests/tree/examples1", target_list=target_list)
    tree1.find_documents()

    # There should be 3 target_path files, relative to the project root
    # 'tests/tree/examples/'
    target_filepaths = ('tests/tree/examples1/tex/sub1/intro.tex',
                        'tests/tree/examples1/tex/sub1/appendix.tex',
                        'tests/tree/examples1/tex/index.tex')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_filepaths):
        targets = tree1.convert_src_filepath(src_filepath,
                                             target_list=['.tex'],
                                             segregate_target=True)
        converted_path = targets['.tex']
        assert converted_path == target_filepath

    # Now test a customized output directory without target segregation
    tree1 = Tree(subpath="tests/tree/examples1",
                 output_dir=".",
                 target_list=target_list)
    tree1.find_documents()

    # There should be 3 src_filepath files. The following target_filepaths are:
    target_filepaths = ('./sub1/intro.html',
                        './sub1/appendix.html',
                        './index.html')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_filepaths):
        targets = tree1.convert_src_filepath(src_filepath,
                                             segregate_target=False)
        converted_path = targets['.html']
        assert converted_path == target_filepath

    # And test a customized output directory with target segregation
    tree1 = Tree(subpath="tests/tree/examples1",
                 output_dir=".",
                 target_list=target_list)
    tree1.find_documents()

    # There should be 3 src_filepath files. The following target_filepaths are:
    target_filepaths = ('./html/sub1/intro.html',
                        './html/sub1/appendix.html',
                        './html/index.html')
    for src_filepath, target_filepath in zip(tree1.src_filepaths,
                                             target_filepaths):
        targets = tree1.convert_src_filepath(src_filepath,
                                             segregate_target=True)
        converted_path = targets['.html']
        assert converted_path == target_filepath


def test_convert_src_filepath_absolute(tmpdir):
    """Tests the conversion of src_filepaths to target_filepaths with
    absolute directories."""
    # Create a series of src documents
    src_path = tmpdir.mkdir("src")
    f1 = src_path.join("index1.dm")
    f2 = src_path.join("index2.dm")

    # Save text and create new fieles
    f1.write("@{index1}")
    f2.write("@{index2}")

    target_list = ['.html', ".tex"]
    # First we try getting paths without the segregate_targets option

    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory and no index.tree in the root directory 'examples1'.
    # Consequently, 'examples1/sub' is considered managed and 'examples1' is
    # not. The 'examples1/' directory only contains on document (source markup)
    # file.
    tree = Tree(subpath=src_path, target_list=target_list)
    tree.find_documents()

    # Test the correct population of the src_filepaths
    assert tree.src_filepaths[0] == f1
    assert tree.src_filepaths[1] == f2

    # Test the correct idenfication of the project_root
    assert tree.project_root() == os.path.relpath(src_path, ".")

    # Test the convert of src_filepaths to target_filepaths
    project_root = tree.project_root()
    target_paths = (project_root + '/html/index1.html',
                    project_root + '/html/index2.html',)
    for src_filepath, target_filepath in zip(tree.src_filepaths, target_paths):
        converted_html = tree.convert_src_filepath(src_filepath)['.html']
        assert target_filepath == converted_html


def test_convert_target_filepath(tmpdir):
    """Tests the conversion of target paths to source paths."""
    output_dir = tmpdir.realpath()

    target_list = ['.html']
    # First we try getting paths without the segregate_targets option

    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory and no index.tree in the root directory 'examples1'.
    # Consequently, 'examples1/sub' is considered managed and 'examples1' is
    # not. The 'examples1/' directory only contains on document (source markup)
    # file.
    tree1 = Tree(subpath="tests/tree/examples1", target_list=target_list,
                 output_dir=output_dir)

    # There should be 3 src_filepath files. The following target_filepaths are:
    target_filepaths = (output_dir + '/html/sub1/intro.html',
                        output_dir + '/html/sub1/appendix.html',
                        output_dir + '/html/index.html')

    # The target paths can't be converted without finding documents first and
    # rendering them
    with pytest.raises(TreeException):
        tree1.convert_target_filepath(target_filepaths[0])

    # Now find the documents and see if the source paths can be converted.
    source_filepaths = ("tests/tree/examples1/sub1/intro.dm",
                        "tests/tree/examples1/sub1/appendix.dm",
                        "tests/tree/examples1/index.dm")

    tree1.find_documents()
    tree1.render()

    for src_filepath, target_filepath in zip(source_filepaths,
                                             target_filepaths):
        filepath, target = tree1.convert_target_filepath(target_filepath)
        assert filepath == src_filepath


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
    tree1.render(target_list=['.html'])

    # Check to see that the targets were all rendered
    target_filepaths = (output_dir + '/html/sub1/intro.html',
                        output_dir + '/html/sub1/appendix.html',
                        output_dir + '/html/index.html')
    for src_path, target_path in zip(tree1.src_filepaths, target_filepaths):
        doc = tree1.documents[src_path]
        path1 = doc.targets['.html']
        assert path1 == target_path
        assert os.path.isfile(path1)


def test_update_render(tmpdir):
    """Tests that new and updated files only are rendered."""
    # Create a series of src documents
    src_path = tmpdir.mkdir("src")
    f1 = src_path.join("index1.dm")
    f2 = src_path.join("index2.dm")

    # Save text and create new fieles
    f1.write("@{index1}")
    f2.write("@{index2}")

    # Create a tree and render
    tree = Tree(subpath=str(src_path))
    tree.render()

    # Check that the target files have been created
    target_paths = (os.path.relpath(src_path + "/html/index1.html", "."),
                    os.path.relpath(src_path + "/html/index2.html", "."))
    for src_filepath, target_path in zip(tree.src_filepaths, target_paths):
        doc = tree.documents[src_filepath]
        assert doc.targets['.html'] == target_path
        assert os.path.isfile(target_path)

    # Get the mtimes for the documents
    mtime1 = os.stat(target_paths[0]).st_mtime
    mtime2 = os.stat(target_paths[1]).st_mtime

    # Update one of the files, and see which is rendered.
    ast1, ast2 = [tree.documents[s]._ast for s in tree.src_filepaths]

    f2.write("@{new index2}")
    tree.render()

    newast1, newast2 = [tree.documents[s]._ast for s in tree.src_filepaths]

    # The ast for document 2 should change, but not the one for document 1
    assert ast1 == newast1
    assert ast2 != newast2

    # The document2 should have changed, but not document1
    assert mtime1 == os.stat(target_paths[0]).st_mtime
    assert mtime2 < os.stat(target_paths[1]).st_mtime

    # Try adding a new file
    f3 = src_path.join("index3.dm")
    f3.write("@{index3}")
    tree.render()

    assert len(tree.src_filepaths) == 3
    assert len(tree.documents) == 3

    # Now delete it
    f3.remove()
    tree.render()

    assert len(tree.src_filepaths) == 2
    assert len(tree.documents) == 2
    assert [newast1, newast2] == [tree.documents[s]._ast
                                  for s in tree.src_filepaths]


def test_html(tmpdir):
    """Tests the html method."""
    # The 'examples1' directory contains an index.tree in the 'examples1/sub1'
    # directory and no index.tree in the root directory 'examples1'.
    # Consequently, 'examples1/sub' is considered managed and 'examples1' is
    # not. The 'examples1/' directory only contains on document (source markup)
    # file.
    subpath = "tests/tree/examples1"
    tree1 = Tree(subpath=subpath)
    tree1.find_documents()

    html = tree1.html()

    # The result html string should have the subpath as the project root
    assert subpath in html

    # The result html string should have 3 table rows: one for each of the
    # documents
    assert html.count("<tr>") == 3

