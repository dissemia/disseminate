"""
Test the ScaleSvg builder
"""
import pytest

from disseminate.builders.pdf2svg import Pdf2svg
from disseminate.builders.scalesvg import ScaleSvg
from disseminate.paths import SourcePath, TargetPath


def test_scalesvg(env):
    """Test the ScaleSvg builder."""
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
    scalesvg = ScaleSvg(parameters=infilepath2,
                        outfilepath=outfilepath, scale=2, env=env)

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

    # Make sure we created a scaled svg
    assert 'width="164px" height="146px"' in outfilepath.read_text()

    # 2. Test an example without an outfilepath specified
    cache_path = env.cache_path / 'media' / 'sample_scale.svg'
    scalesvg = ScaleSvg(parameters=infilepath2, scale=2, env=env)

    assert scalesvg.status == "ready"
    assert not cache_path.exists()
    status = scalesvg.build(complete=True)
    assert status == 'done'
    assert scalesvg.status == 'done'
    assert cache_path.exists()
    assert cache_path.read_text() == outfilepath.read_text()

    # 3. Test an example with an invalid scale value
    with pytest.raises(ValueError):
        scalesvg = ScaleSvg(parameters=pdf2svg.outfilepath, scale='a', env=env)
