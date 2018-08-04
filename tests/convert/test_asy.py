"""
Tests the asy converters
"""
import pathlib

from disseminate import SourcePath, TargetPath
from disseminate.convert import convert


def test_asy2pdf(tmpdir):
    """Test the Asy2pdf converter."""
    tmpdir = pathlib.Path(tmpdir)

    # Setup the target file in a temp directory
    target_basefilepath = TargetPath(target_root=tmpdir,
                                     target='.pdf', subpath='diagram')

    # Load an asymptote file
    src_filepath = SourcePath(project_root='tests/convert/asy_example1',
                              subpath='diagram.asy')
    target_filepath = convert(src_filepath=src_filepath,
                              target_basefilepath=target_basefilepath,
                              targets=['.pdf'])

    # See if the file was converted
    correct_path = target_basefilepath.with_suffix('.pdf')
    assert target_filepath == correct_path
    assert target_filepath.is_file()


def test_asy2svg(tmpdir):
    """Test the Asy2svg converter."""
    tmpdir = pathlib.Path(tmpdir)

    # Setup the target file in a temp directory
    target_basefilepath = TargetPath(target_root=tmpdir,
                                     target='.asy',
                                     subpath='diagram')

    # Load an asymptote file
    src_filepath = SourcePath(project_root='tests/convert/asy_example1',
                              subpath='diagram.asy')
    target_filepath = convert(src_filepath=src_filepath,
                              target_basefilepath=target_basefilepath,
                              targets=['.svg'])

    # See if the file was converted
    correct_path = target_basefilepath.with_suffix('.svg')
    assert target_filepath == correct_path
    assert target_filepath.is_file()
