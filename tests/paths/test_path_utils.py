"""
Test path utilities
"""
import pathlib
from os import curdir

from disseminate.paths.utils import find_files
from disseminate.paths import SourcePath, TargetPath


def test_find_files_example1(doc):
    """Test the find_files function with the find_files_example1"""
    # tests/paths/find_files_example1/
    # └── sample.pdf
    context = doc.context

    # The source file should be found
    filepaths = find_files('test.dm', context)
    assert len(filepaths) == 1
    assert filepaths[0].name == 'test.dm'

    # Invalid files are not found
    filepaths = find_files('garbage331.py', context)
    assert len(filepaths) == 0

    # Try absolute paths
    img_path = (pathlib.Path(curdir) / 'tests' / 'paths' /
                'find_files_example1' / 'sample.pdf').absolute()
    filepaths = find_files(img_path, context)
    assert len(filepaths) == 1


def test_find_files_example2(doc_cls, tmpdir):
    """Test the find_files function with the find_files_example2"""
    # tests/paths/find_files_example2/
    # └── src
    #     ├── chapter1
    #     │   ├── figures
    #     │   │   └── local_img.png
    #     │   └── index.dm
    #     ├── index.dm
    #     └── media
    #         └── ch1
    #             └── root_img.png
    #
    # chapter1/index.dm includes local_img.png and root_img.png

    # Load the root document and subdocument
    project_root = 'tests/paths/find_files_example2/src'
    src_filepath = SourcePath(project_root=project_root, subpath='index.dm')
    target_root = TargetPath(target_root=tmpdir)

    doc = doc_cls(src_filepath=src_filepath, target_root=target_root)
    subdoc = doc.documents_list(only_subdocuments=True)[0]

    # Check the paths relative to the root document
    filepaths = find_files('media/ch1/root_img.png', doc.context)
    assert len(filepaths) == 1
    assert (filepaths[0].match('tests/paths/find_files_example2/src/'
                               'media/ch1/root_img.png'))

    filepaths = find_files('figures/local_img.png', doc.context)  # not found
    assert len(filepaths) == 0

    # Check the paths relative to the sub document
    filepaths = find_files('media/ch1/root_img.png', subdoc.context)
    assert len(filepaths) == 1
    assert (filepaths[0].match('tests/paths/find_files_example2/src/'
                               'media/ch1/root_img.png'))

    filepaths = find_files('figures/local_img.png', subdoc.context)
    assert len(filepaths) == 1
    assert (filepaths[0].match('tests/paths/find_files_example2/src/'
                               'chapter1/figures/local_img.png'))
