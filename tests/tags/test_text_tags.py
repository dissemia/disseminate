"""Test the text formatting tags."""
from lxml.html import tostring

from disseminate.ast import process_ast
from disseminate.tags.text import P


def test_html():
    """Test the text formatting tags into html."""

    markups = {'@b{bold}': '<strong>bold</strong>',
               '@i{italics}': '<i>italics</i>',
               '@sup{superscript}': '<sup>superscript</sup>',
               '@sub{subscript}': '<sub>subscript</sub>',
               }

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">\n  '
    root_end = '\n</span>\n'

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        root = process_ast(src)
        # Remove the root tag
        root_html = root.html[len(root_start):]  # strip the start
        root_html = root_html[:(len(root_html) - len(root_end))]  # strip end
        assert root_html == html

    markups = {'@symbol{alpha}': '&alpha;',
               }

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">'
    root_end = '</span>\n'

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        root = process_ast(src)
        # Remove the root tag
        root_html = root.html[len(root_start):]  # strip the start
        root_html = root_html[:(len(root_html) - len(root_end))]  # strip end
        assert root_html == html


def test_tex():
    """Test the text formatting tags in tex."""

    markups = {'@b{bold}': '\\textbf{bold}',
               '@i{italics}': '\\textit{italics}',
               '@sup{superscript}': '\\ensuremath{^{superscript}}',
               '@sub{subscript}': '\\ensuremath{_{subscript}}',
               '@symbol{alpha}': '\\ensuremath{\\alpha}',
               }

    # Generate a tag for each and compare the generated tex to the answer key
    for src, tex in markups.items():
        root = process_ast(src)

        # Remove the root tag
        root_tex = root.tex
        assert root_tex == tex


def test_paragraph():
    """Test the formatting of paragraph tags."""

    p = P(name='p', content='content', attributes=(), context=dict())
    assert str(p.html) == '<p>content</p>\n'
    assert p.tex == '\ncontent\n'
    assert p.default == 'content'


def test_verbatim():
    """Test the verbatim tags."""

    # Test a verb tag that includes a tag
    test = "@v{@bold{bolded}}"
    root = process_ast(test)
    verb = root.content

    # Match targets
    assert verb.default == "@bold{bolded}"
    assert tostring(verb.html_fmt(level=2)) == b'<code>@bold{bolded}</code>'
    assert verb.tex == "\\verb|@bold{bolded}|"

    # Test a verbatim block
    test = "@verbatim{@bold{bolded}}"
    root = process_ast(test)
    verb = root.content

    # Match targets
    assert verb.default == "@bold{bolded}"
    assert tostring(verb.html_fmt(level=2)) == (b'<code class="block">'
                                                b'@bold{bolded}'
                                                b'</code>')
    assert verb.tex == ("\n\\begin{verbatim}\n"
                        "@bold{bolded}\\end{verbatim}\n")
