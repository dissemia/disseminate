"""
Test the PdfCrop builder
"""
import pytest

from disseminate.builders.pdfcrop import PdfCrop
from disseminate.paths import SourcePath, TargetPath


def test_pdfcrop_build_missing_parameters(env):
    """Test the PdfCrop builder."""

    # 1. Test examples without the parameters specified.
    #    The builder should be available, but the status should be missing.
    #    The use_cache is False
    pdfcrop = PdfCrop(env=env)

    # Make sure pdfcrop is available and read
    assert pdfcrop.active
    assert pdfcrop.status == "missing (parameters)"


def test_pdfcrop_build_with_outfilepath(env):
    """Test the PdfCrop builder with the outfilepath specified."""

    # 2. Test example with the infilepath and outfilepath specified.
    #    The builder should be available, but the status should be missing
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample_crop.pdf')
    pdfcrop = PdfCrop(parameters=infilepath, outfilepath=outfilepath, env=env)

    # Make sure pdfcrop is available and read
    assert pdfcrop.active
    assert pdfcrop.status == "ready"

    # Now run the build. Since this takes a bit of time, we'll catch the
    # command building
    assert not outfilepath.exists()
    status = pdfcrop.build()
    assert status == 'building'
    assert pdfcrop.status == 'building'

    # Now run the command to completion
    status = pdfcrop.build(complete=True)
    assert pdfcrop.popen == "done"  # A new process hasn't been spawned
    assert status == 'done'
    assert pdfcrop.status == 'done'
    assert outfilepath.exists()


def test_pdfcrop_build_without_outfilepath(env):
    """Test the PdfCrop builder without the outfilepath specified."""

    # 3. Test an example without specifying the outfilepath. Since use_cache is
    #    False, it'll store it in the target_root directory.
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = env.target_root / 'media' / 'sample_crop.pdf'
    pdfcrop = PdfCrop(parameters=infilepath, env=env)

    # Make sure pdfcrop is available and read
    assert pdfcrop.active
    assert pdfcrop.status == "ready"
    assert pdfcrop.status == 'ready'

    # Now run the build.
    assert not outfilepath.exists()
    status = pdfcrop.build(complete=True)
    assert status == 'done'
    assert pdfcrop.status == 'done'
    assert outfilepath.exists()


def test_pdf_crop_percentage(env):
    """Test the PdfCrop builder with a specified crop_percentage."""
    # Create a reference build
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    ref_outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample_ref.pdf')
    pdfcrop = PdfCrop(parameters=infilepath, outfilepath=ref_outfilepath,
                      env=env)
    pdfcrop.build(complete=True)
    assert ref_outfilepath.exists()

    # 1. Test example with crop_percentage and 4 numbers
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample_crop.pdf')
    parameters = [infilepath, ('crop_percentage', (20, 20, 20, 20))]
    pdfcrop = PdfCrop(parameters=parameters, outfilepath=outfilepath, env=env)

    status = pdfcrop.build(complete=True)
    assert status == 'done'
    assert outfilepath.exists()

    # Make sure the cropped file is different from the reference
    assert ref_outfilepath.read_bytes() != outfilepath.read_bytes()

    # 2. Test example with crop_percentage and 1 number
    outfilepath2 = TargetPath(target_root=env.context['target_root'],
                              subpath='sample_crop2.pdf')
    pdfcrop = PdfCrop(parameters=[infilepath, ('crop', 20)],
                      outfilepath=outfilepath2, env=env)

    status = pdfcrop.build(complete=True)
    assert status == 'done'
    assert outfilepath2.exists()

    # Make sure the cropped file is different from the reference
    assert ref_outfilepath.read_bytes() != outfilepath2.read_bytes()

    # It should also be the same as test example 1
    assert outfilepath.read_bytes() == outfilepath2.read_bytes()

    # 3. Try an invalid crop number
    with pytest.raises(ValueError):
        parameters = [infilepath, ('crop_percentage', (20, 'a', 20, 20))]
        pdfcrop = PdfCrop(parameters=parameters, outfilepath=outfilepath,
                          env=env)
