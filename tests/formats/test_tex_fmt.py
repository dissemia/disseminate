"""
Tests for tex formatting functions for tags.
"""
import pytest

from disseminate.formats import tex_env, tex_cmd, TexFormatError


def test_tag_tex_environment(attributes_cls):
    """Tests the formatting of tex environments."""

    # 1. Test a basic equation with a required argument

    # A required argument is missing; raise an error
    with pytest.raises(TexFormatError):
        tex_env('alignat*', '', formatted_content='y=x')

    # Place the parameter
    key = ('\n'
           '\\begin{alignat*}{3}\n'
           'y=x\n'
           '\\end{alignat*}\n')
    assert (tex_env('alignat*', attributes_cls('3'), formatted_content='y=x') ==
            key)

    # 2. Test an environment with optional arguments
    key = ('\n'
           '\\begin{enumerate}\n'
           '\\item 1\n'
           '\\end{enumerate}\n')
    return_str = tex_env('enumerate', attributes_cls(),
                         formatted_content='\\item 1')
    assert return_str == key

    key = ('\n'
           '\\begin{enumerate}[(a)]\n'
           '\\item 1\n'
           '\\end{enumerate}\n')
    return_str = tex_env('enumerate', attributes_cls('(a)'),
                         formatted_content='\\item 1')
    assert return_str == key

    key = ('\n'
           '\\begin{enumerate}[label=(\\roman*)]\n'
           '\\item 1\n'
           '\\end{enumerate}\n')
    return_str = tex_env('enumerate',
                         attributes_cls('label=(\\roman*)'),
                         formatted_content='\\item 1')
    assert return_str == key


def test_tag_tex_command(attributes_cls):
    """Tests the formatting of tex environments."""

    # 1. Try a non-allowed command
    with pytest.raises(TexFormatError):
        tex_cmd('notchapter', '', 'My Chapter')

    # 2. Try textbf, textit
    assert (tex_cmd('textbf', '', 'bold') ==
            '\\textbf{bold}')
    assert (tex_cmd('textit', '', 'italics') ==
            '\\textit{italics}')

    # 3. Try document sections
    assert (tex_cmd('part', '', 'My Part') ==
            '\\part{My Part}')
    assert (tex_cmd('chapter', '', 'My Chapter') ==
            '\\chapter{My Chapter}')
    assert (tex_cmd('section', '', 'My Section') ==
            '\\section{My Section}')
    assert (tex_cmd('subsection', '', 'My Subsection') ==
            '\\subsection{My Subsection}')
    assert (tex_cmd('paragraph', '', 'My Paragraph') ==
            '\\paragraph{My Paragraph}')
    assert (tex_cmd('subparagraph', '', 'Subparagraph') ==
            '\\subparagraph{Subparagraph}')

    # 3. Try document sections (starred version)
    assert (tex_cmd('part*', '', 'My Part') ==
            '\\part*{My Part}')
    assert (tex_cmd('chapter*', '', 'My Chapter') ==
            '\\chapter*{My Chapter}')
    assert (tex_cmd('section*', '', 'My Section') ==
            '\\section*{My Section}')
    assert (tex_cmd('subsection*', '', 'My Subsection') ==
            '\\subsection*{My Subsection}')

    # 5. Try maketitle, title and author
    assert (tex_cmd('maketitle') ==
            '\\maketitle')
    assert (tex_cmd('title', '', 'My Title') ==
            '\\title{My Title}')
    assert (tex_cmd('author', '', 'author') ==
            '\\author{author}')
    assert (tex_cmd('today') ==
            '\\today')

    # 6. setcounter
    assert (tex_cmd('setcounter', attributes_cls('counter 3')) ==
            '\\setcounter{counter}{3}')
