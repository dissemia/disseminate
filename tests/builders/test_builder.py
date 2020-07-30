"""
Tests with the code Builder functionality
"""
import pytest

from disseminate.builders.builder import Builder
from disseminate.builders.pdfcrop import PdfCrop
from disseminate.paths import SourcePath, TargetPath


def test_builder_creation(env):
    """Test the creation of builders and ensure that they can take arbitrary
    arguments"""
    # The environment (env) is required
    with pytest.raises(TypeError):
        Builder()

    # Other options are allowed (but ignored)
    Builder(env, extra=1)


def test_builder_filepaths(env):
    """Test the Builder filepaths using a concrete builder (PdfCrop)"""

    # 1. Try an example without specifying parameters or outfilepath.
    pdfcrop = PdfCrop(env=env)
    assert pdfcrop.parameters == []
    assert (pdfcrop.outfilepath ==
            env.target_root / 'media' / 'd41d8cd98f00_crop.pdf')

    # 2. Try an example with specifying an infilepath but no outfilepath. By
    #    default, use_cache is False so the product is placed in the
    #     arget_root
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.target_root,
                           subpath='media/sample_crop.pdf')
    pdfcrop = PdfCrop(parameters=infilepath, env=env)
    assert pdfcrop.parameters == [infilepath]
    assert pdfcrop.outfilepath == outfilepath

    # 3. Try an example with specifying an infilepath but no outfilepath.
    #    This time, use a document target
    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    outfilepath = TargetPath(target_root=env.target_root,
                            target='html',
                            subpath='media/sample_crop.pdf')
    pdfcrop = PdfCrop(parameters=infilepath, target='html', env=env)
    assert pdfcrop.parameters == [infilepath]
    assert pdfcrop.outfilepath == outfilepath

    # 5. Try an example with specifying an outfilepath
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='sample_crop.pdf')
    pdfcrop = PdfCrop(parameters=infilepath, outfilepath=outfilepath,
                      env=env)
    assert pdfcrop.parameters == [infilepath]
    assert pdfcrop.outfilepath == outfilepath


def test_builder_get_parameter(env):
    """Test the Builder get_parameter method."""
    builder = Builder(env=env, parameters=[('test', 'value'), 1])

    assert builder.get_parameter('test') == 'value'
    assert builder.get_parameter(1) is None


def test_builder_status(env):
    """Test the Builder status property"""

    tmpdir = env.context['target_root']
    infilepath = SourcePath(project_root=tmpdir,
                            subpath='in.txt')
    outfilepath = TargetPath(target_root=env.context['target_root'],
                             subpath='out.txt')

    class ExampleBuilder(Builder):
        action = 'echo test'
        priority = 1000
        required_execs = tuple()

    # 1. Test an example without an infilepath. The status should be missing
    builder = ExampleBuilder(env)
    assert builder.status == 'missing (parameters)'

    # 2. Test an example in which the infilepath doesn't exist. The status
    #    should be missing
    builder = ExampleBuilder(env, parameters=infilepath,
                             outfilepath=outfilepath)
    assert builder.status == 'missing (parameters)'

    # 3. Test an example in which the infilepath now exists
    infilepath.write_text('infile')
    assert builder.status == 'ready'

    # 4. Now try a build
    assert builder.build() == 'building'

    # Create the outfilepath
    outfilepath.write_text('infile')
    assert builder.build() == 'done'
    assert builder.status == 'done'

    # 5. A new builder will report that it's done too.
    builder = ExampleBuilder(env, parameters=infilepath,
                             outfilepath=outfilepath)
    assert not builder.build_needed()
    assert builder.status == 'done'


def test_run_cmd_args(env):
    """Test the run_cmd_args method"""

    # 1. Test a basic example
    infilepath = SourcePath(project_root='', subpath='sample.pdf')
    targetpath = TargetPath(target_root='', subpath='out.pdf')
    builder = Builder(env=env, parameters=infilepath, outfilepath=targetpath)
    builder.action = ("My test with {builder.infilepaths} and "
                      "{builder.outfilepath}")
    assert builder.run_cmd_args() == ('My', 'test', 'with', 'sample.pdf', 'and',
                                      'out.pdf')

    # 2. Test an unsafe example with options and an unsafe option input as
    #    a filename
    infilepath = SourcePath(project_root='', subpath='-unsafe')
    targetpath = TargetPath(target_root='', subpath='out.pdf')
    builder = Builder(env=env, parameters=infilepath, outfilepath=targetpath)
    builder.action = ("test -safe {builder.parameters} and "
                      "-outputfile={builder.outfilepath}")
    assert builder.run_cmd_args() == ('test', '-safe', 'unsafe', 'and',
                                      '-outputfile=out.pdf')


def test_builder_build(env):
    """Test the Builder build method"""

    infilepath = SourcePath(project_root='tests/builders/examples/ex1',
                            subpath='sample.pdf')
    targetpath = TargetPath(target_root=env.context['target_root'],
                            subpath='sample_crop.pdf')

    # 1. Test a  subbuilder with a command run by build
    class SubBuilder(Builder):
        priority = 1000
        required_execs = tuple()
        was_run = False

        @property
        def status(self):
            return "done" if self.was_run else "ready"

        def build(self, complete=False):
            super().build(complete=complete)
            self.was_run = True
            return "done"

    subbuilder = SubBuilder(env=env, parameters=infilepath,
                            outfilepath=targetpath)

    # 1. Test a null build using the builder class should create a done build
    assert not subbuilder.was_run
    assert subbuilder.build() == 'done'
    assert subbuilder.build(complete=True) == 'done'
    assert subbuilder.was_run


def test_builder_md5decision(env, wait):
    """Test the Builder with the Md5Decision."""

    tmpdir = env.context['target_root']
    infilepath = SourcePath(project_root=tmpdir, subpath='in.txt')
    targetpath = TargetPath(target_root=tmpdir, subpath='out.txt')

    # 1. Test a  copy with a command run by build
    class CopyCmd(Builder):
        action = 'cp {builder.infilepaths} {builder.outfilepath}'
        priority = 1000
        required_execs = ('cp',)

    cp = CopyCmd(env=env, parameters=infilepath, outfilepath=targetpath)

    # 1. Test a build that copies the file. It'll fail first because we haven't
    #    created the input file
    assert not infilepath.exists()
    assert not targetpath.exists()
    assert cp.build(complete=True) == 'missing (parameters)'

    # Now create the input file
    infilepath.write_text('infile text')
    assert cp.status == 'ready'

    status = cp.build(complete=True)

    # Get details on the created output file
    assert targetpath.exists()
    assert infilepath.read_text() == targetpath.read_text()
    assert status == 'done'
    mtime = targetpath.stat().st_mtime

    # Try running the build again. The output file should not be modified
    cp = CopyCmd(env=env, parameters=infilepath, outfilepath=targetpath)

    assert cp.build(complete=True) == 'done'
    assert targetpath.stat().st_mtime == mtime

    # 2. Try modifying the contents of the infile
    wait()
    infilepath.write_text('infile text2')
    cp = CopyCmd(env=env, parameters=infilepath, outfilepath=targetpath)

    assert cp.build(complete=True) == 'done'
    assert targetpath.stat().st_mtime > mtime
    assert targetpath.read_text() == 'infile text2'

    # 3. Try modifying the contents of the outfile. Now the outfile is newer
    #    than the infile, but its contents don't match the hash
    targetpath.write_text('outfile')

    cp = CopyCmd(env=env, parameters=infilepath, outfilepath=targetpath)

    assert cp.build(complete=True) == 'done'
    assert targetpath.read_text() == 'infile text2'
