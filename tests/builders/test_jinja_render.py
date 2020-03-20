"""
Test the render builder
"""
from collections import namedtuple

import pytest

from disseminate.builders.jinja_render import JinjaRender
from disseminate.paths import TargetPath


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

    # Check the infilepaths. These should be SourcePaths with correctly set
    # project_root / subpath
    assert len(render_build.infilepaths) == 8
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
    assert "My body" in render_build.infilepaths[7]

    # 2. Test an example without an outfilepath. However, a target must be
    #    specified.
    context['body'] = tag(html="My body")  # expects {{ body.html }}
    render_build = JinjaRender(env, context=context, target='.html')
    assert len(render_build.infilepaths) == 8
    assert str(render_build.outfilepath.subpath) == '8542405607fd.html'

    # A new content body produces a different hash
    context['body'] = tag(html="My new body")  # expects {{ body.html }}
    render_build = JinjaRender(env, context=context, target='.html')
    assert str(render_build.outfilepath.subpath) == 'bce375a982d5.html'

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

    # Check the infilepaths. These should be SourcePaths with correctly set
    # project_root / subpath
    assert len(render_build.infilepaths) == 12
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
    assert "My body" in render_build.infilepaths[11]


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

    # 4. Test an example without an outfilepath. However, a target must be
    #    specified.
    render_build = JinjaRender(env, context=context, target='.html')

    assert not render_build.outfilepath.exists()
    assert render_build.status == 'ready'

    assert render_build.build_needed()
    assert render_build.build(complete=True) == 'done'
    assert render_build.outfilepath.exists()
    assert str(render_build.outfilepath.subpath) == 'bce375a982d5.html'
    assert render_build.status == 'done'

    # A new builder does not require a new build.
    render_build = JinjaRender(env, context=context, target='.html')
    assert render_build.status == 'done'
