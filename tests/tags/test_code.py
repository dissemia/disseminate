"""
Test the @code tag
"""
from disseminate.tags import Tag


def test_tag_code_sources(doc):
    """Test the @code tag with code fragments or files."""
    context = doc.context

    # 1. Setup a code tag with a specified lexer
    src = "@code[python]{print('test')}"
    root = Tag(name='root', content=src, attributes='', context=context)

    # Check the @code tag
    code = root.content
    assert code.name == 'code'
    assert code.content == "print('test')"

    # 2. Test a file
    src = "@code[python]{tests/tags/code_example1/test.py}"
    root = Tag(name='root', content=src, attributes='', context=context)

    # Check the @code tag
    code = root.content
    assert code.name == 'code'
    assert code.content == ("#!/usr/bin/python\n"
                            "print('This is my file!')\n")


def test_tag_code_lexer(doc):
    """Test the identification of the lexer for the code tag."""
    context = doc.context

    # 1. Setup a code tag with a specified lexer
    src = "@code[python]{print('test')}"
    root = Tag(name='root', content=src, attributes='', context=context)

    # Check the @code tag
    code = root.content
    assert code.name == 'code'
    assert 'python' in code.attributes
    assert code.lexer.name == 'Python'

    # 2. Setup a code tag without a specified lexer
    src = """@code{#!/usr/bin/python
    print('test')}"""
    root = Tag(name='root', content=src, attributes='', context=context)

    # Check the @code tag
    code = root.content
    assert code.name == 'code'
    assert code.lexer.name == 'Python'


def test_tag_code_paragraphs(doc):
    """Test the @code tag with paragraphs."""
    # Setup the context
    context = doc.context
    context['process_paragraphs'] = 'root'

    # 1. Setup a code tag with a specified lexer
    src = """This is my code.
    
    @code[python]{print('test')}
    
    This is my @code{inline} code.
    """
    root = Tag(name='root', content=src, attributes='', context=context)

    # Check the @code tag
    assert root.content[0].name == 'p'
    assert root.content[0].content == 'This is my code.'

    assert root.content[1].name == 'p'
    assert root.content[1].content.name == 'code'
    assert root.content[1].content.paragraph_role == 'block'

    assert root.content[2].name == 'p'
    assert root.content[2].content[0] == "This is my "
    assert root.content[2].content[1].name == 'code'
    assert root.content[2].content[1].paragraph_role == 'inline'
    assert root.content[2].content[2] == ' code.\n    '


# Tests for html targets

def test_tag_code_html(doc):
    """Test the generation of html from @code tags"""
    context = doc.context

    # 1. Setup a code tag with a specified lexer
    src = "@code[python]{print('test')}"
    root = Tag(name='root', content=src, attributes='', context=context)

    # Check the @code tag
    code = root.content
    code.paragraph_role = 'block'
    assert code.html == ('<div class="code">'
                         '<div class="highlight block">'
                            '<pre>'
                                '<span></span>'
                                '<span class="k">print</span>'
                                '<span class="p">(</span>'
                                '<span class="s1">\'test\'</span>'
                                '<span class="p">)</span>\n'
                            '</pre>'
                         '</div>'
                         '</div>\n')
    assert root.html == ('<span class="root">'
                         '<div class="code">'
                         '<div class="highlight block">'
                            '<pre>'
                                '<span></span>'
                                '<span class="k">print</span>'
                                '<span class="p">(</span>'
                                '<span class="s1">\'test\'</span>'
                                '<span class="p">)</span>\n'
                            '</pre>'
                         '</div>'
                         '</div>'
                         '</span>\n')

    # Test inline
    code.paragraph_role = 'inline'
    assert code.html == '<code>print(\'test\')</code>\n'

    # 2. Test unsafe tags
    src = "@code[html]{<script></script}"
    root = Tag(name='root', content=src, attributes='', context=context)

    # Check the @code tag
    code = root.content
    code.paragraph_role = 'block'

    assert code.html == ('<div class="code">'
                         '<div class="highlight block">'
                           '<pre>'
                             '<span></span>'
                             '<span class="p">&lt;</span>'
                             '<span class="nt">script</span>'
                             '<span class="p">&gt;</span>'
                             '<span class="err">&lt;/script</span>\n'
                         '</pre></div></div>\n')
    assert root.html == ('<span class="root">'
                           '<div class="code">'
                           '<div class="highlight block">'
                             '<pre>'
                               '<span></span>'
                               '<span class="p">&lt;</span>'
                               '<span class="nt">script</span>'
                               '<span class="p">&gt;</span>'
                               '<span class="err">&lt;/script</span>\n'
                         '</pre></div></div></span>\n')

    # Test inline
    code.paragraph_role = 'inline'
    assert code.html == '<code>&lt;script&gt;&lt;/script</code>\n'


# Tests for tex targets

def test_tag_code_tex(doc):
    """Test the generation of tex from @code tags"""
    context = doc.context

    # 1. Setup a code tag with a specified lexer
    src = "@code[python]{print('test')}"
    root = Tag(name='root', content=src, attributes='', context=context)

    # Check the @code tag
    code = root.content
    code.paragraph_role = 'block'
    assert code.tex == ('\\begin{Verbatim}[commandchars=\\\\\\{\\}]\n'
                        '\\PY{k}{print}\\PY{p}{(}\\PY{l+s+s1}{\\PYZsq{}}'
                        '\\PY{l+s+s1}{test}\\PY{l+s+s1}{\\PYZsq{}}\\PY{p}{)}\n'
                        '\\end{Verbatim}\n')
    assert root.tex == ('\\begin{Verbatim}[commandchars=\\\\\\{\\}]\n'
                        '\\PY{k}{print}\\PY{p}{(}\\PY{l+s+s1}{\\PYZsq{}}'
                        '\\PY{l+s+s1}{test}\\PY{l+s+s1}{\\PYZsq{}}\\PY{p}{)}\n'
                        '\\end{Verbatim}\n')

    # Test inline
    code.paragraph_role = 'inline'
    assert code.tex == "\\verb|print('test')|"
    assert root.tex == "\\verb|print('test')|"
