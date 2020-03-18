"""
General tests for target builders.
"""
import pathlib
from collections import namedtuple

from disseminate.builders.target_builders.html_builder import HtmlBuilder
from disseminate.builders.target_builders.tex_builder import TexBuilder
from disseminate.paths import SourcePath, TargetPath


def test_target_builder_setup(env):
    """Test the setup of target builders """
    context = env.context
    tmpdir = context['target_root']

    for targer_builder_cls, target_subpath in ((HtmlBuilder, 'test.html'),
                                               (TexBuilder, 'test.tex'),):
        # 1. Setup the builder. At least an outfilepath is needed and a content
        #    is needed
        target_filepath = TargetPath(target_root=tmpdir, subpath=target_subpath)
        context['body'] = 'My test'

        builder = targer_builder_cls(env, context=context,
                                     outfilepath=target_filepath)

        # Check the infilepaths. These should be SourcePaths with correctly set
        # project_root / subpath
        assert len(builder.infilepaths) == 0
        assert builder.outfilepath == target_filepath


def test_html_builder_setup_doc(setup_example):
    """Test the setup of the HtmlBuilder with a Document"""
    # 1. example 1: tests/builders/target_builders/example1
    env, doc = setup_example('tests/builders/target_builders/example1',
                             'dummy.dm')

    for targer_builder_cls, ext in ((HtmlBuilder, 'html'),
                                    (TexBuilder, 'tex'),):

        # Setup the builder
        builder = targer_builder_cls(env, context=doc.context)

        # Check the infilepaths. These should be SourcePaths with correctly set
        # project_root / subpath
        assert len(builder.infilepaths) == 1
        assert builder.infilepaths[0].match('dummy.dm')
        assert (str(builder.infilepaths[0].subpath) ==
                'dummy.dm')
        assert builder.outfilepath.match('{ext}/dummy.{ext}'.format(ext=ext))
        assert str(builder.outfilepath.subpath) == 'dummy.{ext}'.format(ext=ext)
