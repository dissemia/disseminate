"""
Test the TexBuilder
"""
import pathlib
from collections import namedtuple

from disseminate.builders.target_builders.txt_builder import TxtBuilder
from disseminate.paths import SourcePath, TargetPath


def test_txt_builder_setup_in_targets(env):
    """Test the setup of a TxtBuilder when 'txt' is listed as a target
    in the context['targets']"""
    context = env.context
    src_filepath = context['src_filepath']
    target_root = context['target_root']

    # 1. Setup the builder without an outfilepath.  In this case, 'tex' is
    #    listed in the targets, so the outfilepath will *not* be in the
    #    cache directory
    context['targets'] |= {'txt'}
    target_filepath = TargetPath(target_root=target_root, target='txt',
                                 subpath='test.txt')
    builder = TxtBuilder(env, context=context)

    # check the build
    assert context['builders']['.txt'] == builder  # builder in context
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
                                 subpath='final.txt')
    builder = TxtBuilder(env, context=context, outfilepath=target_filepath)

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


def test_txt_builder_setup_not_in_targets(env):
    """Test the setup of a TxtBuilder when 'txt' is not listed as a target
    in the context['targets']"""
    context = env.context
    src_filepath = context['src_filepath']
    target_root = context['target_root']

    # 1. Setup the builder without an outfilepath.  In this case, 'tex' is *not*
    #    listed in the targets, so the outfilepath will be in the
    #    cache directory
    context['targets'] -= {'txt'}
    target_filepath = TargetPath(target_root=target_root / '.cache',
                                 target='txt', subpath='test.txt')
    builder = TxtBuilder(env, context=context)

    # check the build
    assert context['builders']['.txt'] == builder  # builder in context
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


def test_txt_builder_simple(env):
    """Test a simple build with the TxtBuilder """
    context = env.context
    tmpdir = context['target_root']

    # 1. Setup the builder. At least an outfilepath is needed and a content
    #    is needed
    target_filepath = TargetPath(target_root=tmpdir, target='txt',
                                 subpath='test.txt')
    tag = namedtuple('tag', 'txt')
    context['body'] = tag(txt="My body")  # expects {{ body.tex }}

    builder = TxtBuilder(env, context=context, outfilepath=target_filepath)

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
    builder = TxtBuilder(env, context=context, outfilepath=target_filepath)
    assert builder.status == 'done'


def test_txt_builder_simple_doc(load_example):
    """Test a simple build with the TxtBuilder."""
    # 1. example 1: tests/builders/examples/ex3
    doc = load_example('tests/builders/examples/ex3/dummy.dm')
    env = doc.context['environment']

    # Setup the builder
    builder = TxtBuilder(env, context=doc.context)

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not doc.targets['.txt'].exists()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert doc.targets['.txt'].exists()

    # Check the answer key
    key = pathlib.Path('tests/builders/examples/ex3/dummy.txt')
    assert doc.targets['.txt'].read_text() == key.read_text()

    # New builders don't need to rebuild.
    builder = TxtBuilder(env, context=doc.context)
    assert builder.status == 'done'


def test_txt_builder_simple_doc_build(load_example):
    """Test a render of a simple document with the TxtBuilder."""
    # 1. example 1: tests/builders/examples/ex3
    doc = load_example('tests/builders/examples/ex3/dummy.dm')
    target_root = doc.target_root

    doc.build()

    # Check the copied and built files
    tgt_filepath = TargetPath(target_root=target_root, target='txt',
                              subpath='dummy.txt')
    assert tgt_filepath.exists()
    key = pathlib.Path('tests/builders/examples/ex3/dummy.txt')
    assert tgt_filepath.read_text() == key.read_text()
