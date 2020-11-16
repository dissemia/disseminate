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


def test_pdf2svg_build_with_outfilepath(env, is_svg):
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
    assert is_svg(outfilepath)


def test_pdf2svg_pdfcrop_with_outfilepath(env, svg_dims):
    """Test the Pdf2svg builder with a PdfCrop subbuilder."""

    # 1. Test example with the infilepath and outfilepath specified.
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample.svg')
    pdf2svg = Pdf2SvgCropScale(parameters=[infilepath, ('crop', 20)],
                               outfilepath=outfilepath,env=env)

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

    # Check the parameters and outfilepath for the subbuilders
    assert pdfcrop.parameters == [infilepath, ('crop', 20)]
    assert pdfcrop.infilepaths == [infilepath]
    assert pdfcrop.outfilepath.match('*.pdf')
    assert pdfcrop.use_cache

    assert subpdf2svg.parameters == [pdfcrop.outfilepath, ('crop', 20)]
    assert subpdf2svg.infilepaths == [pdfcrop.outfilepath]
    assert subpdf2svg.outfilepath.match('*.svg')
    assert subpdf2svg.use_cache

    assert copy.parameters == [subpdf2svg.outfilepath, ('crop', 20)]
    assert copy.infilepaths == [subpdf2svg.outfilepath]
    assert copy.outfilepath == outfilepath
    assert not copy.use_cache

    # Check the parameters and outfilepath for the pdf2svg builder
    assert pdf2svg.parameters == [infilepath, ('crop', 20)]
    assert pdf2svg.infilepaths == [infilepath]
    assert pdf2svg.outfilepath == outfilepath
    assert not pdf2svg.use_cache

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
    assert not svg_dims(outfilepath, width='65.5pt', height='58.3pt', abs=1.0)
    assert svg_dims(outfilepath, width='30.7pt', height='30.0pt', abs=1.0)


def test_pdf2svg_pdfcrop_without_outfilepath(env, svg_dims):
    """Test the Pdf2svg builder with a PdfCrop subbuilder."""

    # 2. Test example without the outfilepath specified. Since use_cache is
    #    False, the product will be placed in the target root, but the
    #    intermediate files will not be
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = env.target_root / 'media' / 'sample.svg'
    pdf2svg = Pdf2SvgCropScale(parameters=[infilepath, ('crop', 20)],
                               env=env)
    assert not outfilepath.exists()
    assert not pdf2svg.use_cache

    # Check that the intermediate sub-builders use_caches
    pdfcrop = pdf2svg.subbuilders[0]
    assert pdfcrop.use_cache

    subpdf2svg = pdf2svg.subbuilders[1]
    assert subpdf2svg.use_cache

    copy = pdf2svg.subbuilders[2]
    assert not copy.use_cache

    status = pdf2svg.build(complete=True)
    assert status == 'done'

    # Make sure the produced svg is cropped
    assert not svg_dims(outfilepath, width='65.5pt', height='58.3pt', abs=1.0)
    assert svg_dims(outfilepath, width='30.7pt', height='30.0pt', abs=1.0)


def test_pdf2svg_scalesvg_with_outfilepath(env, svg_dims):
    """Test the Pdf2svg builder with a ScaleSvg subbuilder."""

    # 1. Test example with the infilepath and outfilepath specified.
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample.svg')
    pdf2svg = Pdf2SvgCropScale(parameters=[infilepath, ('scale', 2)],
                               outfilepath=outfilepath, env=env)

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
    assert subpdf2svg.use_cache
    assert subpdf2svg.parameters == [infilepath, ('scale', 2)]
    assert subpdf2svg.infilepaths == [infilepath]
    assert subpdf2svg.outfilepath.match('*.svg')

    assert scalesvg.use_cache
    assert scalesvg.parameters == [subpdf2svg.outfilepath, ('scale', 2)]
    assert scalesvg.infilepaths == [subpdf2svg.outfilepath]
    assert scalesvg.outfilepath.match('*.svg')

    assert not copy.use_cache
    assert copy.parameters == [scalesvg.outfilepath, ('scale', 2)]
    assert copy.infilepaths == [scalesvg.outfilepath]
    assert copy.outfilepath == outfilepath

    assert not pdf2svg.use_cache
    assert pdf2svg.parameters == [infilepath, ('scale', 2)]
    assert pdf2svg.infilepaths == [infilepath]
    assert pdf2svg.outfilepath == outfilepath

    # Check path types for the builders
    for builder in (scalesvg, subpdf2svg, copy, pdf2svg):
        assert all(isinstance(i, pathlib.Path) for i in builder.infilepaths)
        assert isinstance(builder.outfilepath, pathlib.Path)

    # Now run the build. Since this takes a bit of time, we'll catch the
    # command building
    assert not outfilepath.exists()
    status = pdf2svg.build(complete=True)
    assert status == 'done'
    assert pdf2svg.status == 'done'
    assert outfilepath.exists()

    # Make sure the produced svg is scaled
    assert not svg_dims(outfilepath, width='82', height='73', abs=1.0)
    assert svg_dims(outfilepath, width='164', height='146', abs=1.0)


def test_pdf2svg_scalesvg_without_outfilepath(env, svg_dims):
    """Test the Pdf2svg builder with a ScaleSvg subbuilder."""

    # 2. Test example without the outfilepath specified. The final file will
    #    be placed in a cached folder
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = env.target_root / 'media' / 'sample.svg'
    pdf2svg = Pdf2SvgCropScale(parameters=[infilepath, ('scale', 2)], env=env)

    assert not outfilepath.exists()
    assert not pdf2svg.use_cache

    # Check that the sub-builders use caches
    subpdf2svg = pdf2svg.subbuilders[0]
    assert subpdf2svg.use_cache

    scalesvg = pdf2svg.subbuilders[1]
    assert scalesvg.use_cache

    copy = pdf2svg.subbuilders[2]
    assert not copy.use_cache

    # Check the build and the product
    status = pdf2svg.build(complete=True)
    assert status == 'done'
    assert outfilepath.exists()

    # Make sure the produced svg is scaled
    assert not svg_dims(outfilepath, width='82', height='73', abs=1.0)
    assert svg_dims(outfilepath, width='164', height='146', abs=1.0)
