"""
Test the render builder
"""
import pathlib

import jinja2
import pytest

from disseminate.builders.jinja_render import (JinjaRender, template_filepaths,
                                               context_filepaths)
from disseminate.tags import Tag
from disseminate.paths import TargetPath


def hash_filename1(ext):
    return 'template_68c8b3e6dc51' + ext


def hash_filename2(ext):
    return 'template_a471ff72af26' + ext


@pytest.fixture
def jinja2_env():
    """Setup a jinja2 environment"""
    # Setup environments and loaders
    pl = jinja2.loaders.PackageLoader('disseminate', 'templates')

    env = jinja2.environment.Environment(loader=pl)
    return env


def test_jinja_render_with_find_builder_cls():
    """Test the JinjaRender builder access with the find_builder_cls."""

    builder_cls = JinjaRender.find_builder_cls(in_ext='.render')
    assert builder_cls.__name__ == "JinjaRender"


def test_jinja_render_setup_with_outfilepath(env):
    """Test the setup of the JinjaRender builder with an outfilepath
    specified."""

    context = env.context
    target_root = context['target_root']

    # 1. Setup the render build with a specified outfilepath. A default
    #    template 'templates/default' is used.
    outfilepath = TargetPath(target_root=target_root, target='html',
                             subpath='subpath.html')
    tag = Tag(name='body', content='My body', attributes='', context=context)
    context['body'] = tag

    render_build = JinjaRender(env, outfilepath=outfilepath, context=context)

    # Check the parameters and infilepaths. These should be SourcePaths with
    # correctly set project_root / subpath
    assert len(render_build.parameters) == 17
    assert len(render_build.infilepaths) == 14
    assert render_build.infilepaths[0].match('default/html/template.html')
    assert (str(render_build.infilepaths[0].subpath) ==
            'template.html')
    assert render_build.infilepaths[1].match('default/html/menu.html')
    assert (str(render_build.infilepaths[1].subpath) ==
            'menu.html')
    assert render_build.infilepaths[2].match('default/context.txt')
    assert (str(render_build.infilepaths[2].subpath) ==
            'context.txt')
    assert render_build.infilepaths[3].match('default/html/'
                                             'media/css/bootstrap.min.css')
    assert (str(render_build.infilepaths[3].subpath) ==
            'media/css/bootstrap.min.css')
    assert render_build.infilepaths[4].match('default/html/'
                                             'media/css/base.css')
    assert (str(render_build.infilepaths[4].subpath) ==
            'media/css/base.css')
    assert render_build.infilepaths[5].match('default/html/'
                                             'media/css/default.css')
    assert (str(render_build.infilepaths[5].subpath) ==
            'media/css/default.css')
    assert render_build.infilepaths[6].match('default/html/'
                                             'media/css/pygments.css')
    assert (str(render_build.infilepaths[6].subpath) ==
            'media/css/pygments.css')
    assert (str(render_build.infilepaths[7].subpath) ==
            'media/icons/menu_inactive.svg')
    assert (str(render_build.infilepaths[8].subpath) ==
            'media/icons/menu_active.svg')
    assert (str(render_build.infilepaths[9].subpath) ==
            'media/icons/dm_icon.svg')
    assert (str(render_build.infilepaths[10].subpath) ==
            'media/icons/txt_icon.svg')
    assert (str(render_build.infilepaths[11].subpath) ==
            'media/icons/tex_icon.svg')
    assert (str(render_build.infilepaths[12].subpath) ==
            'media/icons/pdf_icon.svg')
    assert (str(render_build.infilepaths[13].subpath) ==
            'media/icons/epub_icon.svg')
    assert render_build.parameters[14] == '33996cdb1a'  # hash of tags
    assert render_build.parameters[15] == 'd41d8cd98f'  # hash of tags
    assert render_build.parameters[16] == 'e596b323f6'  # hash of tags

    # Check the outfilepath
    assert render_build.outfilepath == outfilepath


def test_jinja_render_setup_without_outfilepath(env):
    """Test the setup of the JinjaRender builder with an outfilepath
    specified."""

    context = env.context

    # 2. Test an example without an outfilepath. However, a target must be
    #    specified.
    tag = Tag(name='body', content='My body', attributes='', context=context)
    context['body'] = tag

    render_build = JinjaRender(env, context=context, render_ext='.html')
    assert len(render_build.parameters) == 17
    assert len(render_build.infilepaths) == 14
    assert (render_build.outfilepath ==
            env.target_root / 'media' / hash_filename1('.html'))

    # The same tag body gives the same hash
    tag = Tag(name='body', content='My body', attributes='', context=context)
    context['body'] = tag

    render_build = JinjaRender(env, context=context, render_ext='.html')
    assert (render_build.outfilepath ==
            env.target_root / 'media' / hash_filename1('.html'))

    # A new content body produces a different hash
    tag = Tag(name='body', content='My new body', attributes='',
              context=context)
    context['body'] = tag
    render_build = JinjaRender(env, context=context, render_ext='.html')
    assert (render_build.outfilepath ==
            env.target_root / 'media' / hash_filename2('.html'))

    # 3. Test an example without an outfilepath or target specified. An
    #    assertion error is raised
    with pytest.raises(AssertionError):
        JinjaRender(env, context=context)


def test_jinja_render_setup_inherited(env):
    """Test the setup of the JinjaRender builder with a template that uses
    inheritance."""

    context = env.context
    target_root = context['target_root']

    # 1. Setup the render build with a specified outfilepath. A default
    #    template 'templates/default' is used.
    outfilepath = TargetPath(target_root=target_root, target='html',
                             subpath='subpath.html')
    tag = Tag(name='body', content='My body', attributes='', context=context)
    context['body'] = tag
    context['template'] = 'books/tufte'

    render_build = JinjaRender(env, outfilepath=outfilepath, context=context)

    # Check the parameters and infilepaths. These should be SourcePaths with
    # correctly set project_root / subpath
    assert len(render_build.parameters) == 21
    assert len(render_build.infilepaths) == 18
    assert render_build.infilepaths[0].match('books/tufte/html/'
                                             'template.html')
    assert render_build.infilepaths[1].match('default/html/template.html')
    assert render_build.infilepaths[2].match('default/html/menu.html')
    assert render_build.infilepaths[3].match('default/html/nav.html')
    assert render_build.infilepaths[4].match('books/tufte/context.txt')
    assert render_build.infilepaths[5].match('default/context.txt')
    assert render_build.infilepaths[6].match('books/tufte/html/'
                                             'media/css/tufte.css')
    assert render_build.infilepaths[7].match('default/html/'
                                             'media/css/bootstrap.min.css')
    assert render_build.infilepaths[8].match('default/html/'
                                             'media/css/base.css')
    assert render_build.infilepaths[9].match('default/html/'
                                             'media/css/default.css')
    assert render_build.infilepaths[10].match('default/html/'
                                              'media/css/pygments.css')
    assert render_build.infilepaths[11].match('default/html/'
                                              'media/icons/menu_inactive.svg')
    assert render_build.infilepaths[12].match('default/html/'
                                              'media/icons/menu_active.svg')
    assert render_build.infilepaths[13].match('default/html/'
                                              'media/icons/dm_icon.svg')
    assert render_build.infilepaths[14].match('default/html/'
                                              'media/icons/txt_icon.svg')
    assert render_build.infilepaths[15].match('default/html/'
                                              'media/icons/tex_icon.svg')
    assert render_build.infilepaths[16].match('default/html/'
                                              'media/icons/pdf_icon.svg')
    assert render_build.infilepaths[17].match('default/html/'
                                              'media/icons/epub_icon.svg')
    assert render_build.parameters[18] == "33996cdb1a"  # tag hash
    assert render_build.parameters[19] == "d41d8cd98f"  # tag hash
    assert render_build.parameters[20] == "e596b323f6"  # tag hash


def test_jinja_render(env):
    """Test the JinjaRender build"""
    context = env.context
    target_root = context['target_root']

    # 1. Setup the render build with a specified outfilepath. A default
    #    template 'templates/default' is used.
    outfilepath = TargetPath(target_root=target_root, target='html',
                             subpath='subpath.html')
    tag = Tag(name='body', content='My body', attributes='', context=context)
    context['body'] = tag

    render_build = JinjaRender(env, outfilepath=outfilepath, context=context)

    # Check that a build is needed
    assert not outfilepath.exists()
    assert render_build.build_needed()
    assert render_build.status == 'ready'

    # Run the build
    assert render_build.build(complete=True) == 'done'
    assert not render_build.build_needed()
    assert outfilepath.exists()
    assert 'My body' in outfilepath.read_text()

    # 2. A new builder will not need to build
    render_build = JinjaRender(env, outfilepath=outfilepath, context=context)
    assert not render_build.build_needed()
    assert render_build.status == 'done'

    # 3. But changing the contents will trigger a new build
    context['body'] = Tag(name='body', content='My new body', attributes='',
                          context=context)
    render_build = JinjaRender(env, outfilepath=outfilepath, context=context)

    assert render_build.build_needed()
    assert render_build.build(complete=True) == 'done'

    # 4. Test an example without an outfilepath. However, a render_ext must be
    #    specified.
    render_build = JinjaRender(env, context=context, render_ext='.html')

    assert not render_build.outfilepath.exists()
    assert render_build.status == 'ready'

    assert render_build.build_needed()
    assert render_build.build(complete=True) == 'done'
    assert render_build.outfilepath.exists()
    assert (render_build.outfilepath.subpath ==
            pathlib.Path('media') / hash_filename2('.html'))
    assert render_build.status == 'done'

    # A new builder does not require a new build.
    render_build = JinjaRender(env, context=context, render_ext='.html')
    assert render_build.status == 'done'

    # 5. Test an example without an outfilepath but render_ext and document
    #    target specified
    render_build = JinjaRender(env, target='test', context=context,
                               render_ext='.html')

    assert not render_build.outfilepath.exists()
    assert render_build.status == 'ready'

    assert render_build.build_needed()
    assert render_build.build(complete=True) == 'done'
    assert render_build.outfilepath.exists()
    assert str(render_build.outfilepath.target) == 'test'
    assert (render_build.outfilepath.subpath ==
            pathlib.Path('media') / hash_filename2('.html'))
    assert render_build.status == 'done'

    # A new builder does not require a new build.
    render_build = JinjaRender(env, context=context, render_ext='.html')
    assert render_build.status == 'done'


def test_template_filepaths(jinja2_env):
    """Test the template_filepaths function."""

    # 1. Test the package loader path. It should only have 1 path for the
    #    disseminate package
    template = jinja2_env.get_or_select_template('default/tex/template.tex')
    pl_path = template_filepaths(template, environment=jinja2_env)
    assert len(pl_path) == 1
    assert pl_path[0].match('disseminate/templates/default/tex/template.tex')

    # 2. Test an example with template inheritance
    template = jinja2_env.get_or_select_template('books/tufte/tex/'
                                                 'template.tex')
    pl_path = template_filepaths(template, environment=jinja2_env)
    assert len(pl_path) == 2
    assert pl_path[0].match('disseminate/templates/books/tufte/'
                            'tex/template.tex')
    assert pl_path[1].match('disseminate/templates/default/'
                            'tex/template.tex')


def test_context_filepaths(jinja2_env):
    """Test the context_filepaths function."""

    # 1. Test a basic package template
    template = jinja2_env.get_or_select_template('default/tex/template.tex')
    template_fps = template_filepaths(template, environment=jinja2_env)

    # Get the context filepath for this template
    fps = context_filepaths(template_fps)
    assert len(fps) == 1
    assert fps[0].match('disseminate/templates/default/context.txt')

    # 2. Test a package template with inheritance
    template = jinja2_env.get_or_select_template('books/tufte/tex/'
                                                 'template.tex')
    template_fps = template_filepaths(template, environment=jinja2_env)

    # Get the context filepath for this template
    fps = context_filepaths(template_fps)
    assert len(fps) == 2
    assert fps[0].match('disseminate/templates/books/tufte/context.txt')
    assert fps[1].match('disseminate/templates/default/context.txt')
