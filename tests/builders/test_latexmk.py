"""
Test the Latexmk builder.
"""
from disseminate.builders.builder import Builder
from disseminate.builders.latexmk import Latexmk
from disseminate.paths import SourcePath, TargetPath


def reset_builder_cache():
    Builder._active.clear()
    Builder._available_builders.clear()


def test_latexmk_with_find_builder_cls():
    """Test the Latexmk builder access with the find_builder_cls."""

    try:
        default_state = Latexmk.available
        Latexmk.available = True
        reset_builder_cache()
        builder_cls = Latexmk.find_builder_cls(in_ext='.tex', out_ext='.pdf')
        assert builder_cls.__name__ == "Latexmk"
    finally:
        Latexmk.available = default_state
        reset_builder_cache()


def test_latexmk_find_builder_cls_backup():
    """Test the find_builder_cls method Pdflatex as a backup builders"""

    # Setup a test function
    def test_find(in_ext, out_ext, cls_name):
        builder_cls = Builder.find_builder_cls(in_ext=in_ext, out_ext=out_ext)
        assert builder_cls.__name__ == cls_name
        return builder_cls

    # 1. Test Latexmk > Pdflatex
    try:
        default_state = Latexmk.available
        Latexmk.available = True
        reset_builder_cache()

        test_find('.tex', '.pdf', 'Latexmk')
    finally:
        Latexmk.available = default_state
        reset_builder_cache()

    try:
        default_state = Latexmk.available
        Latexmk.available = False
        reset_builder_cache()

        test_find('.tex', '.pdf', 'Pdflatex')
    finally:
        Latexmk.available = default_state
        reset_builder_cache()


def test_latexmk_setup_no_outfilepath_use_media_use_cache(env):
    """Test the setup of the Latexmk builder with the use_media and use_cache
    options and no outfilepath specified."""

    infilepath = SourcePath(project_root='tests/builders/examples',
                            subpath='ex3/dummy.tex')
    latexmk = Latexmk(parameters=infilepath, env=env, use_cache=True,
                      use_media=True)

    assert str(latexmk.parameters[0].subpath) == 'ex3/dummy.tex'
    assert str(latexmk.outfilepath.subpath) == 'media/ex3/dummy.pdf'
    assert latexmk.outfilepath.target_root == env.cache_path


def test_latexmk_setup_no_outfilepath_use_cache(env):
    """Test the setup of the Latexmk builder with the use_cache option and no
     outfilepath specified."""

    infilepath = SourcePath(project_root='tests/builders/examples',
                            subpath='ex3/dummy.tex')
    latexmk = Latexmk(parameters=infilepath, env=env, use_cache=True,
                      use_media=False)

    assert str(latexmk.parameters[0].subpath) == 'ex3/dummy.tex'
    assert str(latexmk.outfilepath.subpath) == 'ex3/dummy.pdf'
    assert latexmk.outfilepath.target_root == env.cache_path


def test_latexmk_setup_outfilepath(env):
    """Test the setup of the Latexmk builder with outfilepath specified."""
    infilepath = SourcePath(project_root='tests/builders',
                            subpath='ex3/dummy.tex')
    outfilepath = TargetPath(target_root=env.target_root,
                             subpath='mytest.pdf')
    latexmk = Latexmk(parameters=infilepath, outfilepath=outfilepath,
                      env=env)

    assert latexmk.parameters[0] == infilepath
    assert latexmk.outfilepath == outfilepath


def test_latexmk_simple(env):
    """A simple build for Latexmk."""
    target_root = env.context['target_root']

    # 1. Test example with the infilepath specified.
    infilepath = SourcePath(project_root='tests/builders/examples',
                            subpath='ex3/dummy.tex')
    latexmk = Latexmk(parameters=infilepath, env=env)
    cache_path = latexmk.cache_path

    # Check the status of the build
    assert latexmk.status == 'ready'

    # Now run the build
    assert latexmk.build(complete=True) == 'done'

    # Check the state of the build
    assert latexmk.status == 'done'
    assert str(cache_path) in str(latexmk.outfilepath)
    assert latexmk.outfilepath.exists()

    # A new builder doesn't need to be run
    latexmk = Latexmk(parameters=infilepath, env=env)
    assert latexmk.status == 'done'

    # 2. Test example with the infilepath and outfilepath specified
    infilepath = SourcePath(project_root='tests/builders/examples',
                            subpath='ex3/dummy.tex')
    outfilepath = TargetPath(target_root=target_root,
                             subpath='myfile.pdf')
    latexmk = Latexmk(parameters=infilepath, outfilepath=outfilepath, env=env)

    # Check the status of the build
    assert latexmk.status == 'ready'
    assert not outfilepath.exists()

    # Now run the build
    assert latexmk.build(complete=True) == 'done'

    # Check the state of the build
    assert latexmk.status == 'done'
    assert latexmk.outfilepath.exists()

    # Check that the output file is a pdf
    assert b'%PDF' in latexmk.outfilepath.read_bytes()
