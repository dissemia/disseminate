"""
Test the render builder
"""
from collections import namedtuple
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

    # Check the infilepaths
    assert len(render_build.infilepaths) == 4
    assert render_build.infilepaths[0].match('templates/default/template.html')
    assert render_build.infilepaths[1].match('templates/default/menu.html')
    assert render_build.infilepaths[2].match('templates/default/context.txt')
    assert "My body" in render_build.infilepaths[3]


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

    # Check the infilepaths
    assert len(render_build.infilepaths) == 7
    assert render_build.infilepaths[0].match('templates/books/'
                                             'tufte/template.html')
    assert render_build.infilepaths[1].match('templates/default/template.html')
    assert render_build.infilepaths[2].match('templates/default/menu.html')
    assert render_build.infilepaths[3].match('templates/default/nav.html')
    assert render_build.infilepaths[4].match('templates/books/'
                                             'tufte/context.txt')
    assert render_build.infilepaths[5].match('templates/default/context.txt')
    assert "My body" in render_build.infilepaths[6]


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




# def test_render(env, doc):
#     """Test the Render builder."""
#     # Setup the renderer
#     ## FIXME: renderer should not use dependency manager and the context
#     # should hold renderer classes that can be instantiated with the contents.
#     renderer = doc.context['renderers']['template']
#     context = doc.context
#     target_root = context['target_root']
#
#     # 1. Setup the render build with a specified outfilepath
#     outfilepath = TargetPath(target_root=target_root, target='html',
#                              subpath='subpath')
#     render_build = Render(env, renderer, outfilepath=outfilepath,
#                           target='.html', context=context)
#
#     # Check that the render build is correctly setup
#     assert render_build.build()
#     assert render_build.infilepaths == []
#
#     assert '<html lang="en">' in renderer.render(context=context,
#                                                  target='.html')
