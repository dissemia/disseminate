"""
Tests with the code Builder functionality
"""
from disseminate.builders.builder import Builder
from disseminate.builders.pdfcrop import PdfCrop
from disseminate.paths import SourcePath, TargetPath


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

        def build(self, complete=False):
            super().build(complete=complete)

            self.was_run = True

            self.status = 'done'
            return self.status

    subbuilder = SubBuilder(env=env, infilepaths=infilepath,
                            outfilepath=targetpath)

    # 1. Test a null build using the builder class should create a done build
    assert not subbuilder.was_run
    assert subbuilder.build() == 'done'
    assert subbuilder.build(complete=True) == 'done'
    assert subbuilder.was_run
