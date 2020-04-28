"""
Test the render builder
"""
from collections import namedtuple

import jinja2
import pytest

from disseminate.builders.jinja_render import (JinjaRender, template_filepaths,
                                               context_filepaths)
from disseminate.paths import TargetPath


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


def test_jinja_render_setup(env):
    """Test the setup of the JinjaRender builder."""
    context = env.context
    target_root = context['target_root']

    # 1. Setup the render build with a specified outfilepath. A default template
    #    'templates/default' is used.
    outfilepath = TargetPath(target_root=target_root, target='html',
                             subpath='subpath.html')
    tag = namedtuple('tag', 'html')
    context['body'] = tag(html="My body")  # expects {{ body.html }}

    render_build = JinjaRender(env, outfilepath=outfilepath, context=context)

    # Check the parameters and infilepaths. These should be SourcePaths with
    # correctly set project_root / subpath
    assert len(render_build.parameters) == 8
    assert len(render_build.infilepaths) == 7
    assert render_build.infilepaths[0].match('templates/default/template.html')
    assert (str(render_build.infilepaths[0].subpath) ==
            'template.html')
    assert render_build.infilepaths[1].match('templates/default/menu.html')
    assert (str(render_build.infilepaths[1].subpath) ==
            'menu.html')
    assert render_build.infilepaths[2].match('templates/default/context.txt')
    assert (str(render_build.infilepaths[2].subpath) ==
            'context.txt')
    assert render_build.infilepaths[3].match('templates/default/'
                                             'media/css/bootstrap.min.css')
    assert (str(render_build.infilepaths[3].subpath) ==
            'media/css/bootstrap.min.css')
    assert render_build.infilepaths[4].match('templates/default/'
                                             'media/css/base.css')
    assert (str(render_build.infilepaths[4].subpath) ==
            'media/css/base.css')
    assert render_build.infilepaths[5].match('templates/default/'
                                             'media/css/default.css')
    assert (str(render_build.infilepaths[5].subpath) ==
            'media/css/default.css')
    assert render_build.infilepaths[6].match('templates/default/'
                                             'media/css/pygments.css')
    assert (str(render_build.infilepaths[6].subpath) ==
            'media/css/pygments.css')
    assert "My body" in render_build.parameters[7]

    # Check the outfilepath
    assert render_build.outfilepath == outfilepath

    # 2. Test an example without an outfilepath. However, a target must be
    #    specified.
    context['body'] = tag(html="My body")  # expects {{ body.html }}
    render_build = JinjaRender(env, context=context, render_ext='.html')
    assert len(render_build.parameters) == 8
    assert len(render_build.infilepaths) == 7
    assert render_build.outfilepath.target_root == env.cache_path
    assert str(render_build.outfilepath.subpath) == ('media/template_'
                                                     '9c695c53185d.html')

    # A new content body produces a different hash
    context['body'] = tag(html="My new body")  # expects {{ body.html }}
    render_build = JinjaRender(env, context=context, render_ext='.html')
    assert render_build.outfilepath.target_root == env.cache_path
    assert str(render_build.outfilepath.subpath) == ('media/template_'
                                                     '10d3c1460f63.html')

    # 3. Test an example without an outfilepath or target specified. An
    #    assertion error is raised
    with pytest.raises(AssertionError):
        JinjaRender(env, context=context)


def test_jinja_render_setup_inherited(env):
    """Test the setup of the JinjaRender builder with a template that uses
    inheritance."""

    context = env.context
    target_root = context['target_root']

    # 1. Setup the render build with a specified outfilepath. A default template
    #    'templates/default' is used.
    outfilepath = TargetPath(target_root=target_root, target='html',
                             subpath='subpath.html')
    tag = namedtuple('tag', 'html')
    context['body'] = tag(html="My body")  # expects {{ body.html }}
    context['template'] = 'books/tufte'

    render_build = JinjaRender(env, outfilepath=outfilepath, context=context)

    # Check the parameters and infilepaths. These should be SourcePaths with
    # correctly set project_root / subpath
    assert len(render_build.parameters) == 12
    assert len(render_build.infilepaths) == 11
    assert render_build.infilepaths[0].match('templates/books/tufte/'
                                             'template.html')
    assert (str(render_build.infilepaths[0].subpath) ==
            'template.html')
    assert render_build.infilepaths[1].match('templates/default/template.html')
    assert (str(render_build.infilepaths[1].subpath) ==
            'template.html')
    assert render_build.infilepaths[2].match('templates/default/menu.html')
    assert (str(render_build.infilepaths[2].subpath) ==
            'menu.html')
    assert render_build.infilepaths[3].match('templates/default/nav.html')
    assert (str(render_build.infilepaths[3].subpath) ==
            'nav.html')
    assert render_build.infilepaths[4].match('templates/books/'
                                             'tufte/context.txt')
    assert (str(render_build.infilepaths[4].subpath) ==
            'context.txt')
    assert render_build.infilepaths[5].match('templates/default/context.txt')
    assert (str(render_build.infilepaths[5].subpath) ==
            'context.txt')
    assert render_build.infilepaths[6].match('templates/books/tufte/'
                                             'media/css/tufte.css')
    assert (str(render_build.infilepaths[6].subpath) ==
            'media/css/tufte.css')
    assert render_build.infilepaths[7].match('templates/default/'
                                             'media/css/bootstrap.min.css')
    assert (str(render_build.infilepaths[7].subpath) ==
            'media/css/bootstrap.min.css')
    assert render_build.infilepaths[8].match('templates/default/'
                                             'media/css/base.css')
    assert (str(render_build.infilepaths[8].subpath) ==
            'media/css/base.css')
    assert render_build.infilepaths[9].match('templates/default/'
                                             'media/css/default.css')
    assert (str(render_build.infilepaths[9].subpath) ==
            'media/css/default.css')
    assert render_build.infilepaths[10].match('templates/default/'
                                              'media/css/pygments.css')
    assert (str(render_build.infilepaths[10].subpath) ==
            'media/css/pygments.css')
    assert "My body" in render_build.parameters[11]


def test_jinja_render(env):
    """Test the JinjaRender build"""
    context = env.context
    target_root = context['target_root']

    # 1. Setup the render build with a specified outfilepath. A default template
    #    'templates/default' is used.
    outfilepath = TargetPath(target_root=target_root, target='html',
                             subpath='subpath.html')
    tag = namedtuple('tag', 'html')
    context['body'] = tag(html="My body")  # expects {{ body.html }}

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
    context['body'] = tag(html="My new body")  # expects {{ body.html }}
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
    assert str(render_build.outfilepath.subpath) == ('media/template_'
                                                     '10d3c1460f63.html')
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
    assert str(render_build.outfilepath.subpath) == ('media/template_'
                                                     '10d3c1460f63.html')
    assert render_build.status == 'done'

    # A new builder does not require a new build.
    render_build = JinjaRender(env, context=context, render_ext='.html')
    assert render_build.status == 'done'


def test_template_filepaths(jinja2_env):
    """Test the template_filepaths function."""

    # 1. Test the package loader path. It should only have 1 path for the
    #    disseminate package
    template = jinja2_env.get_or_select_template('default/template.tex')
    pl_path = template_filepaths(template, environment=jinja2_env)
    assert len(pl_path) == 1
    assert pl_path[0].match('disseminate/templates/default/template.tex')

    # 2. Test an example with template inheritance
    template = jinja2_env.get_or_select_template('books/tufte/template.tex')
    pl_path = template_filepaths(template, environment=jinja2_env)
    assert len(pl_path) == 2
    assert pl_path[0].match('disseminate/templates/books/tufte/template.tex')
    assert pl_path[1].match('disseminate/templates/default/template.tex')


def test_context_filepaths(jinja2_env):
    """Test the context_filepaths function."""

    # 1. Test a basic package template
    template = jinja2_env.get_or_select_template('default/template.tex')
    template_fps = template_filepaths(template, environment=jinja2_env)

    # Get the context filepath for this template
    fps = context_filepaths(template_fps)
    assert len(fps) == 1
    assert fps[0].match('disseminate/templates/default/context.txt')

    # 2. Test a package template with inheritance
    template = jinja2_env.get_or_select_template('books/tufte/template.tex')
    template_fps = template_filepaths(template, environment=jinja2_env)

    # Get the context filepath for this template
    fps = context_filepaths(template_fps)
    assert len(fps) == 2
    assert fps[0].match('disseminate/templates/books/tufte/context.txt')
    assert fps[1].match('disseminate/templates/default/context.txt')
