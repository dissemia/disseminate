"""
Test the @code tag
"""
from disseminate.tags import Tag


def test_tag_code_sources(context):
    """Test the @code tag with code fragments or files."""

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


def test_tag_code_lexer(context):
    """Test the identification of the lexer for the code tag."""

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


def test_tag_code_paragraphs(context):
    """Test the @code tag with paragraphs."""
    # Setup the context
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


def test_tag_code_specific(context):
    """Test code tags for specific languages"""

    for language in ('python', 'html', 'ruby', 'java', 'javascript'):
        src1 = "@code[{}]".format(language) + "{test}"
        root1 = Tag(name='root', content=src1, attributes='', context=context)
        code1 = root1.content

        src2 = "@" + language + "{test}"
        root2 = Tag(name='root', content=src2, attributes='', context=context)
        code2 = root2.content

        assert code1.html == code2.html
        assert code1.tex == code2.tex


# Tests for tex targets

def test_tag_code_tex(context):
    """Test the generation of tex from @code tags"""

    # 1. Setup a code tag with a specified lexer
    src = "@code[python]{print('test')}"
    root = Tag(name='root', content=src, attributes='', context=context)

    # Check the @code tag
    code = root.content
    code.paragraph_role = 'block'
    assert code.tex == ('\\begin{Verbatim}[commandchars=\\\\\\{\\}]\n'
                        '\\PY{n+nb}{print}\\PY{p}{(}\\PY{l+s+s1}{\\PYZsq{}}'
                        '\\PY{l+s+s1}{test}\\PY{l+s+s1}{\\PYZsq{}}\\PY{p}{)}\n'
                        '\\end{Verbatim}\n')
    assert root.tex == ('\\begin{Verbatim}[commandchars=\\\\\\{\\}]\n'
                        '\\PY{n+nb}{print}\\PY{p}{(}\\PY{l+s+s1}{\\PYZsq{}}'
                        '\\PY{l+s+s1}{test}\\PY{l+s+s1}{\\PYZsq{}}\\PY{p}{)}\n'
                        '\\end{Verbatim}\n')

    # Test inline
    code.paragraph_role = 'inline'
    assert code.tex == "\\verb|print('test')|"
    assert root.tex == "\\verb|print('test')|"


# Tests for html targets

def test_tag_code_html(context):
    """Test the generation of html from @code tags"""

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
                         '<span class="nb">print</span>'
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
                         '<span class="nb">print</span>'
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
                         '<span class="o">&lt;</span>'
                         '<span class="err">/script</span>\n'
                         '</pre></div></div>\n')
    assert root.html == ('<span class="root">'
                         '<div class="code">'
                         '<div class="highlight block">'
                         '<pre>'
                         '<span></span>'
                         '<span class="p">&lt;</span>'
                         '<span class="nt">script</span>'
                         '<span class="p">&gt;</span>'
                         '<span class="o">&lt;</span>'
                         '<span class="err">/script</span>\n'
                         '</pre></div></div></span>\n')

    # Test inline
    code.paragraph_role = 'inline'
    assert code.html == '<code>&lt;script&gt;&lt;/script</code>\n'


# Tests for xhtml targets

def test_tag_code_xhtml(context, is_xml):
    """Test the generation of xhtml from @code tags"""

    # 1. Setup a code tag with a specified lexer
    src = "@code[python]{print('test')}"
    root = Tag(name='root', content=src, attributes='', context=context)

    # Check the @code tag
    code = root.content
    code.paragraph_role = 'block'
    assert code.xhtml == ('<div class="code">\n'
                          '  <div class="highlight block">\n'
                          '    <pre>'
                          '<span/>'
                          '<span class="nb">print</span>'
                          '<span class="p">(</span>'
                          '<span class="s1">\'test\'</span>'
                          '<span class="p">)</span>\n'
                          '</pre>\n'
                          '  </div>\n'
                          '</div>\n')
    assert is_xml(code.xhtml)

    assert root.xhtml == ('<span class="root">\n'
                          '  <div class="code">\n'
                          '    <div class="highlight block">\n'
                          '      <pre>'
                          '<span/>'
                          '<span class="nb">print</span>'
                          '<span class="p">(</span>'
                          '<span class="s1">\'test\'</span>'
                          '<span class="p">)</span>\n'
                          '</pre>\n'
                          '    </div>\n'
                          '  </div>\n'
                          '</span>\n')
    assert is_xml(root.xhtml)

    # Test inline
    code.paragraph_role = 'inline'
    assert code.html == '<code>print(\'test\')</code>\n'

    # 2. Test unsafe tags
    src = "@code[html]{<script></script}"
    root = Tag(name='root', content=src, attributes='', context=context)

    # Check the @code tag
    code = root.content
    code.paragraph_role = 'block'

    assert code.xhtml == ('<div class="code">\n'
                          '  <div class="highlight block">\n'
                          '    <pre>'
                          '<span/>'
                          '<span class="p">&lt;</span>'
                          '<span class="nt">script</span>'
                          '<span class="p">&gt;</span>'
                          '<span class="o">&lt;</span>'
                          '<span class="err">/script</span>\n'
                          '</pre>\n'
                          '  </div>\n'
                          '</div>\n')
    assert is_xml(code.xhtml)
    assert root.xhtml == ('<span class="root">\n'
                          '  <div class="code">\n'
                          '    <div class="highlight block">\n'
                          '      <pre>'
                          '<span/>'
                          '<span class="p">&lt;</span>'
                          '<span class="nt">script</span>'
                          '<span class="p">&gt;</span>'
                          '<span class="o">&lt;</span>'
                          '<span class="err">/script</span>\n'
                          '</pre>\n'
                          '    </div>\n'
                          '  </div>\n'
                          '</span>\n')

    # Test inline
    code.paragraph_role = 'inline'
    assert code.xhtml == '<code>&lt;script&gt;&lt;/script</code>\n'
    assert is_xml(code.xhtml)
