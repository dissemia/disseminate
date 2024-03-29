"""
General tests for target builders.
"""
from collections import namedtuple
import pathlib

from disseminate.builders.target_builders.html_builder import HtmlBuilder
from disseminate.builders.target_builders.tex_builder import TexBuilder
from disseminate.paths import SourcePath, TargetPath
from disseminate.signals import signal


# Paths for examples
ex3_root = pathlib.Path('tests') / 'builders' / 'examples' / 'ex3'
ex3_srcdir = ex3_root / 'src'


def test_target_builder_setup(env):
    """Test the setup of target builders."""
    context = env.context
    tmpdir = context['target_root']
    root_document = env.root_document
    src_filepath = root_document.src_filepath

    for targer_builder_cls, target_subpath in ((HtmlBuilder, 'test.html'),
                                               (TexBuilder, 'test.tex'),):
        # 1. Setup the builder. At least an outfilepath is needed and a content
        #    is needed
        target_filepath = TargetPath(target_root=tmpdir,
                                     subpath=target_subpath)
        context['body'] = 'My test'

        builder = targer_builder_cls(env, context=context,
                                     outfilepath=target_filepath)

        # Check the parameters. These should be SourcePaths with correctly set
        # project_root / subpath
        cls_name = targer_builder_cls.__name__
        assert len(builder.parameters) == 2
        assert builder.parameters == ["build '{}'".format(cls_name),
                                      src_filepath]
        assert builder.outfilepath == target_filepath


def test_target_builder_setup_doc(load_example):
    """Test the setup of the target builders with a Document"""
    # 1. example 1: tests/builders/examples/ex3
    doc = load_example(ex3_srcdir / 'dummy.dm', cp_src=True)
    env = doc.context['environment']

    for targer_builder_cls, ext in ((HtmlBuilder, 'html'),
                                    (TexBuilder, 'tex'),):
        # Setup the builder
        builder = targer_builder_cls(env, context=doc.context)

        # Check the parameters. These should be SourcePaths with correctly set
        # project_root / subpath
        cls_name = targer_builder_cls.__name__
        assert len(builder.parameters) == 2
        assert builder.parameters[0] == "build '{}'".format(cls_name)
        assert builder.parameters[1].match('dummy.dm')
        assert (str(builder.parameters[1].subpath) ==
                'dummy.dm')
        assert builder.outfilepath.match('{ext}/dummy.{ext}'.format(ext=ext))
        assert (str(builder.outfilepath.subpath) ==
                'dummy.{ext}'.format(ext=ext))


def test_target_builder_decision(env):
    """Test the build decision for target builders"""
    context = env.context
    tmpdir = context['target_root']
    Tag = namedtuple('Tag', 'tex html')
    tag = Tag(tex='My body', html='My body')

    for targer_builder_cls, target in ((HtmlBuilder, 'html'),
                                       (TexBuilder, 'tex'),):
        # Write a source file
        subpath = 'test_{target}.dm'.format(target=target)
        src_filepath = SourcePath(project_root=tmpdir, subpath=subpath)
        src_filepath.write_text('test 1')

        # Setup the builder. At least an outfilepath is needed and a content
        # is needed
        subpath = 'test.{ext}'.format(ext=target)
        target_filepath = TargetPath(target_root=tmpdir, target=target,
                                     subpath=subpath)
        context['body'] = tag

        builder = targer_builder_cls(env, context=context,
                                     parameters=src_filepath,
                                     outfilepath=target_filepath)

        # Check the build and run the build
        assert len(builder.subbuilders) > 0
        assert src_filepath in builder.parameters
        assert builder.outfilepath == target_filepath
        assert builder.status == 'ready'
        assert builder.build(complete=True) == 'done'
        assert target_filepath.is_file()

        # A new builder will not need a build
        builder = targer_builder_cls(env, context=context,
                                     parameters=src_filepath,
                                     outfilepath=target_filepath)
        assert builder.status == 'done'

        # If we change the source file, a new build is needed
        src_filepath.write_text('test 2')

        builder = targer_builder_cls(env, context=context,
                                     parameters=src_filepath,
                                     outfilepath=target_filepath)

        assert builder.build_needed()

        # However, since the builder doesn't use the src_filepath in its build
        # nothing needs to be done
        assert builder.status == 'done'
        assert builder.build(complete=True) == 'done'
        assert target_filepath.is_file()


def test_target_builder_ref_labels_html(env):
    """Test target builders with ref label dependencies with the
    HtmlBuilder."""

    # Check that the signal is in place
    sig = signal("ref_label_dependencies")
    assert len(sig.receivers) > 0  # at least 1 receiver is in place

    context = env.context
    tmpdir = context['target_root']
    root_document = env.root_document
    src_filepath = root_document.src_filepath

    target_filepath = TargetPath(target_root=tmpdir, subpath='test.html')
    context['body'] = 'My test'

    # 1. Setup the basic target builder
    builder = HtmlBuilder(env, context=context, outfilepath=target_filepath)
    jinja_builder = builder.subbuilders[1]

    name = HtmlBuilder.__name__
    assert len(builder.parameters) == 2
    assert builder.parameters == ["build '{}'".format(name), src_filepath]

    assert jinja_builder.__class__.__name__ == "JinjaRender"
    assert len(jinja_builder.parameters) == 16

    assert builder.build_needed()
    assert builder.build(complete=True) == 'done'
    assert not builder.build_needed()

    # 2. Add a ref label dependency
    root_document.src_filepath.write_text("""
    @chapter[id=ch:intro]{First Chapter}
    @ref{ch:intro}
    """)
    root_document.load()

    assert len(builder.parameters) == 3
    assert builder.parameters[:2] == ["build '{}'".format(name), src_filepath]
    assert 'First Chapter' in str(builder.parameters[2])
    assert 'ch:intro' in str(builder.parameters[2])
