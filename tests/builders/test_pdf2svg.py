"""
Test the Pdf2svg builder
"""
import pytest

from disseminate.builders.pdf2svg import Pdf2svg
from disseminate.builders.pdfcrop import PdfCrop
from disseminate.paths import SourcePath, TargetPath


def test_pdf2svg(env):
    """Test the Pdf2svg builder."""
    # 1. Test example with the infilepath and outfilepath specified.
    infilepath = SourcePath(project_root='tests/builders/example1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample.svg')
    pdf2svg = Pdf2svg(infilepaths=infilepath, outfilepath=outfilepath, env=env)

    # Make sure pdfcrop is available and read
    assert pdf2svg.active
    assert pdf2svg.status == "ready"

    # Now run the build. Since this takes a bit of time, we'll catch the
    # command building
    assert not outfilepath.exists()
    status = pdf2svg.build(complete=True)
    assert status == 'done'
    assert pdf2svg.status == 'done'
    assert outfilepath.exists()

    # Make sure we created an svg
    assert '<?xml version="1.0" encoding="UTF-8"?>' in outfilepath.read_text()


def test_pdf2svg_pdfcrop(env):
    """Test the Pdf2svg builder with a PdfCrop subbuilder."""
    # 1. Test example with the infilepath and outfilepath specified.
    infilepath = SourcePath(project_root='tests/builders/example1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample.svg')
    pdf2svg = Pdf2svg(infilepaths=infilepath, outfilepath=outfilepath, env=env,
                      crop=20)

    # Make sure pdfcrop is available and read
    assert pdf2svg.active
    assert pdf2svg.status == "ready"

    # Make sure the pdfcrop builder was added as a subbuilder
    assert len(pdf2svg.subbuilders) == 1
    assert isinstance(pdf2svg.subbuilders[0], PdfCrop)

    # Now run the build. Since this takes a bit of time, we'll catch the
    # command building
    assert not outfilepath.exists()
    status = pdf2svg.build(complete=True)
    assert status == 'done'
    assert pdf2svg.status == 'done'
    assert outfilepath.exists()

    # Make sure the produced svg is cropped
    svg_text = outfilepath.read_text()
    assert 'width="65.5156pt" height="58.2628pt"' not in svg_text  # if not crop
    assert 'width="30.70147pt" height="29.60897pt"' in svg_text
