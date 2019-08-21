"""
Test the Document utilities functions.
"""
from pathlib import Path

from disseminate.paths import SourcePath
from disseminate.document.utils import (find_project_paths,
                                        find_root_src_filepaths,
                                        load_root_documents)
from disseminate.utils.tests import strip_leading_space


def test_find_project_paths():
    """Test the find_project_paths function."""

    # find the project_paths
    project_paths = find_project_paths('tests')

    # Make sure the correct root paths are in the project_paths
    # tests/document/example1/
    # ├── dummy.dm
    # ├── dummy.html
    # └── dummy.tex
    assert Path('tests/document/example1') in project_paths

    # tests/document/example2/
    # ├── noheader.dm
    # └── withheader.dm
    assert Path('tests/document/example2') in project_paths

    # tests/document/example3/
    # └── sample.png
    # The following directory has subdirectories. Only the root path should be
    # listed in the project_paths
    assert Path('tests/document/example3') not in project_paths

    # tests/document/example4/
    # └── src
    #     └── file.dm
    assert Path('tests/document/example4/src') in project_paths

    # tests/document/example5/
    # ├── index.dm
    # ├── sub1
    # │   └── index.dm
    # ├── sub2
    # │   ├── index.dm
    # │   └── subsub2
    # │       └── index.dm
    # └── sub3
    #     └── index.dm
    assert Path('tests/document/example5') in project_paths
    assert Path('tests/document/example5/sub1') not in project_paths
    assert Path('tests/document/example5/sub2') not in project_paths
    assert Path('tests/document/example5/sub3') not in project_paths

    # tests/document/example6/
    # └── src
    #     ├── file1.dm  (includes file2.dm)
    #     └── file2.dm
    assert Path('tests/document/example6/src') in project_paths

    # Test example9. It has a main.dm in the 'tests/document/example9' directory
    # and a subfile in 'tests/document/example9/sub/sub/sub.dm'. The basepath
    # 'tests/document/example9' should be a project path, but
    # 'tests/document/example9/sub' or 'tests/document/example9/sub/sub' should
    # not
    assert Path('tests/document/example9') in project_paths
    assert Path('tests/document/example9/sub') not in project_paths
    assert Path('tests/document/example9/sub/sub') not in project_paths

    # tests/document/example7/
    # └── src
    #     ├── file1.dm
    #     └── sub1
    #         ├── file11.dm
    #         └── subsub1
    #             └── file111.dm
    assert Path('tests/document/example7/src') in project_paths
    assert (Path('tests/document/example7/src/sub1')
            not in project_paths)
    assert (Path('tests/document/example7/src/sub1/subsub1')
            not in project_paths)


def _check_src_filepaths(src_filepaths, only_root=False):
    """Tests for src_filepaths from the tests directory"""
    # tests/document/example1/
    # ├── dummy.dm
    # ├── dummy.html
    # └── dummy.tex
    assert Path('tests/document/example1/dummy.dm') in src_filepaths

    # tests/document/example2/
    # ├── noheader.dm
    # └── withheader.dm
    assert Path('tests/document/example2/withheader.dm') in src_filepaths
    assert Path('tests/document/example2/noheader.dm') in src_filepaths

    # tests/document/example4/
    # └── src
    #     └── file.dm
    assert Path('tests/document/example4/src/file.dm') in src_filepaths

    # tests/document/example5/
    # ├── index.dm
    # ├── sub1
    # │   └── index.dm
    # ├── sub2
    # │   ├── index.dm
    # │   └── subsub2
    # │       └── index.dm
    # └── sub3
    #     └── index.dm
    assert Path('tests/document/example5/index.dm') in src_filepaths
    assert Path('tests/document/example5/sub1') not in src_filepaths
    assert Path('tests/document/example5/sub2') not in src_filepaths
    assert Path('tests/document/example5/sub3') not in src_filepaths

    # tests/document/example6/
    # └── src
    #     ├── file1.dm  (includes file2.dm)
    #     └── file2.dm
    assert Path('tests/document/example6/src/file1.dm') in src_filepaths

    if only_root:
        assert Path('tests/document/example6/src/file2.dm') not in src_filepaths
    else:
        assert Path('tests/document/example6/src/file2.dm') in src_filepaths

    # tests/document/example7/
    # └── src
    #     ├── file1.dm
    #     └── sub1
    #         ├── file11.dm
    #         └── subsub1
    #             └── file111.dm
    assert Path('tests/document/example7/src/file1.dm') in src_filepaths
    assert (Path('tests/document/example7/src/sub1/file11.dm')
            not in src_filepaths)
    assert (Path('tests/document/example7/src/sub1/subsub1/file111.dm')
            not in src_filepaths)


def test_find_root_src_filepaths():
    """Test the find_root_src_filepaths function"""

    # find the root src_filepaths
    src_filepaths = find_root_src_filepaths('tests')

    # Check the src_filepaths
    _check_src_filepaths(src_filepaths)


def test_load_root_documents_src_filepaths(tmpdir):
    """Test the load_root_documents function and the src_filepaths
    of root documents."""

    # 1. load the root documents
    documents = load_root_documents('tests/document')

    # Get the src_filepaths for these documents
    src_filepaths = [d.src_filepath for d in documents]

    # Check the src_filepaths
    _check_src_filepaths(src_filepaths, only_root=True)

    # 2. Create a srcfile in the tmpdir, render it and check the paths
    src_path = SourcePath(tmpdir, 'src')
    src_path.mkdir()
    src_filepath = SourcePath(project_root=src_path, subpath='test.dm')

    markup = """
    ---
    targets: html
    ---
    This is my first test
    """
    src_filepath.write_text(strip_leading_space(markup))

    documents = load_root_documents(path=str(tmpdir))

    assert len(documents) == 1
    doc = documents.pop()
    assert doc.src_filepath == src_filepath

    # Render and check the destination files
    doc.render()
    target_filepath = tmpdir / 'html' / 'test.html'
    assert target_filepath.exists()


def test_load_root_documents_project_target_roots(tmpdir):
    """Test the load_root_documents function and the project_roots and
    target_roots of root documents."""

    # 1. load the root documents
    documents = load_root_documents('tests/document')

    # Get the src_filepaths and project_roots for these documents
    src_filepaths = [d.src_filepath for d in documents]
    project_roots = [src_filepath.project_root
                     for src_filepath in src_filepaths]
    target_roots = [doc.target_root for doc in documents]

    # tests/document/example1/
    # ├── dummy.dm
    # ├── dummy.html
    # └── dummy.tex
    assert Path('tests/document/example1') in project_roots
    assert Path('tests/document/example1') in target_roots


    # tests/document/example2/
    # ├── noheader.dm
    # └── withheader.dm
    assert Path('tests/document/example2') in project_roots
    assert Path('tests/document/example2') in target_roots

    # tests/document/example4/
    # └── src
    #     └── file.dm
    assert Path('tests/document/example4/src') in project_roots
    assert Path('tests/document/example4') in target_roots

    # tests/document/example5/
    # ├── index.dm
    # ├── sub1
    # │   └── index.dm
    # ├── sub2
    # │   ├── index.dm
    # │   └── subsub2
    # │       └── index.dm
    # └── sub3
    #     └── index.dm
    assert Path('tests/document/example5') in project_roots
    assert Path('tests/document/example5/sub1') not in project_roots
    assert Path('tests/document/example5/sub2') not in project_roots
    assert Path('tests/document/example5/sub3') not in project_roots
    assert Path('tests/document/example5') in target_roots

    # tests/document/example6/
    # └── src
    #     ├── file1.dm  (includes file2.dm)
    #     └── file2.dm
    assert Path('tests/document/example6/src') in project_roots
    assert Path('tests/document/example6') in target_roots

    # tests/document/example7/
    # └── src
    #     ├── file1.dm
    #     └── sub1
    #         ├── file11.dm
    #         └── subsub1
    #             └── file111.dm
    assert Path('tests/document/example7/src') in project_roots
    assert (Path('tests/document/example7/src/sub1')
            not in src_filepaths)
    assert (Path('tests/document/example7/src/sub1/subsub1')
            not in src_filepaths)
    assert Path('tests/document/example7') in target_roots


def test_load_root_documents_specific_path():
    """Test the load_root_documents function using the specific path for a
    root document"""

    # Use example7
    # tests/document/example7/
    # └── src
    #     ├── file1.dm
    #     └── sub1
    #         ├── file11.dm
    #         └── subsub1
    #             └── file111.dm

    documents = load_root_documents('tests/document/example7/src/file1.dm')
    assert len(documents) == 1
    assert (documents[0].src_filepath ==
            Path('tests/document/example7/src/file1.dm'))
    assert (documents[0].project_root ==
            Path('tests/document/example7/src'))
    assert (documents[0].target_root ==
            Path('tests/document/example7'))
