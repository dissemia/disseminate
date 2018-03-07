"""
Tags for headings
"""
from disseminate.ast import process_ast


def test_html():
    """Tests the conversion of heading tags to html."""

    markups = {'@section{Section 1}': '<h2>Section 1</h2>',
               '@subsection{Section 2}': '<h3>Section 2</h3>',
               '@subsubsection{Section 3}': '<h4>Section 3</h4>',
               '@h1{Section 1}': '<h1>Section 1</h1>',
               '@h2{Section 2}': '<h2>Section 2</h2>',
               '@h3{Section 3}': '<h3>Section 3</h3>',
               '@h4{Section 4}': '<h4>Section 4</h4>',
               }

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">\n  '
    root_end = '\n</span>\n'

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        root = process_ast(src)

        # Remove the root tag
        root_html = root.html()[len(root_start):]  # strip the start
        root_html = root_html[:(len(root_html) - len(root_end))]  # strip end
        assert root_html == html


def test_tex():
    """Tests the conversion of headings tags to tex."""

    markups = {'@section{Section 1}': '\n\section{Section 1}\n\n',
               '@subsection{Section 2}': '\n\subsection{Section 2}\n\n',
               '@subsubsection{Section 3}': '\n\subsubsection{Section 3}\n\n',
               '@h2{Section 2}': '\n\section{Section 2}\n\n',
               '@h3{Section 3}': '\n\subsection{Section 3}\n\n',
               '@h4{Section 4}': '\n\subsubsection{Section 4}\n\n',
               '@h5{Section 5}': '\paragraph{Section 5}',
               }

    # The following root tags have to be stripped for the html strings
    root_start = ''
    root_end = ''

    # Generate a tag for each and compare the generated html to the answer key
    for src, tex in markups.items():
        root = process_ast(src)

        # Remove the root tag
        root_tex = root.tex()[len(root_start):]  # strip the start
        root_tex = root_tex[:(len(root_tex) - len(root_end))]  # strip end
        assert root_tex == tex
