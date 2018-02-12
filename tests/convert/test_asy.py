"""
Tests the asy converters
"""
import os.path

from disseminate.convert import convert


def test_asy2pdf(tmpdir):
    """Test the Asy2pdf converter."""
    # Setup the target file in a temp directory
    target_basefilepath = str(tmpdir.join('diagram'))

    # Load an asymptote file
    src_filepath = 'tests/convert/asy_example1/diagram.asy'
    target_filepath = convert(src_filepath=src_filepath,
                              target_basefilepath=target_basefilepath,
                              targets=['.pdf'])

    # See if the file was converted
    assert target_filepath == target_basefilepath + '.pdf'
    assert os.path.isfile(target_filepath)


def test_asy2svg(tmpdir):
    """Test the Asy2svg converter."""
    # Setup the target file in a temp directory
    target_basefilepath = str(tmpdir.join('diagram'))

    # Load an asymptote file
    src_filepath = 'tests/convert/asy_example1/diagram.asy'
    target_filepath = convert(src_filepath=src_filepath,
                              target_basefilepath=target_basefilepath,
                              targets=['.svg'])

    # See if the file was converted
    assert target_filepath == target_basefilepath + '.svg'
    assert os.path.isfile(target_filepath)
