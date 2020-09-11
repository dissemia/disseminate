"""
Tests for the ParallelBuilder
"""
import logging
from collections import namedtuple

import pytest

from disseminate.builders.composite_builders import ParallelBuilder
from disseminate.builders.exceptions import BuildError
from disseminate.paths import SourcePath, TargetPath


def test_parallelbuilder_flatten(env):
    """Test the ParallelBuilder flatten method."""
    tmpdir = env.context['target_root']

    # Add paths to the context
    paths = [SourcePath(project_root='tests/builders/examples/ex1')]
    env.context['paths'] = paths

    # 1. Test a parallel builder for an html target.
    infilepath = 'sample.pdf'
    outfilepath = TargetPath(target_root=tmpdir, target='html',
                             subpath='test.svg')
    parallel_builder = ParallelBuilder(env, target='html')
    parallel_builder.add_build(parameters=infilepath, outfilepath=outfilepath)

    builds = parallel_builder.flatten()
    assert len(builds) == 4


def test_parallelbuilder_add_build_file_with_outfilepath(env):
    """Test the ParallelBuilder add_build method with an outfilepath
    specified"""
    tmpdir = env.context['target_root']
    target_root = tmpdir

    # Add paths to the context
    paths = [SourcePath(project_root='tests/builders/examples/ex1')]
    env.context['paths'] = paths

    # 1. Test a parallel builder for an html target.
    #    Test html pdf->svg. Tracked deps: ['.css', '.svg', '.png'],
    infilepath = 'sample.pdf'
    outfilepath = TargetPath(target_root=tmpdir, target='html',
                             subpath='test.svg')
    parallel_builder = ParallelBuilder(env, target='html')
    build = parallel_builder.add_build(parameters=infilepath,
                                       outfilepath=outfilepath)
    pdf2svg = parallel_builder.subbuilders[0]

    # Check the builder
    assert len(parallel_builder) == 3
    assert len(parallel_builder.subbuilders) == 1  # a Pdf2svgCropScale
    assert all(i.exists() for i in build.infilepaths)
    assert not outfilepath.exists()

    # Check that the SourcePath and TargetPath were properly formatted
    sp = SourcePath(project_root='tests/builders/examples/ex1',
                    subpath='sample.pdf')
    tp = TargetPath(target_root=target_root, target='html', subpath='test.svg')
    assert build.infilepaths[0] == sp
    assert build.infilepaths[0].subpath == sp.subpath
    assert build.outfilepath == tp
    assert build.outfilepath.subpath == tp.subpath

    assert build.build_needed()
    assert parallel_builder.build_needed()

    # Now run the build
    assert parallel_builder.build(complete=True) == 'done'

    # and make sure the build is complete
    assert parallel_builder.status == 'done'
    assert not parallel_builder.build_needed()
    assert outfilepath.exists()
    assert pdf2svg.status == 'done'

    # Try a new parallel builder, and its status should be 'done'--i.e. no
    # build is needed
    parallel_builder = ParallelBuilder(env, target='html')
    parallel_builder.add_build(parameters=infilepath, outfilepath=outfilepath)
    pdf2svg = parallel_builder.subbuilders[0]

    assert not parallel_builder.build_needed()
    assert parallel_builder.status == 'done'
    assert pdf2svg.status == 'done'


def test_parallelbuilder_add_build_file_without_outfilepath(env):
    """Test the ParallelBuilder add_build method without an outfilepath
    specified"""
    tmpdir = env.context['target_root']
    target_root = tmpdir

    # Add paths to the context
    paths = [SourcePath(project_root='tests/builders/examples/ex1')]
    infilepath = 'sample.pdf'
    env.context['paths'] = paths

    # 2. Test an example without an outfilepath. This should not be created in
    #    the cache directory since use_cache is False by default
    outfilepath = TargetPath(target_root=env.target_root, target='html',
                             subpath='media/sample.svg')
    parallel_builder = ParallelBuilder(env, target='html')
    parallel_builder.add_build(parameters=infilepath)

    assert parallel_builder.subbuilders[-1].outfilepath == outfilepath
    assert parallel_builder.build_needed()  # file doesn't exist

    # 3. Test an example with a new outfilepath. This build will be needed,
    infilepath = 'sample.pdf'
    outfilepath = TargetPath(target_root=tmpdir, target='html',
                             subpath='test2.svg')
    parallel_builder = ParallelBuilder(env, target='html')
    parallel_builder.add_build(parameters=infilepath, outfilepath=outfilepath)

    assert parallel_builder.build_needed()
    assert parallel_builder.status == 'ready'
    assert parallel_builder.build(complete=True) == 'done'
    assert parallel_builder.status == 'done'


def test_parallelbuilder_add_build_render(env):
    """Test the ParallelBuilder add_build method with render builder"""
    tmpdir = env.context['target_root']
    target_root = tmpdir

    # Add paths to the context
    paths = [SourcePath(project_root='tests/builders/examples/ex1')]
    env.context['paths'] = paths

    # Add the render fields into the context
    Tag = namedtuple('Tag', 'tex')
    env.context['body'] = Tag(tex='my body')

    # 1. Test a parallel builder with a Svgrender builder
    outfilepath = TargetPath(target_root=tmpdir, target='html',
                             subpath='test.svg')
    parallel_builder = ParallelBuilder(env, target='html')
    builder = parallel_builder.add_build(parameters='.render',
                                         outfilepath=outfilepath,
                                         context=env.context)

    assert parallel_builder.build_needed()
    assert builder.build_needed()

    # Run the build
    assert parallel_builder.build(complete=True) == 'done'
    assert not parallel_builder.build_needed()
    assert not builder.build_needed()

    # Make sure the the rendered file is created
    assert builder.outfilepath == outfilepath
    assert outfilepath.exists()
    assert '<svg' in outfilepath.read_text()


def test_parallelbuilder_add_build_missing(env):
    """Test the ParallelBuilder add_build method with missing file types"""
    tmpdir = env.context['target_root']

    # Add paths to the context
    paths = [SourcePath(project_root='tests/builders/examples/ex1')]
    env.context['paths'] = paths

    # 1. Test html pdf->unknown. The Pdf2svg converter will be returned
    infilepath = 'sample.pdf'
    outfilepath = TargetPath(target_root=tmpdir, target='html',
                             subpath='test.unknown')
    parallel_builder = ParallelBuilder(env, target='.html')

    # Add the subbuilder and and make sure it's of the correct type
    build = parallel_builder.add_build(parameters=infilepath,
                                       outfilepath=outfilepath)
    assert build.__class__.__name__ == 'Pdf2SvgCropScale'

    # 2. Test html unknown->pdf. This raises an error because a builder
    #    cannot be found.
    infilepath = 'sample.unknown'

    with pytest.raises(BuildError):
        parallel_builder.add_build(parameters=infilepath,
                                   outfilepath=outfilepath)


def test_parallelbuilder_add_build_multiple(env):
    """Test the ParallelBuilder add_build method with multiple sequential
    builds added."""
    tmpdir = env.context['target_root']

    # Add paths to the context
    paths = [SourcePath(project_root='tests/builders/examples/ex1')]
    env.context['paths'] = paths

    # 1. Test tex with adding a pdf file
    infilepath = 'sample.pdf'
    outfilepath1 = TargetPath(target_root=tmpdir, target='tex',
                              subpath='test1.pdf')
    parallel_builder = ParallelBuilder(env, target='.tex')

    # Add a subbbuilder
    build1 = parallel_builder.add_build(parameters=infilepath,
                                        outfilepath=outfilepath1)

    # Run the build
    assert parallel_builder.build(complete=True) == 'done'
    assert parallel_builder.status == 'done'
    assert build1.status == 'done'

    # Now add a second build
    outfilepath2 = TargetPath(target_root=tmpdir, target='tex',
                              subpath='test2.pdf')
    build2 = parallel_builder.add_build(parameters=infilepath,
                                        outfilepath=outfilepath2)

    # The parallel builder should now need to be rebuilt
    assert parallel_builder.status == 'ready'
    assert parallel_builder.build(complete=True) == 'done'
    assert parallel_builder.status == 'done'
    assert build2.status == 'done'


def test_parallelbuilder_empty(env):
    """Test the build of a parallel builder that is empty."""
    # 1. One with a document target specified
    parallel_builder = ParallelBuilder(env, target='html')
    assert parallel_builder.status == 'done'  # no builders
    assert parallel_builder.build(complete=True) == 'done'

    # 2. One without a document target specified
    parallel_builder = ParallelBuilder(env)
    assert parallel_builder.status == 'done'  # no builders
    assert parallel_builder.build(complete=True) == 'done'


def test_parallelbuilder_clear_done(env):
    """Test the clearing of done subbuilders with the parallelbuilder"""
    tmpdir = env.context['target_root']

    # Add paths to the context
    paths = [SourcePath(project_root='tests/builders/examples/ex1')]
    env.context['paths'] = paths

    # 1. Test a parallel builder for an html target.
    #    Test html pdf->svg. Tracked deps: ['.css', '.svg', '.png'],
    infilepath = 'sample.pdf'
    outfilepath = TargetPath(target_root=tmpdir, target='html',
                             subpath='test.svg')
    parallel_builder = ParallelBuilder(env, target='html')
    assert parallel_builder.clear_done
    assert len(parallel_builder.subbuilders) == 0

    # Now add a build
    parallel_builder.add_build(parameters=infilepath, outfilepath=outfilepath)
    assert len(parallel_builder.subbuilders) == 1

    # Now run the build. The subbuilder completes so it should be removed
    assert parallel_builder.build(complete=True) == 'done'
    assert len(parallel_builder.subbuilders) == 0


def test_parallelbuilder_sequential_builds(env):
    """Test the ParallelBuilder with 2 sequential builds"""
    tmpdir = env.context['target_root']

    # Add paths to the context
    paths = [SourcePath(project_root='tests/builders/examples/ex1')]
    env.context['paths'] = paths

    # 1. Test a parallel builder for an html target.
    #    Test html pdf->svg. Tracked deps: ['.css', '.svg', '.png'],
    infilepath = 'sample.pdf'
    outfilepath1 = TargetPath(target_root=tmpdir, target='html',
                              subpath='test1.svg')
    outfilepath2 = TargetPath(target_root=tmpdir, target='html',
                              subpath='test2.svg')
    parallel_builder = ParallelBuilder(env, target='html')
    parallel_builder.add_build(parameters=infilepath, outfilepath=outfilepath1)
    parallel_builder.add_build(parameters=infilepath, outfilepath=outfilepath2)

    # Test the builder
    assert not outfilepath1.exists()
    assert not outfilepath2.exists()
    assert len(parallel_builder.subbuilders) == 2
    assert (id(parallel_builder.subbuilders[0]) !=
            id(parallel_builder.subbuilders[1]))

    # Run the build
    assert parallel_builder.build_needed()
    assert parallel_builder.build(complete=True) == 'done'

    assert parallel_builder.status == 'done'
    assert not parallel_builder.build_needed()
    assert outfilepath1.exists()
    assert outfilepath2.exists()


def test_parallelbuilder_md5decider(env, caplog):
    """Test the ParallelBuilder with the Md5Decider."""
    tmpdir = env.context['target_root']

    # Track logging of DEBUG events
    caplog.set_level(logging.DEBUG)

    # Add paths to the context
    paths = [SourcePath(project_root='tests/builders/examples/ex1')]
    env.context['paths'] = paths

    # 1. Test a parallel builder for an html target.
    #    Test example with the infilepath and outfilepath specified that uses
    #    the PdfCrop and ScaleSvg subbuilders
    infilepath = 'sample.pdf'
    outfilepath = TargetPath(target_root=tmpdir, target='html',
                             subpath='test.svg')
    parallel_builder = ParallelBuilder(env, target='html')
    parallel_builder.add_build(parameters=infilepath, outfilepath=outfilepath)

    assert not outfilepath.exists()  # target file not created yet

    # Run the build
    assert parallel_builder.build_needed()
    status = None
    while status != "done":
        status = parallel_builder.build()
    assert not parallel_builder.build_needed()

    # The pdf2svg and copying commands should have only been run once
    assert len([r for r in caplog.records if 'pdf2svg' in r.msg]) == 1
    assert len([r for r in caplog.records if 'Copying' in r.msg]) == 1

    # If you run the build again, the pdf2svg command has not be run an
    # additional time
    assert parallel_builder.build(complete=True) == 'done'

    # The pdf2svg and copying commands should not have been run additionally.
    assert len([r for r in caplog.records if 'pdf2svg' in r.msg]) == 1
    assert len([r for r in caplog.records if 'Copying' in r.msg]) == 1

    # 2. Try modifying the outfilepath and a new build should be needed
    parallel_builder = ParallelBuilder(env, target='html')
    parallel_builder.add_build(parameters=infilepath, outfilepath=outfilepath)

    # Change the output file; a new build should be needed
    outfilepath.write_text('new output!')

    assert parallel_builder.build_needed()
    assert parallel_builder.build(complete=True) == 'done'

    # The cached version needs to be copied again, but not the pdf2svg command
    assert len([r for r in caplog.records if 'pdf2svg' in r.msg]) == 1
    assert len([r for r in caplog.records if 'Copying' in r.msg]) == 2

    # 3. Try modifying the cached versions and a full set of builds is needed.
    parallel_builder = ParallelBuilder(env, target='html')
    parallel_builder.add_build(parameters=infilepath, outfilepath=outfilepath)

    pdf2svg = parallel_builder.subbuilders[0]
    for subbuilder in pdf2svg.subbuilders:
        subbuilder.outfilepath.write_text('new output')

    assert parallel_builder.build_needed()
    assert parallel_builder.build(complete=True) == 'done'

    # The cached version needs to be copied again, but not the pdf2svg command
    assert len([r for r in caplog.records if 'pdf2svg' in r.msg]) == 2
    assert len([r for r in caplog.records if 'Copying' in r.msg]) == 3
