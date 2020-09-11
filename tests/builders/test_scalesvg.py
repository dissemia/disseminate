"""
Test the ScaleSvg builder
"""
import pytest

from disseminate.builders.pdf2svg import Pdf2svg
from disseminate.builders.scalesvg import ScaleSvg
from disseminate.paths import SourcePath, TargetPath


def test_scalesvg_build_with_outfilepath(env, svg_dims):
    """Test the ScaleSvg builder with the outfilepath specified."""

    # 1. Test example with the infilepath and outfilepath specified.
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample.svg')
    pdf2svg = Pdf2svg(parameters=infilepath, env=env)

    # Create the example svg
    assert pdf2svg.build(complete=True) == 'done'

    # Create the Scalesvg
    infilepath2 = pdf2svg.outfilepath
    scalesvg = ScaleSvg(parameters=[infilepath2, ('scale', 2)],
                        outfilepath=outfilepath, env=env)

    # Make sure scalesvg is available
    assert scalesvg.active
    assert scalesvg.status == "ready"

    # Now run the build. Since this takes a bit of time, we'll catch the
    # command building
    assert not outfilepath.exists()
    status = scalesvg.build(complete=True)
    assert status == 'done'
    assert scalesvg.status == 'done'
    assert outfilepath.exists()

    # Make sure the produced svg is scaled
    assert not svg_dims(outfilepath, width='82px', height='73px')
    assert svg_dims(outfilepath, width='164px', height='146px')


def test_scalesvg_build_without_outfilepath(env):
    """Test the ScaleSvg builder without the outfilepath specified."""

    # 2. Test an example without an outfilepath specified. The use_cache is
    #    False so the outfilepath will be stored in the target_root
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                           subpath='sample.pdf')
    pdf2svg = Pdf2svg(parameters=infilepath, env=env)

    # Create the example svg
    assert pdf2svg.build(complete=True) == 'done'

    # Create the Scalesvg
    infilepath2 = pdf2svg.outfilepath
    outfilepath = env.target_root / 'media' / 'sample_scale.svg'
    scalesvg = ScaleSvg(parameters=[infilepath2, ('scale', 2)], env=env)

    assert scalesvg.status == "ready"
    assert not outfilepath.exists()
    status = scalesvg.build(complete=True)
    assert status == 'done'
    assert scalesvg.status == 'done'
    assert outfilepath.exists()

    # 3. Test an example with an invalid scale value
    with pytest.raises(ValueError):  # no scale provided
        scalesvg = ScaleSvg(parameters=pdf2svg.outfilepath, env=env)

    with pytest.raises(ValueError):  # wrong type specified
        scalesvg = ScaleSvg(parameters=[pdf2svg.outfilepath, ('scale', 'a')],
                            env=env)
