"""
Test the Document utilities functions.
"""
from pathlib import Path

from disseminate.document import Document
from disseminate.paths import SourcePath
from disseminate.document.utils import (find_project_paths, load_root_documents,
                                        translate_path)
from disseminate.document.document_context import DocumentContext
from disseminate.utils.tests import strip_leading_space


def test_find_project_paths():
    """Test the find_project_paths function."""

    # find the project_paths
    project_paths = find_project_paths('tests')

    # Make sure the correct root paths are in the project_paths
    assert Path('tests/document/example1') in project_paths
    assert Path('tests/document/example2') in project_paths
    assert Path('tests/document/example4/src') in project_paths

    # The following directory does not contain disseminate files and should not
    # be listed in the project_paths
    assert Path('tests/document/example3') not in project_paths

    # The following directory has subdirectories. Only the root path should be
    # listed in the project_paths
    assert Path('tests/document/example5') in project_paths
    assert Path('tests/document/example5/sub1') not in project_paths
    assert Path('tests/document/example5/sub2') not in project_paths
    assert Path('tests/document/example5/sub3') not in project_paths

    # Test example9. It has a main.dm in the 'tests/document/example9' directory
    # and a subfile in 'tests/document/example9/sub/sub/sub.dm'. The basepath
    # 'tests/document/example9' should be a project path, but
    # 'tests/document/example9/sub' or 'tests/document/example9/sub/sub' should
    # not
    assert Path('tests/document/example9') in project_paths
    assert Path('tests/document/example9/sub') not in project_paths
    assert Path('tests/document/example9/sub/sub') not in project_paths


def test_load_root_documents(tmpdir):
    """Test the load_root_documents function"""

    # 1. load the root documents
    documents = load_root_documents('tests/document')

    # Check the contexts
    for doc in documents:
        assert isinstance(doc.context, DocumentContext)

    # Get the src_filepaths for these documents
    src_filepaths = [d.src_filepath for d in documents]
    assert Path('tests/document/example1/dummy.dm') in src_filepaths
    assert Path('tests/document/example2/withheader.dm') in src_filepaths
    assert Path('tests/document/example2/noheader.dm') in src_filepaths
    assert Path('tests/document/example4/src/file.dm') in src_filepaths
    assert Path('tests/document/example5/index.dm') in src_filepaths

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


def test_translate_path(tmpdir):
    """Test the translate_path function."""
    tmpdir = Path(tmpdir)

    # 1. Load a document from example4. Example4 has a file in the 'src'
    #    directory
    target_root4 = tmpdir / 'example4'
    target_root4.mkdir()

    doc = Document('tests/document/example4/src/file.dm', target_root4)
    doc.render()

    # Find the document based on the src_filepath render path and relative to
    # the project root
    assert (translate_path('tests/document/example4/src/file.dm', [doc]) ==
            Path('tests/document/example4/src/file.dm'))
    assert (translate_path('file.dm', [doc]) ==
            Path('tests/document/example4/src/file.dm'))

    # Find the target based on the tgt_filepath relative to the target root
    # Test with and without the trailing slash
    assert (translate_path('file.html', [doc]) ==
            target_root4 / 'html' / 'file.html')
    assert (translate_path('/file.html', [doc]) ==
            target_root4 / 'html' / 'file.html')
    assert (translate_path('html/file.html', [doc]) ==
            target_root4 / 'html' / 'file.html')
    assert (translate_path('/html/file.html', [doc]) ==
            target_root4 / 'html' / 'file.html')

    # 2. Load documents from example5. Example5 has a file in the root
    #    directory, a file in the 'sub1', 'sub2' and 'sub3' directories and a
    #    file in the 'sub2/subsub2' directory
    target_root5 = tmpdir / 'example5'
    target_root5.mkdir()

    doc = Document('tests/document/example5/index.dm', str(target_root5))
    doc.render()

    # Find the documents based on src_filepath render paths
    docs = [doc]

    assert (translate_path('tests/document/example5/index.dm', docs) ==
            Path('tests/document/example5/index.dm'))
    assert (translate_path('tests/document/example5/sub1/index.dm', docs) ==
            Path('tests/document/example5/sub1/index.dm'))
    assert (translate_path('tests/document/example5/sub2/index.dm', docs) ==
            Path('tests/document/example5/sub2/index.dm'))
    assert (translate_path('tests/document/example5/sub2/subsub2/index.dm',
                           docs) ==
            Path('tests/document/example5/sub2/subsub2/index.dm'))
    assert (translate_path('tests/document/example5/sub3/index.dm', docs) ==
            Path('tests/document/example5/sub3/index.dm'))

    # Find the documents based on src_filepaths relative to the project_root.
    assert (translate_path('index.dm', docs) ==
            Path('tests/document/example5/index.dm'))
    assert (translate_path('sub1/index.dm', docs) ==
            Path('tests/document/example5/sub1/index.dm'))
    assert (translate_path('sub2/index.dm', docs) ==
            Path('tests/document/example5/sub2/index.dm'))
    assert (translate_path('sub2/subsub2/index.dm', docs) ==
            Path('tests/document/example5/sub2/subsub2/index.dm'))
    assert (translate_path('sub3/index.dm', docs) ==
            Path('tests/document/example5/sub3/index.dm'))

    # Find the documents based on tgt_filepath render paths.
    assert (translate_path('/index.html', docs) ==
            target_root5 / 'html' / 'index.html')
    assert (translate_path('/sub1/index.html', docs) ==
            target_root5 / 'html' / 'sub1' / 'index.html')
    assert (translate_path('/sub2/index.html', docs) ==
            target_root5 / 'html' / 'sub2' / 'index.html')
    assert (translate_path('/sub2/subsub2/index.html', docs) ==
            target_root5 / 'html' / 'sub2' / 'subsub2' / 'index.html')
    assert (translate_path('/sub3/index.html', docs) ==
            target_root5 / 'html' / 'sub3' / 'index.html')

    assert (translate_path('/html/index.html', docs) ==
            target_root5 / 'html' / 'index.html')
    assert (translate_path('/html/sub1/index.html', docs) ==
            target_root5 / 'html' / 'sub1' / 'index.html')
    assert (translate_path('/html/sub2/index.html', docs) ==
            target_root5 / 'html' / 'sub2' / 'index.html')
    assert (translate_path('/html/sub2/subsub2/index.html', docs) ==
            target_root5 / 'html' / 'sub2' / 'subsub2' / 'index.html')
    assert (translate_path('/html/sub3/index.html', docs) ==
            target_root5 / 'html' / 'sub3' / 'index.html')
