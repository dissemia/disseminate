"""
Test the Asy builder
"""
from disseminate.builders.asy_builders import Asy2pdf, Asy2svg
from disseminate.paths import SourcePath, TargetPath


def test_asy2pdf_setup(env):
    """Test the setup of the Asy2pdf builder."""
    target_root = env.context['target_root']
    context = env.context

    # 1. Setup a build with an outfilepath
    infilepath = SourcePath(project_root='tests/builders/examples/ex7',
                            subpath='diagram.asy')
    outfilepath = TargetPath(target_root=target_root,
                             subpath='final.svg')
    asy2pdf = Asy2pdf(env=env, infilepaths=infilepath, outfilepath=outfilepath)

    assert asy2pdf.infilepaths == [infilepath]
    assert asy2pdf.outfilepath == outfilepath


def test_asy2pdf_file(env):
    """Test the Asy2pdf builder with an .asy file."""
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


def test_asy2svg_file(env):
    """Test the Asy2svg builder with an .asy file."""
    target_root = env.target_root

    # 1. Test example with the infilepath and outfilepath specified.
    infilepath = SourcePath(project_root='tests/builders/examples/ex7',
                            subpath='diagram.asy')
    outfilepath = TargetPath(target_root=target_root,
                             subpath='diagram.svg')
    asy2svg = Asy2svg(infilepaths=infilepath, outfilepath=outfilepath, env=env)

    # Make sure pdfcrop is available and read
    assert asy2svg.active
    assert asy2svg.status == "ready"

    # Now run the build. Since this takes a bit of time, we'll catch the
    # command building
    assert not outfilepath.exists()
    status = asy2svg.build(complete=True)
    assert status == 'done'
    assert asy2svg.status == 'done'
    assert outfilepath.exists()
    assert isinstance(asy2svg.infilepaths[0], SourcePath)
    assert isinstance(asy2svg.outfilepath, TargetPath)

    # Make sure we created an svg
    assert '<svg' in outfilepath.read_text()
