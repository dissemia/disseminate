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
    """Test the Builder filepaths using a concreate builder (PdfCrop)"""

    # 1. Try an example without specifying infilepaths or outfilepath
    pdfcrop = PdfCrop(env=env)
    assert pdfcrop.infilepaths == []
    assert pdfcrop.outfilepath is None

    # 2. Try an example with specifying an infilepath. However, if it's not
    #    a SourcePath, it won't be used
    pdfcrop = PdfCrop(infilepaths='tests/builders/example1/sample.pdf', env=env)
    assert pdfcrop.infilepaths == []
    assert pdfcrop.outfilepath is None

    # 3. Try an example with specifying an infilepath. This time, use a
    #    SourcePath
    infilepath = SourcePath(project_root='tests/builders/example1',
                            subpath='sample.pdf')
    cachepath = SourcePath(project_root=env.cache_path,
                           subpath='sample_crop.pdf')
    pdfcrop= PdfCrop(infilepaths=infilepath, env=env)
    assert pdfcrop.infilepaths == [infilepath]
    assert pdfcrop.outfilepath == cachepath

    # 4. Try an example with specifying an outfilepath. However, if it's not
    #    a TargetPath, it won't be used. It this case
    targetpath = TargetPath(target_root=env.context['target_root'],
                            subpath='sample_crop.pdf')
    pdfcrop = PdfCrop(infilepaths=infilepath, outfilepath=str(targetpath),
                      env=env)
    assert pdfcrop.infilepaths == [infilepath]
    assert pdfcrop.outfilepath == cachepath

    # 4. Try an example with specifying an outfilepath. This time use a
    #    TargetPath
    targetpath = TargetPath(target_root=env.context['target_root'],
                            subpath='sample_crop.pdf')
    pdfcrop = PdfCrop(infilepaths=infilepath, outfilepath=targetpath,
                      env=env)
    assert pdfcrop.infilepaths == [infilepath]
    assert pdfcrop.outfilepath == targetpath


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
    assert builder.status == 'missing'

    # 2. Test an example in which the infilepath doesn't exist. The status
    #    should be missing
    builder = ExampleBuilder(env, infilepaths=infilepath,
                             outfilepath=outfilepath)
    assert builder.status == 'missing'

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
    builder = ExampleBuilder(env, infilepaths=infilepath,
                             outfilepath=outfilepath)
    assert not builder.build_needed()
    assert builder.status == 'done'


def test_builder_build(env):
    """Test the Builder build method"""

    infilepath = SourcePath(project_root='tests/builders/example1',
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

    subbuilder = SubBuilder(env=env, infilepaths=infilepath,
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

    cp = CopyCmd(env=env, infilepaths=infilepath, outfilepath=targetpath)

    # 1. Test a build that copies the file. It'll fail first because we haven't
    #    created the input file
    assert not infilepath.exists()
    assert not targetpath.exists()
    assert cp.build(complete=True) == 'missing'

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
    cp = CopyCmd(env=env, infilepaths=infilepath, outfilepath=targetpath)

    assert cp.build(complete=True) == 'done'
    assert targetpath.stat().st_mtime == mtime

    # 2. Try modifying the contents of the infile
    wait()
    infilepath.write_text('infile text2')
    cp = CopyCmd(env=env, infilepaths=infilepath, outfilepath=targetpath)

    assert cp.build(complete=True) == 'done'
    assert targetpath.stat().st_mtime > mtime
    assert targetpath.read_text() == 'infile text2'

    # 3. Try modifying the contents of the outfile. Now the outfile is newer
    #    than the infile, but its contents don't match the hash
    targetpath.write_text('outfile')

    cp = CopyCmd(env=env, infilepaths=infilepath, outfilepath=targetpath)

    assert cp.build(complete=True) == 'done'
    assert targetpath.read_text() == 'infile text2'
