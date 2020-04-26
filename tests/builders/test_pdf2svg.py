"""
Test the Pdf2svg builder
"""
import pathlib

from disseminate.builders.pdf2svg import Pdf2svg, Pdf2SvgCropScale
from disseminate.builders.pdfcrop import PdfCrop
from disseminate.builders.scalesvg import ScaleSvg
from disseminate.builders.copy import Copy
from disseminate.paths import SourcePath, TargetPath


def test_pdf2svg_with_find_builder_cls():
    """Test the Pdf2SvgCropScale builder access with the find_builder_cls."""

    builder_cls = Pdf2SvgCropScale.find_builder_cls(in_ext='.pdf',
                                                    out_ext='.svg')
    assert builder_cls.__name__ == "Pdf2SvgCropScale"


def test_pdf2svg(env):
    """Test the Pdf2svg builder."""
    # 1. Test example with the infilepath and outfilepath specified.
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample.svg')
    pdf2svg = Pdf2svg(parameters=infilepath, outfilepath=outfilepath, env=env)

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
    assert isinstance(pdf2svg.parameters[0], SourcePath)
    assert isinstance(pdf2svg.outfilepath, TargetPath)

    # Make sure we created an svg
    assert '<?xml version="1.0" encoding="UTF-8"?>' in outfilepath.read_text()


def test_pdf2svg_pdfcrop(env):
    """Test the Pdf2svg builder with a PdfCrop subbuilder."""
    # 1. Test example with the infilepath and outfilepath specified.
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample.svg')
    pdf2svg = Pdf2SvgCropScale(parameters=infilepath, outfilepath=outfilepath,
                               env=env, crop=20)

    # Make sure pdfcrop is available and read
    assert pdf2svg.active
    assert pdf2svg.status == "ready"

    # Make sure the pdfcrop builder was added as a subbuilder
    assert len(pdf2svg.subbuilders) == 3
    assert isinstance(pdf2svg.subbuilders[0], PdfCrop)
    assert isinstance(pdf2svg.subbuilders[1], Pdf2svg)
    assert isinstance(pdf2svg.subbuilders[2], Copy)
    pdfcrop = pdf2svg.subbuilders[0]
    subpdf2svg = pdf2svg.subbuilders[1]
    copy = pdf2svg.subbuilders[2]

    # Check the parameters and outfilepath
    assert pdfcrop.parameters == [infilepath]
    assert pdfcrop.outfilepath.match('*.pdf')
    assert subpdf2svg.parameters == [pdfcrop.outfilepath]
    assert subpdf2svg.outfilepath.match('*.svg')
    assert copy.parameters == [subpdf2svg.outfilepath]
    assert copy.outfilepath == outfilepath

    assert pdf2svg.parameters == [infilepath]
    assert pdf2svg.outfilepath == outfilepath

    # Check path types for the builders
    for builder in (pdfcrop, subpdf2svg, copy, pdf2svg):
        assert all(isinstance(i, pathlib.Path) for i in builder.infilepaths)
        assert isinstance(builder.outfilepath, pathlib.Path)

    # Now run the build
    assert not outfilepath.exists()
    status = pdf2svg.build(complete=True)
    assert status == 'done'
    assert pdf2svg.status == 'done'
    assert outfilepath.exists()

    # Make sure the produced svg is cropped
    svg_text = outfilepath.read_text()
    assert 'width="65.5156pt" height="58.2628pt"' not in svg_text  # if not crop
    assert 'width="30.70147pt" height="29.60897pt"' in svg_text

    # 2. Test example without the outfilepath specified. The final final will
    #    be placed in a cached folder
    cache_path = env.cache_path / 'media/sample.svg'
    pdf2svg = Pdf2SvgCropScale(parameters=infilepath, env=env, crop=20)
    assert not cache_path.exists()

    status = pdf2svg.build(complete=True)
    assert status == 'done'
    assert pdf2svg.outfilepath.exists()
    assert pdf2svg.outfilepath.read_text() == svg_text


def test_pdf2svg_scalesvg(env):
    """Test the Pdf2svg builder with a ScaleSvg subbuilder."""
    # 1. Test example with the infilepath and outfilepath specified.
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample.svg')
    pdf2svg = Pdf2SvgCropScale(parameters=infilepath, outfilepath=outfilepath,
                               env=env, scale=2)

    # Make sure pdfcrop is available and read
    assert pdf2svg.active
    assert pdf2svg.status == "ready"

    # Make sure the pdfcrop builder was added as a subbuilder
    assert len(pdf2svg.subbuilders) == 3
    assert isinstance(pdf2svg.subbuilders[0], Pdf2svg)
    assert isinstance(pdf2svg.subbuilders[1], ScaleSvg)
    assert isinstance(pdf2svg.subbuilders[2], Copy)
    subpdf2svg = pdf2svg.subbuilders[0]
    scalesvg = pdf2svg.subbuilders[1]
    copy = pdf2svg.subbuilders[2]

    # Check the parameters and outfilepath
    assert subpdf2svg.parameters == [infilepath]
    assert subpdf2svg.outfilepath.match('*.svg')
    assert scalesvg.parameters == [subpdf2svg.outfilepath]
    assert scalesvg.outfilepath.match('*.svg')
    assert copy.parameters == [scalesvg.outfilepath]
    assert copy.outfilepath == outfilepath
    assert pdf2svg.parameters == [infilepath]
    assert pdf2svg.outfilepath == outfilepath

    # Check path types for the builders
    for builder in (scalesvg, subpdf2svg, copy, pdf2svg):
        assert all(isinstance(i, pathlib.Path) for i in builder.parameters)
        assert isinstance(builder.outfilepath, pathlib.Path)

    # Now run the build. Since this takes a bit of time, we'll catch the
    # command building
    assert not outfilepath.exists()
    status = pdf2svg.build(complete=True)
    assert status == 'done'
    assert pdf2svg.status == 'done'
    assert outfilepath.exists()

    # Make sure the produced svg is cropped
    svg_text = outfilepath.read_text()
    assert 'width="82px" height="73px"' not in svg_text  # if not crop
    assert 'width="164px" height="146px"' in svg_text

    # Remove all intermediary files
    for builder in [subpdf2svg, scalesvg]:
        builder.outfilepath.unlink()

    # 2. Test example without the outfilepath specified. The final file will
    #    be placed in a cached folder
    cache_path = env.cache_path / 'media/sample.svg'
    pdf2svg = Pdf2SvgCropScale(parameters=infilepath, env=env, scale=2)

    assert not cache_path.exists()
    status = pdf2svg.build(complete=True)
    assert status == 'done'
    assert cache_path.exists()
    assert cache_path.read_text() == svg_text
