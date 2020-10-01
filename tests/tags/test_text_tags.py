"""Test the text formatting tags."""
from disseminate.tags import Tag
from disseminate.tags.text import P


def test_tag_text_body(context_cls):
    """Test the body tag."""
    context = context_cls()

    # Test a body tag
    root = Tag(name='root', content="@body{My body!}", attributes='',
               context=context)
    body = root.content

    assert body.html == '<div class="body">My body!</div>\n'
    assert body.xhtml == '<div class="body">My body!</div>\n'
    assert body.tex == 'My body!'
    assert body.default == 'My body!'


def test_tag_text_paragraph(context_cls):
    """Test the formatting of paragraph tags."""

    context = context_cls()

    p = P(name='p', content='content', attributes='', context=context)
    assert p.html == '<p>content</p>\n'
    assert p.xhtml == '<p>content</p>\n'
    assert p.tex == '\ncontent\n'
    assert p.default == 'content'


def test_tag_text_verbatim(context_cls):
    """Test the verbatim tags."""

    context = context_cls()

    # Test a verb tag that includes a tag
    root = Tag(name='root', content="@v{@bold{bolded}}", attributes='',
               context=context)
    verb = root.content

    # Match targets
    assert verb.default == "@bold{bolded}"
    assert verb.tex == "\\verb|@bold{bolded}|"

    # Test a verbatim block
    root = Tag(name='root', content="@verbatim{@bold{bolded}}", attributes='',
               context=context)
    verb = root.content

    # Match targets
    assert verb.default == "@bold{bolded}"
    assert verb.tex == ("\n"
                        "\\begin{verbatim}\n"
                        "@bold{bolded}\n"
                        "\\end{verbatim}\n")


# html targets

def test_tag_text_html(context_cls):
    """Test the text formatting tags into html."""

    context = context_cls()

    markups = {'@b{bold}': '<strong>bold</strong>\n',
               '@i{italics}': '<i>italics</i>\n',
               '@sup{superscript}': '<sup>superscript</sup>\n',
               '@sub{subscript}': '<sub>subscript</sub>\n',
               '@supsub{sup && sub}': ('<span class="supsub">sup<br>'
                                       'sub</span>\n'),
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        root = Tag(name='root', content=src, attributes='', context=context)
        tag = root.content
        assert tag.html == html

    markups = {'@symbol{alpha}': '&alpha;\n',
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        root = Tag(name='root', content=src, attributes='', context=context)
        assert root.content.html == html


# xhtml targets

def test_tag_text_xhtml(context_cls, is_xml):
    """Test the text formatting tags into xhtml."""

    context = context_cls()

    markups = {'@b{bold}': '<strong>bold</strong>\n',
               '@i{italics}': '<i>italics</i>\n',
               '@sup{superscript}': '<sup>superscript</sup>\n',
               '@sub{subscript}': '<sub>subscript</sub>\n',
               '@supsub{sup && sub}': ('<span class="supsub">sup<br/>'
                                       'sub</span>\n'),
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, xhtml in markups.items():
        root = Tag(name='root', content=src, attributes='', context=context)
        tag = root.content
        assert tag.xhtml == xhtml
        assert is_xml(tag.xhtml)

    markups = {'@symbol{alpha}': '&alpha;\n',
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, xhtml in markups.items():
        root = Tag(name='root', content=src, attributes='', context=context)
        assert root.content.xhtml == xhtml
        assert is_xml(root.content.xhtml)


# tex targets

def test_tag_text_tex(context_cls):
    """Test the text formatting tags in tex."""

    context = context_cls()

    markups = {'@b{bold}': '\\textbf{bold}',
               '@i{italics}': '\\textit{italics}',
               '@sup{superscript}': '\\ensuremath{^{superscript}}',
               '@sub{subscript}': '\\ensuremath{_{subscript}}',
               '@symbol{alpha}': '\\ensuremath{\\alpha}',
               }

    # Generate a tag for each and compare the generated tex to the answer key
    for src, tex in markups.items():
        root = Tag(name='root', content=src, attributes='', context=context)

        # Remove the root tag
        assert root.content.tex == tex
