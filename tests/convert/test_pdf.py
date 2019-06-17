"""
Test converters for pdf files
"""
import re
import pathlib
from distutils.spawn import find_executable
from pathlib import Path

import pytest

from disseminate.convert import convert, ConverterError
from disseminate import SourcePath, TargetPath


def svg_dims(svg_filename):
    """Given and svg filename, return the width and height of the image."""
    # Load the svg file
    svg = pathlib.Path(svg_filename).read_text()

    # Find the width and height
    width = re.search(r'width\s*=\s*[\"\'](?P<value>[\d\.]+)', svg).group(1)
    height = re.search(r'height\s*=\s*[\"\'](?P<value>[\d\.]+)', svg).group(1)

    return float(width), float(height)


def test_pdf2svg(tmpdir):
    """Test the Pdf2svg converter."""
    tmpdir = Path(tmpdir)

    # Get a test pdf file
    pdf_file = SourcePath("tests/convert/example1/", "sample.pdf")

    # Setup a target_filepath
    target_basefilepath = TargetPath(target_root=tmpdir, target='.pdf',
                                     subpath='sample')

    # Try an unavailable: pdf->pdf
    with pytest.raises(ConverterError):
        target_filepath = convert(src_filepath=pdf_file,
                                  target_basefilepath=target_basefilepath,
                                  targets=['.pdf'])

    # Try a pdf->svg Run without crop and scale
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              targets=['.svg'])

    # See if the file was created
    correct_filepath = TargetPath(target_root=tmpdir, target='.pdf',
                                  subpath='sample.svg')
    assert target_filepath == correct_filepath
    assert correct_filepath.is_file()

    # Check the dimensions
    width, height = svg_dims(correct_filepath)
    assert width == 65.5156
    assert height == 58.2628


def test_pdf2svg_optional(tmpdir):
    """Test the Pdf2svg converter with optional pdfcrop and rsvg-convert
    dependencies."""
    tmpdir = Path(tmpdir)

    # Get a test pdf file
    pdf_file = SourcePath("tests/convert/example1", "sample.pdf")

    # Setup a target_filepath
    target_basefilepath = TargetPath(target_root=tmpdir, target='.pdf',
                                     subpath='sample')

    # Try cropping. This should shrink to the image from 65.5 x 58.2 pts to
    # a figure with dimensions smaller than 25 x 25 pts
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=True, targets=['.svg'])

    # See if the file was created
    correct_filepath = TargetPath(target_root=tmpdir, target='.pdf',
                                  subpath='sample_crop.svg')
    assert target_filepath == correct_filepath
    assert correct_filepath.is_file()

    # Check the dimensions
    width, height = svg_dims(correct_filepath)
    assert width < 25.
    assert height < 25.

    # Try cropping and scaling by a factor of 2
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=True, scale='2.0', targets=['.svg'])

    # See if the file was created
    correct_filepath = TargetPath(target_root=tmpdir, target='.pdf',
                                  subpath='sample_crop_scale2.0.svg')
    assert target_filepath == correct_filepath
    assert correct_filepath.is_file()

    # Check the dimensions
    width, height = svg_dims(correct_filepath)
    assert width == 54.
    assert height == 56.

    # Try cropping and scaling by a factor of 2, but this time with a
    # spurious kwarg
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=True, scale='2.0', width='3.0',
                              targets=['.svg'])

    # See if the file was created
    correct_filepath = TargetPath(target_root=tmpdir, target='.pdf',
                                  subpath='sample_crop_scale2.0.svg')
    assert target_filepath == correct_filepath
    assert correct_filepath.is_file()

    # Check the dimensions
    width, height = svg_dims(correct_filepath)
    assert width == 54.
    assert height == 56.


def test_pdf2svg_caching(tmpdir):
    """Test the caching of files"""
    tmpdir = Path(tmpdir)

    # Try convert the file again and see if it was updated

    # Get a test pdf file
    pdf_file = SourcePath(project_root="tests/convert/example1",
                          subpath="sample.pdf")

    # Setup a target_filepath
    target_basefilepath = TargetPath(target_root=tmpdir, target='.svg',
                                     subpath='sample')

    # Try the conversion
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=False, targets=['.svg'],
                              cache=False)

    # See if the file was created and get its mtime and ino
    correct_filepath = TargetPath(target_root=tmpdir, target='.svg',
                                  subpath='sample.svg')
    assert target_filepath == correct_filepath
    assert correct_filepath.is_file
    stats = target_filepath.stat()
    mtime = stats.st_mtime

    # Try the conversion again with caching
    new_target_filepath = convert(src_filepath=pdf_file,
                                  target_basefilepath=target_basefilepath,
                                  crop=False, targets=['.svg'],
                                  cache=True)

    # See if the file has changed
    assert target_filepath == new_target_filepath
    new_stats = new_target_filepath.stat()
    assert mtime == new_stats.st_mtime

    # Now try to get a new version
    new_target_filepath = convert(src_filepath=pdf_file,
                                  target_basefilepath=target_basefilepath,
                                  crop=False, targets=['.svg'],
                                  cache=False)

    # See if the file has changed
    assert new_target_filepath == target_filepath
    new_stats = target_filepath.stat()
    assert mtime != new_stats.st_mtime


def test_pdf2svg_missing_executable(tmpdir, monkeypatch):
    """Test the behavior when the pdf to svg converters are missing."""
    tmpdir = Path(tmpdir)

    # Remove the path from the environment
    monkeypatch.setenv("PATH", "")
    assert find_executable('pdf2svg') is None

    # Get a test pdf file
    pdf_file = SourcePath('tests/convert/example1', 'sample.pdf')

    # Setup a target_filepath
    target_basefilepath = TargetPath(target_root=tmpdir, target='.svg',
                                     subpath='sample')

    # Try an unavailable: pdf->pdf
    with pytest.raises(ConverterError) as exc_info:
        target_filepath = convert(src_filepath=pdf_file,
                                  target_basefilepath=target_basefilepath,
                                  targets=['.svg'])

    # Check the exception message
    assert "required program" in exc_info.value.args[0]
    assert "pdf2svg" in exc_info.value.args[0]
