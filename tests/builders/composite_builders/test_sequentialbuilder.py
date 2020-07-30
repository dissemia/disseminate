"""
Test the SequentialBuilder
"""
import logging

from disseminate.builders.composite_builders import SequentialBuilder
from disseminate.builders.copy import Copy
from disseminate.builders.pdf2svg import Pdf2SvgCropScale
from disseminate.paths import SourcePath, TargetPath


def test_sequentialbuilder_empty(env):
    """Test a SequentialBuilder without subbuilders"""
    sequential_builder = SequentialBuilder(env)
    assert sequential_builder.status == 'done'  # no builders

    assert sequential_builder.build(complete=True) == 'done'


def test_sequentialbuilder_with_outfilepath(env):
    """Test a SequentialBuilder with the outfilepath specified"""
    # The default SequentialBuilder has only a copy builder
    # Create a test file
    src_filepath = env.context['src_filepath']

    # 1. Create a test builder with the outfilepath
    outfilepath = TargetPath(target_root=env.target_root, subpath='out.dm')
    builder = SequentialBuilder(env=env, parameters=src_filepath,
                                outfilepath=outfilepath)

    # Add a subbuilder
    cp_builder = Copy(env=env, parameters=src_filepath,
                      outfilepath=outfilepath)
    builder.subbuilders.append(cp_builder)

    # Check the build
    assert not builder.use_cache  # By default, do not use the cache directory
    assert builder.use_media  # By default, use the media directory
    assert builder.build_needed()  # The target file hasn't been created yet
    assert builder.infilepaths == [src_filepath]
    assert builder.outfilepath == outfilepath
    assert not outfilepath.exists()

    # Check the subbuilder
    assert len(builder.subbuilders) == 1
    copy_builder = builder.subbuilders[0]
    assert copy_builder.infilepaths == [src_filepath]
    assert copy_builder.outfilepath == outfilepath

    # Run the build
    assert builder.build(complete=True) == 'done'
    assert outfilepath.exists()


def test_sequentialbuilder_without_outfilepath(env):
    """Test a SequentialBuilder without the outfilepath specified"""
    # The default SequentialBuilder has only a copy builder
    # Create a test file
    src_filepath = env.context['src_filepath']

    # 1. Create a test builder without the outfilepath
    outfilepath = TargetPath(target_root=env.target_root, subpath='out.dm')
    builder = SequentialBuilder(env=env, parameters=src_filepath)

    # Add a subbuilder
    cp_builder = Copy(env=env, parameters=src_filepath,
                      outfilepath=outfilepath)
    builder.subbuilders.append(cp_builder)
    builder.chain_subbuilders()

    # Check the build
    assert not builder.use_cache  # By default, do not use the cache directory
    assert builder.use_media  # By default, use the media directory
    assert builder.build_needed()  # The target file hasn't been created yet
    assert builder.infilepaths == [src_filepath]
    assert (builder.outfilepath ==
            env.target_root / 'media' / 'test.dm')
    assert not outfilepath.exists()

    # Check the subbuilder
    assert len(builder.subbuilders) == 1
    copy_builder = builder.subbuilders[0]
    assert copy_builder.infilepaths == [src_filepath]
    assert (copy_builder.outfilepath ==
            env.target_root / 'media' / 'test.dm')

    # Run the build
    assert builder.build(complete=True) == 'done'
    assert builder.outfilepath.exists()


def test_sequentialbuilder_basic_decider(env, caplog, wait):
    """Test the SequentialBuilder with the basic Decider to test whether files
    exist."""
    # Track logging of DEBUG events
    caplog.set_level(logging.DEBUG)

    # We'll use the Pdf2SvgCropScale as an example of a SequentialBuilder
    assert issubclass(Pdf2SvgCropScale, SequentialBuilder)

    # 1. Test example with the infilepath and outfilepath specified that uses
    #    the PdfCrop and ScaleSvg subbuilders
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample.svg')
    parameters = [infilepath, ('crop', 100), ('scale', 2)]
    pdf2svg = Pdf2SvgCropScale(parameters=parameters, outfilepath=outfilepath,
                               env=env)

    assert not outfilepath.exists()  # target file not created yet

    # Run the build
    status = None
    while status != "done":
        status = pdf2svg.build()

    # Only 4 commands should have been run (pdfcrop, pdf2svg, rsvg-convert)
    # Filter logging messages for the build command
    assert len([r for r in caplog.records if 'PdfCrop' in r.msg]) == 1
    assert len([r for r in caplog.records if 'Pdf2svg' in r.msg]) == 1
    assert len([r for r in caplog.records if 'ScaleSvg' in r.msg]) == 1

    # Make sure the intermediate files, infilepaths and outfilepath are created
    for subbuilder in pdf2svg.subbuilders:
        assert subbuilder.status == 'done'
        assert all(i.exists() for i in subbuilder.infilepaths)
        assert subbuilder.outfilepath.exists()

    assert outfilepath.exists()
    mtime = outfilepath.stat().st_mtime

    # 2. Running the build again won't create a new outfilepath
    wait()  # a filesystem offset to make sure mtime can change.
    pdf2svg = Pdf2SvgCropScale(parameters=parameters, outfilepath=outfilepath,
                               env=env)
    assert pdf2svg.build(complete=True) == 'done'
    assert outfilepath.stat().st_mtime == mtime

    # The commands have only been run once since the build wasn't re-done
    assert len([r for r in caplog.records if 'PdfCrop' in r.msg]) == 1
    assert len([r for r in caplog.records if 'Pdf2svg' in r.msg]) == 1
    assert len([r for r in caplog.records if 'ScaleSvg' in r.msg]) == 1

    # If the intermediary files are deleted, the build needs to be redone
    pdf2svg = Pdf2SvgCropScale(parameters=parameters, outfilepath=outfilepath,
                               env=env)

    pdf2svg.subbuilders[0].outfilepath.unlink()  # PdfCrop
    pdf2svg.subbuilders[1].outfilepath.unlink()  # Pdf2svg
    pdf2svg.subbuilders[2].outfilepath.unlink()  # ScaleSvg

    assert pdf2svg.status == 'ready'
    assert pdf2svg.build(complete=True) == 'done'
    assert outfilepath.stat().st_mtime == mtime

    # The intermediary commands haven't been run again
    assert len([r for r in caplog.records if 'PdfCrop' in r.msg]) == 2
    assert len([r for r in caplog.records if 'Pdf2svg' in r.msg]) == 2
    assert len([r for r in caplog.records if 'ScaleSvg' in r.msg]) == 2

    # 3. Changing the output file will trigger a new build
    correct_contents = outfilepath.read_bytes()
    outfilepath.write_text('wrong!')

    pdf2svg = Pdf2SvgCropScale(parameters=parameters, outfilepath=outfilepath,
                               env=env)
    assert pdf2svg.build(complete=True) == 'done'
    assert outfilepath.read_bytes() == correct_contents

    # The intermediary files do not need to be re-build
    assert len([r for r in caplog.records if 'PdfCrop' in r.msg]) == 2
    assert len([r for r in caplog.records if 'Pdf2svg' in r.msg]) == 2
    assert len([r for r in caplog.records if 'ScaleSvg' in r.msg]) == 2


def test_sequentialbuilder_md5decider(env, caplog, wait):
    """Test the SequentialBuilder with the Md5Decider to test whether files
    change."""
    tmpdir = env.context['target_root']

    # Track logging of DEBUG events
    caplog.set_level(logging.DEBUG)

    # 1. Test example with an infilepath that is copied.
    infilepath = SourcePath(project_root=tmpdir, subpath='text.txt')
    outfilepath = TargetPath(target_root=tmpdir, subpath='copy.svg')
    infilepath.write_text('test 1')

    builder = SequentialBuilder(env=env, parameters=infilepath,
                                outfilepath=outfilepath)

    # Add a copy subbuilder
    builder.subbuilders.append(Copy(env=env))
    builder.chain_subbuilders()

    # Check the status of the builder before the build
    assert len(builder.subbuilders) == 1
    assert builder.status == 'ready'
    assert not outfilepath.is_file()

    # Run the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert outfilepath.is_file()
    assert outfilepath.read_text() == 'test 1'

    # Now modify the file
    infilepath.write_text('test 2')

    # Check the status of current builder--it has not change
    assert builder.status == 'done'

    # But a new builder will need a rebuild
    builder = SequentialBuilder(env=env, parameters=infilepath,
                                outfilepath=outfilepath)
    builder.subbuilders.append(Copy(env=env))
    builder.chain_subbuilders()

    # Check the status of the builder before the build
    assert len(builder.subbuilders) == 1
    assert builder.status == 'ready'

    # Run the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert outfilepath.is_file()
    assert outfilepath.read_text() == 'test 2'


def test_sequentialbuilder_change_status(env):
    """Test the SequentialBuilder build status when a subbuilder status
    changes."""
    # The default SequentialBuilder has only a copy builder
    # Create a test file
    src_filepath = env.context['src_filepath']

    # 1. Create sequential builder
    sequential_builder = SequentialBuilder(env=env, parameters=src_filepath)

    # Add a subbuilder
    outfilepath = TargetPath(target_root=env.target_root, subpath='out.dm')
    cp_builder = Copy(env=env, parameters=src_filepath,
                      outfilepath=outfilepath)
    sequential_builder.subbuilders.append(cp_builder)

    # Check the build
    assert sequential_builder.status == 'ready'
    assert sequential_builder.build(complete=True) == 'done'
    assert cp_builder.status == 'done'
    assert outfilepath.exists()

    # Nor reset the copy builder
    outfilepath.unlink()

    # The sequential and copy builders should be reset too
    assert cp_builder.status == 'ready'

    assert len(sequential_builder.subbuilders) == 0
    assert sequential_builder.status == 'done'
    assert sequential_builder.build(complete=True) == 'done'
