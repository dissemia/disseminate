"""
Test the Epub builders
"""
import pathlib

import epubcheck

from disseminate.builders.epub import XHtml2Epub
from disseminate.paths import SourcePath, TargetPath


# paths for examples
ex10_root = pathlib.Path('tests') / 'builders' / 'examples' / 'ex10' / 'xhtml'

# parameters for examples
parameters_ex10 = [SourcePath(project_root=ex10_root, subpath='toc.xhtml'),
                   SourcePath(project_root=ex10_root, subpath='ch01.xhtml'),
                   SourcePath(project_root=ex10_root, subpath='ch02.xhtml'),
                   SourcePath(project_root=ex10_root,
                              subpath='media/css/default.css')]


def test_create_opf_builder(env):
    """Test the create_opf_builder function."""
    context = env.context

    builder = XHtml2Epub(env=env, parameters=parameters_ex10, context=context)
    render_builder = builder.create_opf_builder()
    assert render_builder.build(complete=True) == 'done'
    assert render_builder.outfilepath.exists()


def test_xhtml2epub_setup_with_outfilepath(env):
    """Test the setup of the XHtml2Epub builder with an outfilepath
    specified."""
    context = env.context
    target_root = context['target_root']

    # 1. Setup the render build with a specified outfilepath. A default template
    #    'templates/default' is used.
    outfilepath = TargetPath(target_root=target_root, target='epub',
                             subpath='test.epub')

    builder = XHtml2Epub(env=env, parameters=parameters_ex10, context=context,
                         outfilepath=outfilepath)

    # Check the parameters and infilepaths. These should be SourcePaths with
    # correctly set project_root / subpath
    assert len(builder.parameters) == 4  # 4 xhtml files
    assert builder.outfilepath == outfilepath


def test_xhtml2epub_build(env):
    """Test a simple build with the XHtml2Epub builder."""

    context = env.context
    target_root = context['target_root']

    # 1. Setup a build from example 10, which contains xhtml files
    outfilepath = TargetPath(target_root=target_root, target='epub',
                             subpath='test.epub')

    builder = XHtml2Epub(env=env, parameters=parameters_ex10, context=context,
                         outfilepath=outfilepath)

    assert builder.build(complete=True) == 'done'

    # Check the epub file
    valid = epubcheck.validate(builder.outfilepath)
    assert valid is True
