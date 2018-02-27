"""
Test converters for pdf files
"""
import os
from distutils.spawn import find_executable

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
    assert target_filepath == str(tmpdir.join('sample_crop_scale2.0.svg'))
    assert tmpdir.join('sample_crop_scale2.0.svg').check()
    contents = tmpdir.join('sample_crop_scale2.0.svg').read()
    assert 'width="60pt"' in contents
    assert 'height="60pt"' in contents

    # Try cropping and scaling by a factor of 2, but this time with a
    # spurious kwarg
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=True, scale='2.0', width='3.0',
                              targets=['.svg'])

    # See if the file was created
    assert target_filepath == str(tmpdir.join('sample_crop_scale2.0.svg'))
    assert tmpdir.join('sample_crop_scale2.0.svg').check()
    contents = tmpdir.join('sample_crop_scale2.0.svg').read()
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


def test_missing_executable(tmpdir, monkeypatch):
    """Test the behavior when the pdf to svg converters are missing."""
    # Remove the path from the environment
    monkeypatch.setenv("PATH", "")
    assert find_executable('pdf2svg') is None

    # Get a test pdf file
    pdf_file = "tests/convert/example1/sample.pdf"

    # Setup a target_filepath
    target_basefilepath = tmpdir.join('sample')

    # Try an unavailable: pdf->pdf
    with pytest.raises(ConverterError) as exc_info:
        target_filepath = convert(src_filepath=pdf_file,
                                  target_basefilepath=target_basefilepath,
                                  targets=['.svg'])

    # Check the exception message
    assert "required program" in exc_info.value.args[0]
    assert "pdf2svg" in exc_info.value.args[0]


def test_bad_pdflatex(tmpdir):
    """Tests the compilation of a PDF from a tex file with an error."""

    # Create a src document
    src_path = tmpdir.mkdir("src")
    target_basepath = tmpdir.join("index1")

    # Save text and create a new file
    f1 = src_path.join("index1.tex")
    f1.write("This is my \\bad{first} document")

    # Get the target_filepath for the pdf file
    target_filepath = str(src_path) + '/index1.pdf'

    # Render the document. This will raise a CompiledDocumentError
    with pytest.raises(ConverterError) as e:
        convert(src_filepath=str(f1),
                target_basefilepath=target_basepath,
                targets=['.pdf'])

    assert e.match("index1.tex")  # the intermediary file should be in error
    assert e.value.returncode != 0  # unsuccessful run

    assert "! Undefined control sequence." in e.value.shell_out
    assert "This is my \\bad" in e.value.shell_out