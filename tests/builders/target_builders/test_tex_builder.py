"""
Test the TexBuilder
"""
import pathlib

from disseminate.builders.target_builders.tex_builder import TexBuilder
from disseminate.paths import TargetPath


def test_tex_builder_setup(setup_example):
    """Test the setup of the TexBuilder"""
    # 1. example 1: tests/builders/target_builders/example1
    env, doc = setup_example('tests/builders/target_builders/example1',
                             'dummy.dm')

    # Setup the builder
    builder = TexBuilder(env, document=doc)

    # Check the infilepaths. These should be SourcePaths with correctly set
    # project_root / subpath
    assert len(builder.infilepaths) == 1
    assert builder.infilepaths[0].match('dummy.dm')
    assert (str(builder.infilepaths[0].subpath) ==
            'dummy.dm')
    assert builder.outfilepath.match('tex/dummy.tex')
    assert str(builder.outfilepath.subpath) == 'dummy.tex'


def test_tex_builder_simple(setup_example):
    """Test a simple build with the TexBuilder."""
    # 1. example 1: tests/builders/target_builders/example1
    env, doc = setup_example('tests/builders/target_builders/example1',
                             'dummy.dm')

    # Setup the builder
    builder = TexBuilder(env, document=doc)

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not doc.targets['.tex'].exists()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert doc.targets['.tex'].exists()

    # Check the answer key
    key = pathlib.Path('tests/builders/target_builders/example1/dummy.tex')
    assert doc.targets['.tex'].read_text() == key.read_text()

    # New builders don't need to rebuild.
    builder = TexBuilder(env, document=doc)
    assert builder.status == 'done'


def test_tex_builder_inherited(setup_example):
    """Test a build with the TexBuilder using an inherited template."""
    # 1. example 1: tests/builders/target_builders/example1
    env, doc = setup_example('tests/builders/target_builders/example2',
                             'dummy.dm')

    # Setup the builder
    builder = TexBuilder(env, document=doc)

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not doc.targets['.tex'].exists()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert doc.targets['.tex'].exists()
    print(doc.targets['.tex'])
    # Check the answer key
    key = pathlib.Path('tests/builders/target_builders/example2/dummy.tex')
    assert doc.targets['.tex'].read_text() == key.read_text()

    # New builders don't need to rebuild.
    builder = TexBuilder(env, document=doc)
    assert builder.status == 'done'
