"""
Test the TexBuilder
"""
import pathlib
from collections import namedtuple

from disseminate.builders.target_builders.tex_builder import TexBuilder
from disseminate.paths import SourcePath, TargetPath


def test_tex_builder_setup_in_targets(env):
    """Test the setup of a TexBuilder when 'tex' is listed as a target
    in the context['targets']"""
    context = env.context
    src_filepath = context['src_filepath']
    target_root = context['target_root']

    # 1. Setup the builder without an outfilepath.  In this case, 'tex' is
    #    listed in the targets, so the outfilepath will *not* be in the
    #    cache directory
    context['targets'] |= {'tex'}
    target_filepath = TargetPath(target_root=target_root, target='tex',
                                 subpath='test.tex')
    builder = TexBuilder(env, context=context)

    # check the build
    assert context['builders']['.tex'] == builder  # builder in context
    assert not target_filepath.exists()
    assert len(builder.subbuilders) == 2

    assert builder.subbuilders[0].__class__.__name__ == 'ParallelBuilder'
    assert builder.subbuilders[0].infilepaths == []
    assert builder.subbuilders[1].__class__.__name__ == 'JinjaRender'
    assert len(builder.subbuilders[1].infilepaths) > 0
    assert builder.subbuilders[1].outfilepath == target_filepath
    assert builder.infilepaths == [src_filepath]
    assert builder.outfilepath == target_filepath

    assert builder.build_needed()
    assert builder.status == 'ready'

    # 2. Setup the builder with an outfilepath
    target_filepath = TargetPath(target_root=target_root, target='other',
                                 subpath='final.tex')
    builder = TexBuilder(env, context=context, outfilepath=target_filepath)

    # check the build
    assert not target_filepath.exists()
    assert len(builder.subbuilders) == 2

    assert builder.subbuilders[0].__class__.__name__ == 'ParallelBuilder'
    assert builder.subbuilders[0].infilepaths == []
    assert builder.subbuilders[1].__class__.__name__ == 'JinjaRender'
    assert len(builder.subbuilders[1].infilepaths) > 0
    assert builder.infilepaths == [src_filepath]
    assert builder.outfilepath == target_filepath

    assert builder.build_needed()
    assert builder.status == 'ready'


def test_tex_builder_setup_not_in_targets(env):
    """Test the setup of a TexBuilder when 'tex' is not listed as a target
    in the context['targets']"""
    context = env.context
    src_filepath = context['src_filepath']
    target_root = context['target_root']

    # 1. Setup the builder without an outfilepath.  In this case, 'tex' is *not*
    #    listed in the targets, so the outfilepath will be in the
    #    cache directory
    context['targets'] -= {'tex'}
    target_filepath = TargetPath(target_root=target_root / '.cache',
                                 target='tex', subpath='test.tex')
    builder = TexBuilder(env, context=context)

    # check the build
    assert context['builders']['.tex'] == builder  # builder in context
    assert not target_filepath.exists()
    assert len(builder.subbuilders) == 2

    assert builder.subbuilders[0].__class__.__name__ == 'ParallelBuilder'
    assert builder.subbuilders[0].infilepaths == []
    assert builder.subbuilders[1].__class__.__name__ == 'JinjaRender'
    assert len(builder.subbuilders[1].infilepaths) > 0
    assert builder.infilepaths == [src_filepath]
    assert builder.outfilepath == target_filepath

    assert builder.build_needed()
    assert builder.status == 'ready'


def test_tex_builder_simple(env):
    """Test a simple build with the TexBuilder """
    context = env.context
    tmpdir = context['target_root']

    # 1. Setup the builder. At least an outfilepath is needed and a content
    #    is needed
    target_filepath = TargetPath(target_root=tmpdir, target='tex',
                                 subpath='test.tex')
    tag = namedtuple('tag', 'tex')
    context['body'] = tag(tex="My body")  # expects {{ body.tex }}

    builder = TexBuilder(env, context=context, outfilepath=target_filepath)

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not target_filepath.exists()

    # Rechaining the build should change the builder
    builder.chain_subbuilders()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert target_filepath.exists()

    # Check the answer key
    assert 'My body' in target_filepath.read_text()

    # Check the copied files (if there are any)

    # New builders don't need to rebuild.
    builder = TexBuilder(env, context=context, outfilepath=target_filepath)
    assert builder.status == 'done'


def test_tex_builder_simple_doc(load_example):
    """Test a simple build with the TexBuilder."""
    # 1. example 1: tests/builders/examples/ex3
    doc = load_example('tests/builders/examples/ex3/dummy.dm')
    env = doc.context['environment']

    # Setup the builder
    builder = TexBuilder(env, context=doc.context)

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not doc.targets['.tex'].exists()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert doc.targets['.tex'].exists()

    # Check the answer key
    key = pathlib.Path('tests/builders/examples/ex3/dummy.tex')
    assert doc.targets['.tex'].read_text() == key.read_text()

    # New builders don't need to rebuild.
    builder = TexBuilder(env, context=doc.context)
    assert builder.status == 'done'


def test_tex_builder_inherited_doc(load_example):
    """Test a build with the TexBuilder using an inherited template."""
    # 1. example 1: tests/builders/examples/ex4
    doc = load_example('tests/builders/examples/ex4/dummy.dm')
    env = doc.context['environment']

    # Setup the builder
    builder = TexBuilder(env, context=doc.context)

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not doc.targets['.tex'].exists()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert doc.targets['.tex'].exists()
    # Check the answer key
    key = pathlib.Path('tests/builders/examples/ex4/dummy.tex')
    assert doc.targets['.tex'].read_text() == key.read_text()

    # New builders don't need to rebuild.
    builder = TexBuilder(env, context=doc.context)
    assert builder.status == 'done'


def test_tex_builder_add_build(load_example):
    """Test the TexBuilder with an added dependency through add_build."""

    # 1. Example 3 includes a media file that can be included in tex
    #    tests/builders/examples/ex5/
    #     └── src
    #         ├── index.dm
    #         └── media
    #             └── images
    #                 └── NMR
    #                     └── hsqc_bw.pdf
    doc = load_example('tests/builders/examples/ex5/src/index.dm')
    env = doc.context['environment']
    target_root = doc.context['target_root']

    # Setup the builder
    tex_builder = TexBuilder(env, context=doc.context)

    # Add a dependency for the media file
    build = tex_builder.add_build(infilepaths='media/images/NMR/hsqc_bw.pdf',
                                  context=doc.context)

    sp = SourcePath(project_root='tests/builders/examples/ex5/src',
                    subpath='media/images/NMR/hsqc_bw.pdf')
    tp = TargetPath(target_root=target_root, target='tex',
                    subpath='media/images/NMR/hsqc_bw.pdf')
    assert build.__class__.__name__ == 'Copy'
    assert build.infilepaths[0] == sp
    assert build.infilepaths[0].subpath == sp.subpath
    assert build.outfilepath == tp
    assert build.outfilepath.subpath == tp.subpath

    assert build.status == 'ready'
    assert tex_builder.status == 'ready'

    # Now run the build
    assert tex_builder.build(complete=True) == 'done'
    assert tex_builder.status == 'done'
    assert build.status == 'done'

    # Check that the files were created
    assert tp.is_file()
    assert sp.read_bytes() == tp.read_bytes()  # make sure it's the same as
                                               # original
