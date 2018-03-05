"""
Test the equation tags.
"""
from disseminate.tags import Tag
from disseminate.tags.eqs import Eq, EqBold
from disseminate.dependency_manager import DependencyManager
from disseminate.ast import process_ast
from disseminate import settings


def test_inline_equation(tmpdir):
    """Test the tex rendering of a simple inline equations."""

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

    # Example 1 - simple inline equation
    eq1 = Eq(name='eq', content='y=x', attributes=tuple(),
             local_context=local_context, global_context=global_context)
    assert eq1.tex() == "\ensuremath{y=x}"

    # Example 2 - nested inline equation with subtag as content
    eq2 = Eq(name='eq', content=eq1, attributes=tuple(),
             local_context=local_context, global_context=global_context)
    assert eq2.tex() == "\ensuremath{y=x}"

    # Example 3 - nested inline equation with subtag as list
    eq3 = Eq(name='eq', content=['test is my ', eq2], attributes=tuple(),
             local_context=local_context, global_context=global_context)
    assert eq3.tex() == "\ensuremath{test is my y=x}"

    # Example 4 - a bold equation
    eq4 = EqBold(name='eq', content="y=x", attributes=tuple(),
                 local_context=local_context, global_context=global_context)
    assert eq4.tex() == "\ensuremath{\\boldsymbol{y=x}}"

    # Example 5 - an equation with a  bold equation subtag
    eq5 = Eq(name='eq', content=eq4, attributes=tuple(),
             local_context=local_context, global_context=global_context)
    assert eq5.tex() == "\ensuremath{\\boldsymbol{y=x}}"

    # Example 6 - an equation with a  bold equation subtag in a list
    eq6 = Eq(name='eq', content=['this is my ', eq4], attributes=tuple(),
             local_context=local_context, global_context=global_context)
    assert eq6.tex() == "\ensuremath{this is my \\boldsymbol{y=x}}"

    # Example 7 - a bold equation with an equation subtag in a list
    eq7 = EqBold(name='eq', content=['this is my ', eq1], attributes=tuple(),
             local_context=local_context, global_context=global_context)
    assert eq7.tex() == "\ensuremath{\\boldsymbol{this is my y=x}}"


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
    assert eq.src_filepath == 'media/d56f079b8f.tex'

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
                         'src="/media/d56f079b8f.svg"/>')
    assert tmpdir.ensure(settings.media_dir, 'd56f079b8f.svg')
    assert tmpdir.ensure('.html', settings.media_dir,
                         'd56f079b8f.svg')


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

    assert eq.tex() == "\\ensuremath{y = x}"


def test_block_equation_tex(tmpdir):
    """Test the rendering of block equations for tex."""

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
    local_context = {'_targets': {'.tex': 'test.tex'}}

    # Test markup
    test = """
    @section{Section 1}
    
    @eq{y &= x + b \\
          &= x + a}
    """

    root = process_ast([test], local_context=local_context,
                       global_context=global_context)

    print(root)
    print(root.tex())
