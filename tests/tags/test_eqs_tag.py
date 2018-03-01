"""
Test the equation tags.
"""
from disseminate.dependency_manager import DependencyManager
from disseminate.tags import Tag
from disseminate.tags.eqs import Eq
from disseminate import settings


def test_simple_inline_equation_html(tmpdir):
    """Test the rendering of simple inline equations for html."""

    # Setup the test paths
    project_root = str(tmpdir.join('src'))
    target_root = str(tmpdir)

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(project_root=project_root,
                            target_root=target_root,
                            segregate_targets=True)
    global_context = {'_dependencies': dep,
                      '_project_root': project_root,
                      '_target_root': target_root}
    local_context = {'_targets': {'.html': 'test.html'}}

    # Setup the equation tag
    eq = Eq(name='eq', content='y = x', attributes=tuple(),
            local_context=local_context, global_context=global_context)

    # Check the paths. These are stored by the parent Img tag in the
    # 'src_filepath' attribute
    assert eq.src_filepath == 'media/b5fe9c6383.tex'

    # Create a root tag and render the html
    root = Tag(name='root', content=["This is my test", eq, "equation"],
               attributes=tuple(), local_context=local_context,
               global_context=global_context)

    # get the root tag
    root_html = root.html()

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">This is my test'
    root_end = 'equation</span>\n'

    # Remove the root tag
    root_html = root.html()[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert root_html == ('<img class="eq" '
                         'src="/media/b5fe9c6383_crop_scale1.0.svg"/>')
    assert tmpdir.ensure(settings.media_dir, 'b5fe9c6383_crop_scale1.0.svg')
    assert tmpdir.ensure('.html', settings.media_dir,
                         'b5fe9c6383_crop_scale1.0.svg')


def test_simple_inline_equation_tex(tmpdir):
    """Test the rendering of simple inline equations for tex."""

    # Setup the test paths
    project_root = str(tmpdir.join('src'))
    target_root = str(tmpdir)

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(project_root=project_root,
                            target_root=target_root,
                            segregate_targets=True)
    global_context = {'_dependencies': dep,
                      '_project_root': project_root,
                      '_target_root': target_root}
    local_context = {'_targets': {'.html': 'test.html'}}

    # Setup the equation tag
    eq = Eq(name='eq', content='y = x', attributes=tuple(),
            local_context=local_context, global_context=global_context)

    assert eq.tex() == "$y = x$"
