"""
Test the equation tags.
"""
from disseminate.tags import Tag
from disseminate.tags.eqs import Eq
from disseminate.dependency_manager import DependencyManager
from disseminate.renderers import process_context_template
from disseminate.ast import process_ast, process_paragraphs
from disseminate import SourcePath, TargetPath


def test_inline_equation(tmpdir, context_cls):
    """Test the tex rendering of simple inline equations."""

    # Setup the test paths
    project_root = SourcePath(project_root=tmpdir.join('src'))
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')
    target_root = TargetPath(target_root=tmpdir)
    project_root.mkdir()

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'project_root': SourcePath,
                                    'target_root': TargetPath,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(dependency_manager=dep_manager,
                          src_filepath=src_filepath,
                          project_root=project_root,
                          target_root=target_root,
                          paths=[])
    process_context_template(context)  # add the 'equation_renderer' entry

    # Example 1 - simple inline equation
    eq1 = Eq(name='eq', content='y=x', attributes=tuple(), context=context)
    assert eq1.tex == "\\ensuremath{y=x}"

    # Example 2 - nested inline equation with subtag as content
    eq2 = Eq(name='eq', content=eq1, attributes=tuple(), context=context)
    assert eq2.tex == "\\ensuremath{y=x}"

    # Example 3 - nested inline equation with subtag as list
    eq3 = Eq(name='eq', content=['test is my ', eq2], attributes=tuple(),
             context=context)
    assert eq3.tex == "\\ensuremath{test is my y=x}"

    # Example 4 - a bold equation
    eq4 = Eq(name='eq', content="y=x", attributes=('bold',), context=context)
    assert eq4.tex == "\\ensuremath{\\boldsymbol{y=x}}"

    # Example 5 - an equation with a bold equation subtag
    eq5 = Eq(name='eq', content=eq4, attributes=tuple(), context=context)
    assert eq5.tex == "\\ensuremath{\\boldsymbol{y=x}}"

    # Example 6 - an equation with a  bold equation subtag in a list
    eq6 = Eq(name='eq', content=['this is my ', eq4], attributes=tuple(),
             context=context)
    assert eq6.tex == "\\ensuremath{this is my \\boldsymbol{y=x}}"

    # Example 7 - a bold equation with an equation subtag in a list
    eq7 = Eq(name='eq', content=['this is my ', eq1], attributes=('bold',),
             context=context)
    assert eq7.tex == "\\ensuremath{\\boldsymbol{this is my y=x}}"


def test_block_equation(tmpdir, context_cls):
    """Test the tex rendering of a simple block equations."""

    # Setup the test paths
    project_root = SourcePath(project_root=tmpdir.join('src'))
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')
    target_root = TargetPath(target_root=tmpdir)
    project_root.mkdir()

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)
    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'project_root': SourcePath,
                                    'target_root': TargetPath,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(dependency_manager=dep_manager,
                          src_filepath=src_filepath,
                          project_root=project_root,
                          target_root=target_root,
                          paths=[])
    process_context_template(context)  # add the 'equation_renderer' entry

    # Example 1 - simple block equation
    eq1 = Eq(name='eq', content='y=x', attributes=tuple(), context=context,
             block_equation=True)
    assert eq1.tex == '\\begin{align*} %\ny=x\n\\end{align*}'

    # Example 2 - simple block equation with alternative environment
    eq2 = Eq(name='eq', content='y=x', attributes=(('env', 'alignat*'),),
             context=context, block_equation=True)
    assert eq2.tex == '\\begin{alignat*} %\ny=x\n\\end{alignat*}'

    # Example 3 - simple block equation with alternative environment and
    # positional arguments
    eq3 = Eq(name='eq', content='y=x', attributes=(('env', 'alignat*'), '3'),
             context=context, block_equation=True)
    assert eq3.tex == '\\begin{alignat*}{3} %\ny=x\n\\end{alignat*}'


# html targets

def test_simple_inline_equation_html(tmpdir, context_cls):
    """Test the rendering of simple inline equations for html."""

    # Setup the test paths
    project_root = SourcePath(project_root=tmpdir.join('src'))
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')
    target_root = TargetPath(target_root=tmpdir)
    project_root.mkdir()

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)
    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'project_root': SourcePath,
                                    'target_root': TargetPath,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(dependency_manager=dep_manager,
                          src_filepath=src_filepath,
                          project_root=project_root,
                          target_root=target_root,
                          paths=[])
    process_context_template(context)  # add the 'equation_renderer' entry

    # Setup the equation tag
    eq = Eq(name='eq', content='y = x', attributes=tuple(), context=context)

    # Check the paths. These are stored by the parent Img tag in the
    # 'src_filepath' attribute
    assert eq.img_filepath == SourcePath(project_root=dep_manager.cache_path,
                                         subpath='media/test_963ee5ea93.tex')

    # Create a root tag and render the html
    root = Tag(name='root', content=["This is my test", eq, "equation"],
               attributes=tuple(), context=context)

    # get the root tag
    root_html = root.html

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">This is my test'
    root_end = 'equation</span>\n'

    # Remove the root tag
    root_html = root_html[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert (root_html ==
            '<img class="eq" src="/html/media/test_963ee5ea93.svg"/>')


# tex targets

def test_simple_inline_equation_tex(tmpdir, context_cls):
    """Test the rendering of simple inline equations for tex."""

    # Setup the test paths
    project_root = SourcePath(project_root=tmpdir.join('src'))
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')
    target_root = TargetPath(target_root=tmpdir)
    project_root.mkdir()

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)
    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'project_root': SourcePath,
                                    'target_root': TargetPath,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(dependency_manager=dep_manager,
                          src_filepath=src_filepath,
                          project_root=project_root,
                          target_root=target_root,
                          paths=[])
    process_context_template(context)  # add the 'equation_renderer' entry

    # Setup the equation tag
    eq = Eq(name='eq', content='y = x', attributes=tuple(), context=context)

    assert eq.tex == "\\ensuremath{y = x}"


def test_block_equation_tex(tmpdir, context_cls):
    """Test the rendering of block equations for tex."""

    # Setup the test paths
    project_root = SourcePath(project_root=tmpdir.join('src'))
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')
    target_root = TargetPath(target_root=tmpdir)
    project_root.mkdir()

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)
    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'project_root': SourcePath,
                                    'target_root': TargetPath,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(dependency_manager=dep_manager,
                          src_filepath=src_filepath,
                          project_root=project_root,
                          target_root=target_root,
                          paths=[])
    process_context_template(context)  # add the 'equation_renderer' entry

    # Test markup
    test = """
    @eq[env=align*]{
    y &= x + b \\
    &= x + a
    }
    """

    root = process_ast(test, context=context)
    assert root.tex == ('\n    \\begin{align*} %\n'
                        'y &= x + b \\\n'
                        '    &= x + a\n'
                        '\\end{align*}\n    ')

    root = process_paragraphs(root, context=context)

    assert root.tex == ('\n\n    \\begin{align*} %\n'
                        'y &= x + b \\\n'
                        '    &= x + a\n'
                        '\\end{align*}\n    \n')
