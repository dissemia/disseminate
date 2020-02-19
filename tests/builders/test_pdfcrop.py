"""
Test the PDFCrop builder
"""
import pathlib

from disseminate.builders.pdfcrop import PdfCrop
from disseminate.paths import SourcePath, TargetPath


def test_pdfcrop(env):
    """Test the PdfCrop builder."""

    # 1. Test examples without the infilepaths specified.
    #    The builder should be available, but the status should be missing
    pdfcrop = PdfCrop(env=env)

    # Make sure pdfcrop is available and read
    assert pdfcrop.active
    assert pdfcrop.status == "missing"

    # 2. Test examples with the infilepath and outfilepath specified.
    #    The builder should be available, but the status should be missing
    infilepath = SourcePath(project_root='tests/builders/example1',
                            subpath='sample.pdf')
    targetpath = TargetPath(target_root=env.context['target_root'],
                            subpath='sample_crop.pdf')
    pdfcrop = PdfCrop(infilepaths=infilepath, env=env)

    # Make sure pdfcrop is available and read
    assert pdfcrop.active
    assert pdfcrop.status == "ready"

    # Now run the build
    status = pdfcrop.build()
    assert status == 'ready'
    assert pdfcrop.status == 'ready'


    pdfcrop = PdfCrop(infilepaths=infilepath, outfilepath=targetpath,
                      env=env)
