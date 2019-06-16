"""
Test converters for pdf files
"""
from distutils.spawn import find_executable
from pathlib import Path

import pytest

from disseminate.convert import convert, ConverterError
from disseminate import SourcePath, TargetPath


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
    contents = correct_filepath.read_text()
    assert 'width="65.5156pt"' in contents
    assert 'height="58.2628pt"' in contents


def test_pdf2svg_optional(tmpdir):
    """Test the Pdf2svg converter with optional pdfcrop and rsvg-convert
    dependencies."""
    tmpdir = Path(tmpdir)

    # Get a test pdf file
    pdf_file = SourcePath("tests/convert/example1", "sample.pdf")

    # Setup a target_filepath
    target_basefilepath = TargetPath(target_root=tmpdir, target='.pdf',
                                     subpath='sample')

    # Try cropping
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=True, targets=['.svg'])

    # See if the file was created
    correct_filepath = TargetPath(target_root=tmpdir, target='.pdf',
                                  subpath='sample_crop.svg')
    assert target_filepath == correct_filepath
    assert correct_filepath.is_file()
    contents = correct_filepath.read_text()
    print('contents', contents)
    assert 'width="21.99794pt"' in contents
    assert 'height="22.4455pt"' in contents

    # Try cropping and scaling by a factor of 2
    target_filepath = convert(src_filepath=pdf_file,
                              target_basefilepath=target_basefilepath,
                              crop=True, scale='2.0', targets=['.svg'])

    # See if the file was created
    correct_filepath = TargetPath(target_root=tmpdir, target='.pdf',
                                  subpath='sample_crop_scale2.0.svg')
    assert target_filepath == correct_filepath
    assert correct_filepath.is_file()
    contents = correct_filepath.read_text()
    assert 'width="54pt"' in contents or 'width="54px"' in contents
    assert 'height="56pt"' in contents or 'height="56px"' in contents

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
    contents = correct_filepath.read_text()
    assert 'width="54pt"' in contents or 'width="54px"' in contents
    assert 'height="56pt"' in contents or 'height="56px"' in contents


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
