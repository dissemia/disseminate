"""
Test the Asy builder
"""
from disseminate.builders.asy import Asy2pdf
from disseminate.paths import SourcePath, TargetPath


def test_asy2pdf_file(env):
    """Test the Asy builder with an .asy file."""
    target_root = env.target_root

    # 1. Test example with the infilepath and outfilepath specified.
    infilepath = SourcePath(project_root='tests/builders/examples/ex7',
                            subpath='diagram.asy')
    outfilepath = TargetPath(target_root=target_root,
                             subpath='diagram.pdf')
    asy2pdf = Asy2pdf(infilepaths=infilepath, outfilepath=outfilepath, env=env)

    # Make sure pdfcrop is available and read
    assert asy2pdf.active
    assert asy2pdf.status == "ready"

    # Now run the build. Since this takes a bit of time, we'll catch the
    # command building
    assert not outfilepath.exists()
    status = asy2pdf.build(complete=True)
    assert status == 'done'
    assert asy2pdf.status == 'done'
    assert outfilepath.exists()
    assert isinstance(asy2pdf.infilepaths[0], SourcePath)
    assert isinstance(asy2pdf.outfilepath, TargetPath)

    # Make sure we created an svg
    assert b'%PDF' in outfilepath.read_bytes()

