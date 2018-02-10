"""
Test converters for pdf files
"""
import os

import pytest

from disseminate.convert import convert, ConverterError


def test_pdf2svg(tmpdir):
    """Test the Pdf2svg converter."""

    # Get a test pdf file
    pdf_file = "tests/convert/example1/sample.pdf"

    # Setup a target_filepath
    target_basefilepath = tmpdir.join('sample')

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
    assert target_filepath == str(tmpdir.join('sample.svg'))
    assert tmpdir.join('sample.svg').check()
    contents = tmpdir.join('sample.svg').read()
    assert 'width="65.5156pt"' in contents
    assert 'height="58.2628pt"' in contents


@pytest.mark.optional
def test_pdf2svg_optional(tmpdir):
    """Test the Pdf2svg converter with optional pdfcrop and rsvg-convert
    dependencies."""

    # Get a test pdf file
    pdf_file = "tests/convert/example1/sample.pdf"

    # Setup a target_filepath
    target_basefilepath = tmpdir.join('sample')

    # Try cropping
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=True, targets=['.svg'])

    # See if the file was created
    assert target_filepath == str(tmpdir.join('sample_crop.svg'))
    assert tmpdir.join('sample_crop.svg').check()
    contents = tmpdir.join('sample_crop.svg').read()
    assert 'width="24pt"' in contents
    assert 'height="24pt"' in contents

    # Try cropping and scaling by a factor of 2
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=True, scale='2.0', targets=['.svg'])

    # See if the file was created
    assert target_filepath == str(tmpdir.join('sample_crop_scale2.svg'))
    assert tmpdir.join('sample_crop_scale2.svg').check()
    contents = tmpdir.join('sample_crop_scale2.svg').read()
    assert 'width="60pt"' in contents
    assert 'height="60pt"' in contents


def test_caching(tmpdir):
    """Test the caching of files"""
    # Try convert the file again and see if it was updated

    # Get a test pdf file
    pdf_file = "tests/convert/example1/sample.pdf"

    # Setup a target_filepath
    target_basefilepath = tmpdir.join('sample')

    # Try the conversion
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=False, targets=['.svg'],
                              cache=False)

    # See if the file was created and get its mtime and ino
    stats = os.stat(tmpdir.join('sample.svg'))
    mtime = stats.st_mtime
    assert target_filepath == str(tmpdir.join('sample.svg'))
    assert tmpdir.join('sample.svg').check()

    # Try the conversion again with caching
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=False, targets=['.svg'],
                              cache=True)

    # See if the file has changed
    new_stats = os.stat(tmpdir.join('sample.svg'))
    assert mtime == new_stats.st_mtime

    # Now try to get a new version
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=False, targets=['.svg'],
                              cache=False)

    # See if the file has changed
    new_stats = os.stat(tmpdir.join('sample.svg'))
    assert mtime != new_stats.st_mtime
