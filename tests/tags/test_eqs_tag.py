"""
Test the equation tags.
"""
from disseminate.tags import Tag
from disseminate.tags.eqs import Eq
from disseminate.dependency_manager import DependencyManager
from disseminate.renderers import ProcessContextTemplate
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

    # Setup the context processor
    processor = ProcessContextTemplate()
    processor(context)  # add the 'equation_renderer' entry

    # Example 1 - simple inline equation
    eq1 = Eq(name='eq', content='y=x', attributes='', context=context)
    assert eq1.tex == "\\ensuremath{y=x}"

    # Example 2 - nested inline equation with subtag as content
    eq2 = Eq(name='eq', content=eq1, attributes='', context=context)
    assert eq2.tex == "\\ensuremath{y=x}"

    # Example 3 - nested inline equation with subtag as list
    eq3 = Eq(name='eq', content=['test is my ', eq2], attributes='',
             context=context)
    assert eq3.tex == "\\ensuremath{test is my y=x}"

    # Example 4 - a bold equation
    eq4 = Eq(name='eq', content="y=x", attributes='bold', context=context)
    assert eq4.tex == "\\ensuremath{\\boldsymbol{y=x}}"

    # Example 5 - an equation with a bold equation subtag
    eq5 = Eq(name='eq', content=eq4, attributes='', context=context)
    assert eq5.tex == "\\ensuremath{\\boldsymbol{y=x}}"

    # Example 6 - an equation with a  bold equation subtag in a list
    eq6 = Eq(name='eq', content=['this is my ', eq4], attributes='',
             context=context)
    assert eq6.tex == "\\ensuremath{this is my \\boldsymbol{y=x}}"

    # Example 7 - a bold equation with an equation subtag in a list
    eq7 = Eq(name='eq', content=['this is my ', eq1], attributes='bold',
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

    # Setup the context processor
    processor = ProcessContextTemplate()
    processor(context)  # add the 'equation_renderer' entry

    # Example 1 - simple block equation
    eq1 = Eq(name='eq', content='y=x', attributes='', context=context,
             block_equation=True)
    assert eq1.tex == '\\begin{align*} %\ny=x\n\\end{align*}'

    # Example 2 - simple block equation with alternative environment
    eq2 = Eq(name='eq', content='y=x', attributes='env=alignat*',
             context=context, block_equation=True)
    assert eq2.tex == '\\begin{alignat*} %\ny=x\n\\end{alignat*}'

    # Example 3 - simple block equation with alternative environment and
    # positional arguments
    eq3 = Eq(name='eq', content='y=x', attributes='env=alignat* 3',
             context=context, block_equation=True)
    assert eq3.tex == '\\begin{alignat*}{3} %\ny=x\n\\end{alignat*}'


def test_block_equation_paragraph(tmpdir, context_cls):
    """Test the tex rendering of a simple block equations that are identified
    from paragraphs."""

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

    # Setup the context processor
    processor = ProcessContextTemplate()
    processor(context)  # add the 'equation_renderer' entry

    # Example 1 - simple block equation.
    context['process_paragraphs'] = ['root']  # process paragraphs for 'root'

    test1 = "\n\n@eq{y=x}\n\n"
    root = Tag(name='root', content=test1, attributes='', context=context)

    # The tag should be a 'root' wrapping a 'p', wrapping an 'eq'
    print(root.content)
    p = root.content
    eq = p.content

    assert p.name == 'p'
    assert eq.name == 'eq'
    assert p.tex == ('\n'
                       '\\begin{align*} %\n'
                       'y=x\n'
                       '\\end{align*}\n')

    # Example 2 - a simple inline equation
    context['process_paragraphs'] = ['root']  # process paragraphs for 'root'
    test2 = "@eq{y=x}"
    root = Tag(name='root', content=test2, attributes='', context=context)
    eq = root.content

    assert eq.name == 'eq'
    assert eq.tex == '\\ensuremath{y=x}'


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

    # Setup the context processor
    processor = ProcessContextTemplate()
    processor(context)  # add the 'equation_renderer' entry

    # 1. Setup a basic equation tag
    eq = Eq(name='eq', content='y = x', attributes='', context=context)

    # Check the paths. These are stored by the parent Img tag in the
    # 'src_filepath' attribute
    assert eq.img_filepath == SourcePath(project_root=dep_manager.cache_path,
                                         subpath='media/test_963ee5ea93.tex')

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert (eq.html ==
            '<img class="eq" src="/html/media/test_963ee5ea93_crop.svg"/>\n')

    # 2. Test tag with disseminate formatting
    eq = Eq(name='eq', content='y = @termb{x}', attributes='',
            context=context)

    # Check the paths. These are stored by the parent Img tag in the
    # 'src_filepath' attribute
    assert eq.img_filepath == SourcePath(project_root=dep_manager.cache_path,
                                         subpath='media/test_44f6509475.tex')

    # Make sure the @termb has been converted
    tex_file = eq.img_filepath.read_text()
    assert '@termb' not in tex_file
    assert '\\ensuremath{y = \\boldsymbol{x}}' in tex_file

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert (eq.html ==
            '<img class="eq" src="/html/media/test_44f6509475_crop.svg"/>\n')


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

    # Setup the context processor
    processor = ProcessContextTemplate()
    processor(context)  # add the 'equation_renderer' entry

    # Setup the equation tag
    eq = Eq(name='eq', content='y = x', attributes=tuple(), context=context)

    assert eq.tex == "\\ensuremath{y = x}"


def test_block_equation_tex(tmpdir, context_cls):
    """Test the rendering of block equations for tex with process_ast and
    process_paragraphs to ensure that the tex text is well-formed."""

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

    # Setup the context processor
    processor = ProcessContextTemplate()
    processor(context)  # add the 'equation_renderer' entry

    # Test markup
    test = """
    @eq[env=align*]{
    y &= x + b \\
    &= x + a
    }
    """
    context['process_paragraphs'] = ['root']  # process paragraphs for 'root'
    root = Tag(name='root', content=test, attributes='', context=context)
    p = root.content

    assert p.name == 'p'
    assert p.tex == ('\n\n    \\begin{align*} %\n'
                     'y &= x + b \\\n'
                     '    &= x + a\n'
                     '\\end{align*}\n    \n')
