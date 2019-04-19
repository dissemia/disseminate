"""Test the text formatting tags."""
from disseminate.tags import Tag
from disseminate.tags.text import P


def test_tag_text_paragraph(context_cls):
    """Test the formatting of paragraph tags."""

    context = context_cls()

    p = P(name='p', content='content', attributes='', context=context)
    assert str(p.html) == '<p>content</p>\n'
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
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        root = Tag(name='root', content=src, attributes='', context=context)
        assert root.content.html == html

    markups = {'@symbol{alpha}': '&alpha;\n',
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        root = Tag(name='root', content=src, attributes='', context=context)
        assert root.content.html == html


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
