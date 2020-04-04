"""
Test the PdfCrop builder
"""
import pytest

from disseminate.builders.pdfcrop import PdfCrop
from disseminate.paths import SourcePath, TargetPath


def test_pdfcrop(env):
    """Test the PdfCrop builder."""

    # 1. Test examples without the infilepaths specified.
    #    The builder should be available, but the status should be missing
    pdfcrop = PdfCrop(env=env)

    # Make sure pdfcrop is available and read
    assert pdfcrop.active
    assert pdfcrop.status == "missing (infilepaths)"

    # 2. Test example with the infilepath and outfilepath specified.
    #    The builder should be available, but the status should be missing
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample_crop.pdf')
    pdfcrop = PdfCrop(infilepaths=infilepath, outfilepath=outfilepath, env=env)

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

    # 3. Test an example without specifying the outfilepath. This should
    #    automatically save it in a cache diretory from the environment
    cache_path = env.cache_path / 'sample_crop.pdf'
    pdfcrop = PdfCrop(infilepaths=infilepath, env=env)

    # Make sure pdfcrop is available and read
    assert pdfcrop.active
    assert pdfcrop.status == "ready"
    assert pdfcrop.status == 'ready'

    # Now run the build.
    assert not cache_path.exists()
    status = pdfcrop.build(complete=True)
    assert status == 'done'
    assert pdfcrop.status == 'done'
    assert cache_path.exists()


def test_pdf_crop_percentage(env):
    """Test the PdfCrop builder with a specified crop_percentage."""
    # Create a reference build
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    ref_outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample_ref.pdf')
    pdfcrop = PdfCrop(infilepaths=infilepath, outfilepath=ref_outfilepath,
                      env=env)
    pdfcrop.build(complete=True)
    assert ref_outfilepath.exists()

    # 1. Test example with crop_percentage and 4 numbers
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample_crop.pdf')
    pdfcrop = PdfCrop(infilepaths=infilepath, outfilepath=outfilepath, env=env,
                      crop_percentage=(20, 20, 20, 20))

    status = pdfcrop.build(complete=True)
    assert status == 'done'
    assert outfilepath.exists()

    # Make sure the cropped file is different from the reference
    assert ref_outfilepath.read_bytes() != outfilepath.read_bytes()

    # 2. Test example with crop_percentage and 1 number
    outfilepath2 = TargetPath(target_root=env.context['target_root'],
                              subpath='sample_crop2.pdf')
    pdfcrop = PdfCrop(infilepaths=infilepath, outfilepath=outfilepath2, env=env,
                      crop=20)

    status = pdfcrop.build(complete=True)
    assert status == 'done'
    assert outfilepath2.exists()

    # Make sure the cropped file is different from the reference
    assert ref_outfilepath.read_bytes() != outfilepath2.read_bytes()

    # It should also be the same as test example 1
    assert outfilepath.read_bytes() == outfilepath2.read_bytes()

    # 3. Try an invalid crop number
    with pytest.raises(ValueError):
        pdfcrop = PdfCrop(infilepaths=infilepath, outfilepath=outfilepath,
                          env=env, crop_percentage=(20, 'a', 20, 20))
