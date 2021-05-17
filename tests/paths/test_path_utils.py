"""
Test path utilities
"""
import pathlib
from os import curdir

import pytest

from disseminate.paths.utils import find_files, find_file
from disseminate.paths import SourcePath


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

    # Try absolute paths (existing file)
    img_path = (pathlib.Path(curdir) / 'tests' / 'paths' /
                'find_files_example1' / 'sample.pdf').absolute()
    filepaths = find_files(img_path, context)
    assert len(filepaths) == 1

    # Try absolute paths (non-exisistent file)
    img_path = (pathlib.Path(curdir) / 'tests' / 'paths' /
                'find_files_example1' / 'missing.pdf').absolute()
    filepaths = find_files(img_path, context)
    assert len(filepaths) == 0


def test_find_files_example2(doc_cls, env, tmpdir):
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
    env.project_root = SourcePath(project_root='tests/paths/'
                                               'find_files_example2/src')
    src_filepath = SourcePath(project_root=env.project_root,
                              subpath='index.dm')

    doc = doc_cls(src_filepath=src_filepath, environment=env)
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


def test_find_file(context_cls):
    """Test the find_file function."""

    # 1. Test the find_files_example2
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

    # 1. Test with simple strings
    paths = ['tests/paths/find_files_example2/src',
             'tests/paths/find_files_example2/src/chapter1',
             'tests/paths/find_files_example2/src/chapter1/figures']
    context = context_cls(paths=paths)

    assert find_file('local_img.png', context).match('local_img.png')
    assert find_file('figures/local_img.png', context).match('local_img.png')
    assert find_file('media/ch1/root_img.png', context).match('root_img.png')

    # Try a missing file
    with pytest.raises(FileNotFoundError):
        find_file('ch1/root_img.png', context)

    # 2. Test with SourcePath strings
    paths = [SourcePath('tests/paths/find_files_example2/src'),
             SourcePath('tests/paths/find_files_example2/src', 'chapter1'),
             SourcePath('tests/paths/find_files_example2/src',
                        'chapter1/figures')]
    context = context_cls(paths=paths)
    p1 = find_file('local_img.png', context)
    assert p1.match('figures/local_img.png')
    assert isinstance(p1, SourcePath)
    assert str(p1.subpath) == 'chapter1/figures/local_img.png'

    p2 = find_file('figures/local_img.png', context)
    assert p2.match('figures/local_img.png')
    assert isinstance(p2, SourcePath)
    assert str(p2.subpath) == 'chapter1/figures/local_img.png'

    p3 = find_file('media/ch1/root_img.png', context)
    assert p3.match('media/ch1/root_img.png')
    assert isinstance(p3, SourcePath)
    assert str(p3.subpath) == 'media/ch1/root_img.png'

    # 3. Test an example with an invalid type
    with pytest.raises(FileNotFoundError):
        find_file(['invalid'], context)


def test_find_file_missing(context_cls):
    """Test the find_file function when files are missing."""
    context = context_cls(paths=[])

    # Test different sstring
    for string in ('',  # empty string
                   "one\ntwo  \n",  # multiline string
                   ):
        with pytest.raises(FileNotFoundError):
            find_file(string, context)
