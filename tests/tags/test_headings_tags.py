"""
Tags for headings
"""
from disseminate import Document
from disseminate.ast import process_ast
from disseminate.labels import LabelManager
from disseminate.utils.tests import strip_leading_space


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


def test_html_labels(tmpdir):
    """Tests the production of heading html with labels."""

    # Create a mock document
    tmpdir.join('src').mkdir()
    src_filepath = tmpdir.join('src').join('text.dm')

    src = """---
    targets: html
    ---"""
    src_filepath.write(strip_leading_space(src))

    doc = Document(str(src_filepath), str(tmpdir))

    # 1. Test with default labels

    markups = {
        '@section{Section 1}': '<h2 id="section:section-1">Section 1</h2>',
        '@subsection{Section 2}': '<h3 id="subsection:section-2">Section 2</h3>',
        '@subsubsection{Section 3}': '<h4 id="subsubsection:section-3">Section 3</h4>',
        '@h1{Section 1}': '<h1 id="chapter:section-1">Section 1</h1>',
        '@h2{Section 2}': '<h2 id="section:section-2">Section 2</h2>',
        '@h3{Section 3}': '<h3 id="subsection:section-3">Section 3</h3>',
        '@h4{Section 4}': '<h4 id="subsubsection:section-4">Section 4</h4>',
               }

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">\n  '
    root_end = '\n</span>\n'

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        doc.reset_contexts()
        doc.reset_labels()
        root = process_ast(src, context=doc.context)

        # Remove the root tag
        root_html = root.html()[len(root_start):]  # strip the start
        root_html = root_html[:(len(root_html) - len(root_end))]  # strip end
        assert root_html == html

    # 2. Test with 'nolabel' specified

    markups = {
        '@section[nolabel]{Section 1}': '<h2>Section 1</h2>',
        '@subsection[nolabel]{Section 2}': '<h3>Section 2</h3>',
        '@subsubsection[nolabel]{Section 3}': '<h4>Section 3</h4>',
        '@h1[nolabel]{Section 1}': '<h1>Section 1</h1>',
        '@h2[nolabel]{Section 2}': '<h2>Section 2</h2>',
        '@h3[nolabel]{Section 3}': '<h3>Section 3</h3>',
        '@h4[nolabel]{Section 4}': '<h4>Section 4</h4>',
    }

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        doc.reset_contexts()
        doc.reset_labels()
        root = process_ast(src, context=doc.context)

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


def test_tex_labels(tmpdir):
    """Tests the production of heading tex with labels."""

    # Create a mock document
    tmpdir.join('src').mkdir()
    src_filepath = tmpdir.join('src').join('text.dm')

    src = """---
    targets: html
    ---"""
    src_filepath.write(strip_leading_space(src))

    doc = Document(str(src_filepath), str(tmpdir))

    # 1. Test with default labels

    markups = {
        '@section{Section 1}': '\n\section{Section 1} \label{section:section-1}\n\n',
        '@subsection{Section 2}': '\n\subsection{Section 2} \label{subsection:section-2}\n\n',
        '@subsubsection{Section 3}': '\n\subsubsection{Section 3} \label{subsubsection:section-3}\n\n',
        '@h2{Section 2}': '\n\section{Section 2} \label{section:section-2}\n\n',
        '@h3{Section 3}': '\n\subsection{Section 3} \label{subsection:section-3}\n\n',
        '@h4{Section 4}': '\n\subsubsection{Section 4} \label{subsubsection:section-4}\n\n',
        '@h5{Section 5}': '\paragraph{Section 5}',
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, tex in markups.items():
        doc.reset_contexts()
        doc.reset_labels()
        root = process_ast(src, context=doc.context)

        assert root.tex() == tex

    # 2. Test with 'nolabel' specified

    markups = {
        '@section[nolabel]{Section 1}': '\n\section{Section 1}\n\n',
        '@subsection[nolabel]{Section 2}': '\n\subsection{Section 2}\n\n',
        '@subsubsection[nolabel]{Section 3}': '\n\subsubsection{Section 3}\n\n',
        '@h2[nolabel]{Section 2}': '\n\section{Section 2}\n\n',
        '@h3[nolabel]{Section 3}': '\n\subsection{Section 3}\n\n',
        '@h4[nolabel]{Section 4}': '\n\subsubsection{Section 4}\n\n',
        '@h5{Section 5}': '\paragraph{Section 5}',
    }

    # Generate a tag for each and compare the generated html to the answer key
    for src, tex in markups.items():
        doc.reset_contexts()
        doc.reset_labels()
        root = process_ast(src, context=doc.context)

        assert root.tex() == tex
