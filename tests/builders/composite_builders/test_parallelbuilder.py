"""
Tests for the ParallelBuilder
"""
import pytest

from disseminate.builders.composite_builders import ParallelBuilder
from disseminate.builders.exceptions import BuildError
from disseminate.paths import SourcePath, TargetPath


def test_parallelbuilder_find_builder_cls(tmpdir):
    """Test the ParallelBuilder find_buider_cls method."""

    # 1. Test html pdf->svg. Tracked deps: ['.css', '.svg', '.png'],
    infilepath = SourcePath(tmpdir, 'test.pdf')
    cls = ParallelBuilder.find_builder_cls(document_target='.html',
                                           infilepath=infilepath)
    assert cls.__name__ == 'Pdf2SvgCropScale'

    # 2. Test html svg
    infilepath = SourcePath(tmpdir, 'test.svg')
    cls = ParallelBuilder.find_builder_cls(document_target='.html',
                                           infilepath=infilepath)
    assert cls.__name__ == 'Copy'

    # 3. Test invalid extension
    infilepath = SourcePath(tmpdir, 'test.unknown')
    with pytest.raises(BuildError):
        ParallelBuilder.find_builder_cls(document_target='.html',
                                         infilepath=infilepath)

    # 4. Test an example with a specified outfilepath
    infilepath = SourcePath(tmpdir, 'test.pdf')
    outfilepath = TargetPath(tmpdir, subpath='test.svg')
    cls = ParallelBuilder.find_builder_cls(document_target='.html',
                                           infilepath=infilepath,
                                           outfilepath=outfilepath)
    assert cls.__name__ == 'Pdf2SvgCropScale'


def test_parallelbuilder_add_build(env):
    """Test the ParallelBuilder add_build method"""
    tmpdir = env.context['target_root']

    # Add paths to the context
    paths = [SourcePath(project_root='tests/builders/example1')]
    env.context['paths'] = paths

    # 1. Test html pdf->svg. Tracked deps: ['.css', '.svg', '.png'],
    infilepath = 'sample.pdf'
    outfilepath = TargetPath(target_root=tmpdir, target='html',
                             subpath='test.svg')
    parallel_builder = ParallelBuilder(env)
    build = parallel_builder.add_build(document_target='.html',
                                       infilepaths=infilepath,
                                       outfilepath=outfilepath)

    # Check the builder
    assert all(i.exists() for i in build.infilepaths)
    assert not outfilepath.exists()

    assert build.build_needed()
    assert parallel_builder.build_needed()

    # Now run the build
    assert parallel_builder.build(complete=True) == 'done'
    assert parallel_builder.status == 'done'
    assert outfilepath.exists()
