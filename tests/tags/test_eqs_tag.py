"""
Test the equation tags.
"""
import pytest

from disseminate.tags import Tag
from disseminate.formats import TexFormatError
from disseminate.tags.eqs import Eq
from disseminate.document.receivers import process_headers
from disseminate import SourcePath


def test_inline_equation(context):
    """Test the tex rendering of simple inline equations."""

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


def test_equation_typography(context):
    """Test the tex rendering of equations with text typography (i.e. it
    shouldn't be replaced)."""

    # Example 1 - simple equation
    eq1 = Eq(name='eq', content='y---x', attributes='', context=context)
    assert eq1.tex == "\\ensuremath{y---x}"


def test_block_equation(context):
    """Test the tex rendering of a simple block equations."""

    # 1. simple block equation
    eq1 = Eq(name='eq', content='y=x', attributes='', context=context,
             block_equation=True)

    assert eq1.tex == '\\begin{align*} %\ny=x\n\\end{align*}'

    # 2. simple block equation with alternative environment. The alignat*
    #    requires an integer parameter for the number of columns, so this
    #    show raise a TagError
    eq2 = Eq(name='eq', content='y=x', attributes='env=alignat*',
             context=context, block_equation=True)
    with pytest.raises(TexFormatError):
        eq2.tex

    # 3. simple block equation with alternative environment and
    #    positional arguments
    eq3 = Eq(name='eq', content='y=x', attributes='env=alignat* 3',
             context=context, block_equation=True)
    assert eq3.tex == '\\begin{alignat*}{3} %\ny=x\n\\end{alignat*}'


def test_block_equation_paragraph(context):
    """Test the tex rendering of a simple block equations that are identified
    from paragraphs."""

    # 1. a simple block equation.
    context['process_paragraphs'] = ['root']  # process paragraphs for 'root'

    test1 = "\n\n@eq{y=x}\n\n"
    root = Tag(name='root', content=test1, attributes='', context=context)

    # The tag should be a 'root' wrapping a 'p', wrapping an 'eq'
    p = root.content
    eq = p.content

    assert p.name == 'p'
    assert eq.name == 'eq'
    assert eq.tex == ('\\begin{align*} %\n'
                      'y=x\n'
                      '\\end{align*}')
    assert p.tex == ('\\begin{align*} %\n'
                     'y=x\n'
                     '\\end{align*}')

    # 2. Two back-to-back equations
    test1 = "\n\n@eq{a=b}\n\n@eq{x=y}\n\n"
    root = Tag(name='root', content=test1, attributes='', context=context)

    assert root.tex == ('\\begin{align*} %\n'
                        'a=b\n'
                        '\\end{align*}\\begin{align*} %\n'
                        'x=y\n'
                        '\\end{align*}')

    # 3. a simple inline equation
    context['process_paragraphs'] = ['root']  # process paragraphs for 'root'
    test2 = "@eq{y=x}"
    root = Tag(name='root', content=test2, attributes='', context=context)
    eq = root.content

    assert eq.name == 'eq'
    assert eq.tex == '\\ensuremath{y=x}'


# html targets

def test_simple_inline_equation_html(context):
    """Test the rendering of simple inline equations for html."""

    # setup the context
    context['relative_links'] = False  # report absolute links

    # 1. Setup a basic equation tag
    eq = Eq(name='eq', content='y = x', attributes='', context=context)

    # Check the rendered tag and that the asy and svg files were properly
    # created
    html = eq.html
    assert html == '<img src="/html/media/eq_2df78554597f.svg" class="eq">\n'
    assert eq.html == html  # running twice should give same answer

    # Check the build
    build_env = context['environment']
    html_builder = context['builders']['.html']
    svg_builder = html_builder._parallel_builder.subbuilders[4]
    copy_builder = svg_builder.subbuilders[2]

    assert html_builder.build(complete=True) == 'done'
    target_filepath = (build_env.target_root / 'html' / 'media' /
                       'eq_2df78554597f.svg')
    assert target_filepath.exists()

    # 2. Test tag with disseminate formatting
    eq = Eq(name='eq', content='y = @termb{x}', attributes='',
            context=context)

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert (eq.html ==
            '<img src="/html/media/eq_9a3b5b06c002.svg" class="eq">\n')

    # Check the build
    assert html_builder.build(complete=True) == 'done'

    target_filepath = (build_env.target_root / 'html' / 'media' /
                       'eq_9a3b5b06c002.svg')
    assert target_filepath.exists()

    # Make sure the @termb has been converted
    tex = eq.tex
    assert '@termb' not in tex
    assert '\\ensuremath{y = \\boldsymbol{x}}' in tex

    # 3. Test tag with extra attributes
    eq = Eq(name='eq', content='y = @eq[env=alignat* 1]{x}', attributes='',
            context=context)

    # Make sure the tag has been converted
    tex = eq.tex
    assert '@termb' not in tex
    assert '\\ensuremath{y = x}' in tex

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert (eq.html ==
            '<img src="/html/media/eq_2df78554597f.svg" class="eq">\n')


def test_block_equation_html(context):
    """Test the rendering of block equations for tex to ensure that the tex
    text is well-formed."""
    env = context['environment']
    target_root = env.target_root

    # # 1. Test a simple markup example
    test = """
    @eq[env=align*]{
    y &= x + b \\
    &= x + a
    }
    """
    context['process_paragraphs'] = ['root']  # process paragraphs for 'root'
    root = Tag(name='root', content=test, attributes='', context=context)
    p = root.content
    eq = p.content[1]

    assert p.name == 'p'
    assert eq.name == 'eq'

    # Check the rendered content, which is used in making the rendered image
    # for html
    key = ('\\begin{align*} %\n'
           'y &= x + b \\\n'
           '    &= x + a\n'
           '\\end{align*}')
    assert eq.tex == key

    # Check the image infilepath and that the contents are in the file
    assert (eq.html ==
            '<img src="media/eq_77ef2ee610b5.svg" class="eq blockeq">\n')

    # Check the build
    build_env = context['environment']
    html_builder = context['builders']['.html']
    assert html_builder.build(complete=True) == 'done'
    assert (target_root / 'html' / 'media' / 'eq_77ef2ee610b5.svg').exists()

    # 2. Test a markup example with a more complicated environment
    test = """
    @eq[env=alignat* 3]{
    y &= x + b \\
    &= x + a
    }
    """
    context['process_paragraphs'] = ['root']  # process paragraphs for 'root'
    root = Tag(name='root', content=test, attributes='', context=context)
    p = root.content
    eq = p.content[1]

    assert p.name == 'p'
    assert eq.name == 'eq'

    # Check the rendered content, which is used in making the rendered image
    # for html
    key = ('\\begin{alignat*}{3} %\n'
           'y &= x + b \\\n'
           '    &= x + a\n'
           '\\end{alignat*}')
    assert eq.tex == key

    # Check the image infilepath and that the contents are in the file
    assert (eq.html ==
            '<img src="media/eq_205c2f7bc8a1.svg" class="eq blockeq">\n')

    # Check the build
    assert html_builder.build(complete=True) == 'done'
    assert (target_root / 'html' / 'media' / 'eq_205c2f7bc8a1.svg').exists()

    # 3. Test an block equation in a paragraph in which the block equation
    #    hasn't been specified.
    test = """
    @eq{
    y &= x + b \\
    &= x + a
    }
    """
    context['process_paragraphs'] = ['root']  # process paragraphs for 'root'
    root = Tag(name='root', content=test, attributes='', context=context)
    p = root.content
    eq = p.content[1]

    assert p.name == 'p'
    assert eq.name == 'eq'
    assert eq.paragraph_role == 'block'

    # Check the rendered content, which is used in making the rendered image
    # for html
    key = ('\\begin{align*} %\n'
           'y &= x + b \\\n'
           '    &= x + a\n'
           '\\end{align*}')
    assert eq.tex == key

    # Check the image infilepath and that the contents are in the file
    assert (eq.html ==
            '<img src="media/eq_005f59fdeca8.svg" class="eq blockeq">\n')

    # Check the build
    assert html_builder.build(complete=True) == 'done'
    assert (target_root / 'html' / 'media' / 'eq_005f59fdeca8.svg').exists()


def test_equation_relative_absolute_links(context):
    """Test rendered equation images with absolute and relative links."""

    # setup the context
    context['relative_links'] = False  # report absolute links

    # 1. Setup a basic equation tag
    eq = Eq(name='eq', content='y = x', attributes='', context=context)

    # Check that the returned html uses absolute links
    assert (eq.html ==
            '<img src="/html/media/eq_2df78554597f.svg" class="eq">\n')

    # Switch to relative links
    context['relative_links'] = True
    assert (eq.html ==
            '<img src="media/eq_2df78554597f.svg" class="eq">\n')


# tex targets

def test_simple_inline_equation_tex(context):
    """Test the rendering of simple inline equations for tex."""

    # Setup the equation tag
    eq = Eq(name='eq', content='y = x', attributes=tuple(), context=context)

    assert eq.tex == "\\ensuremath{y = x}"


def test_block_equation_tex(context):
    """Test the rendering of block equations for tex to ensure that the tex
    text is well-formed."""

    # 1. A basic block equation
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

    # 2. A custom block equation with a different environment
    test = """
    @eq[env=alignat* 2]{
    y &= x + b \\
    &= x + a
    }
    """
    context['process_paragraphs'] = ['root']  # process paragraphs for 'root'
    root = Tag(name='root', content=test, attributes='', context=context)
    p = root.content

    assert p.name == 'p'
    assert p.tex == ('\n\n    \\begin{alignat*}{2} %\n'
                     'y &= x + b \\\n'
                     '    &= x + a\n'
                     '\\end{alignat*}\n    \n')


# Multiple targets

def test_block_equation_multiple_targets(context):
    """Test the rendering of block equations with multiple targets"""

    # Setup the context
    context['relative_links'] = False  # report absolute links
    context['process_paragraphs'] = ['root']  # process paragraphs for 'root'
    context['targets'] = ['html', 'tex']

    # 1. A basic block equation
    test = """
    @eq[env=align*]{
    y &= x + b \\
    &= x + a
    }
    """

    root = Tag(name='root', content=test, attributes='', context=context)
    p = root.content

    key = ('\\begin{align*} %\n'
           'y &= x + b \\\n'
           '    &= x + a\n'
           '\\end{align*}')
    assert p.name == 'p'

    # Check the tex target
    assert p.tex == ('\n\n    ' + key + '\n    \n')

    # Check the html target
    eq = p.content[1]
    assert (eq.html ==
            '<img src="/html/media/eq_77ef2ee610b5.svg" class="eq blockeq">\n')

    # 2. Test a block equation with a custom math environment
    test = """
    @eq[env=alignat* 2]{
    y &= x + b \\
    &= x + a
    }
    """

    root = Tag(name='root', content=test, attributes='', context=context)
    p = root.content

    key = ('\\begin{alignat*}{2} %\n'
           'y &= x + b \\\n'
           '    &= x + a\n'
           '\\end{alignat*}')
    assert p.name == 'p'

    # Check the html target
    eq = p.content[1]
    assert p.html == ('<p>\n'
                      '    <img src="/html/media/eq_2d57a64d69a5.svg" '
                      'class="eq blockeq">\n'
                      '    </p>\n')
    # Check the tex target
    assert p.tex == ('\n\n    ' + key + '\n    \n')
