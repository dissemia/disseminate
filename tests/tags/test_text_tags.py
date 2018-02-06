"""Test the text formatting tags."""
from disseminate.ast import process_ast


def test_html():
    """Test the text formatting tags into html."""

    markups = {'@b{bold}': '<strong>bold</strong>',
               '@i{italics}': '<i>italics</i>',
               '@sup{superscript}': '<sup>superscript</sup>',
               '@sub{subscript}': '<sub>subscript</sub>',
               '@greek{alpha}': '&alpha;',
               }

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">'
    root_end = '</span>\n'

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        root = process_ast(src)

        # Remove the root tag
        root_html = root.html()[len(root_start):]  # strip the start
        root_html = root_html[:(len(root_html) - len(root_end))]  # strip end
        assert root_html == html


def test_tex():
    """Test the text formatting tags in tex."""

    markups = {'@b{bold}': '\\textbf{bold}',
               '@i{italics}': '\\textit{italics}',
               '@sup{superscript}': '\\ensuremath{^{superscript}}',
               '@sub{subscript}': '\\ensuremath{_{subscript}}',
               '@greek{alpha}': '\\ensuremath{\\alpha}',
               }

    # Generate a tag for each and compare the generated tex to the answer key
    for src, tex in markups.items():
        root = process_ast(src)

        # Remove the root tag
        root_tex = root.tex()
        assert root_tex == tex
