"""
Tags for headings
"""
from disseminate import Document
from disseminate.ast import process_ast
from disseminate.macros import replace_macros
from disseminate.tags.headings import Branch
from disseminate.utils.tests import strip_leading_space


def test_heading_labels(context_cls):
    """Test the setting and of heading identifiers and labels."""

    context = context_cls()

    # 1. Create branch headings without a doc_id and and content
    br1 = Branch(name='branch', content='', attributes=tuple(), context=context)
    assert br1.get_id() == 'br:1'
    assert br1.attributes == (('id', 'br:1'),)
    assert br1.get_attribute('id') == 'br:1'

    # 2. Create branch headings with a doc_id
    context.reset()
    context['doc_id'] = 'src/test.dm'
    br2 = Branch(name='branch', content='', attributes=tuple(), context=context)
    assert br2.get_id() == 'br:src-test-dm-1'
    assert br2.attributes == (('id', 'br:src-test-dm-1'),)
    assert br2.get_attribute('id') == 'br:src-test-dm-1'

    # 3. Create branch headings with a doc_id and content
    context.reset()
    context['doc_id'] = 'src/test.dm'
    br3 = Branch(name='branch', content='Introduction', attributes=tuple(),
                 context=context)
    assert br3.get_id() == 'br:src-test-dm-introduction'
    assert br3.attributes == (('id', 'br:src-test-dm-introduction'),)
    assert br3.get_attribute('id') == 'br:src-test-dm-introduction'

    # 4. Create branch headings with an id specified
    context.reset()
    context['doc_id'] = 'src/test.dm'
    br4 = Branch(name='branch', content='Introduction',
                 attributes=(('id', 'myid'),), context=context)
    assert br4.get_id() == 'myid'
    assert br4.attributes == (('id', 'myid'),)
    assert br4.get_attribute('id') == 'myid'


def test_heading_with_macros(context_cls):
    """Test the heading tags that use macros."""

    # 1. Test a basic macro
    context = context_cls(**{'@test':'This is my test'})

    text = """
    @chapter{@test}
    """
    s = replace_macros(text, context=context)
    ast = process_ast(s, context=context)

    assert ast[1].name == 'chapter'
    assert ast[1].content == 'This is my test'
    assert ast[1].get_id() == 'br:this-is-my-test'

    # 2. Test a macro with tags
    context = context_cls(**{'@test': 'This is @b{my} test'})

    text = """
        @chapter{@test}
        """
    s = replace_macros(text, context=context)
    ast = process_ast(s, context=context)

    assert ast[1].name == 'chapter'
    assert ast[1].content[0] == 'This is '
    assert ast[1].content[1].name == 'b'
    assert ast[1].content[1].content == 'my'
    assert ast[1].content[2] == ' test'
    assert ast[1].get_id() == 'br:this-is-my-test'

    # 3. Test a macro for a header entry that forms a tag.
    context = context_cls(**{'@title': 'This is @b{my} test'})

    text = """
    @chapter{@title}
    """
    s = replace_macros(text, context=context)
    ast = process_ast(s, context=context)

    assert isinstance(ast[1], Branch)
    assert ast[1].name == 'chapter'

    assert ast[1].content[0] == 'This is '
    assert ast[1].content[1].name == 'b'
    assert ast[1].content[1].content == 'my'
    assert ast[1].content[2] == ' test'
    assert ast[1].get_id() == 'br:this-is-my-test'
    assert ast.txt == '\n    This is my test\n    '


def test_heading_labels_formatting(tmpdir):
    """Test the formatting of labels for headings."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write(strip_leading_space("""
    ---
    targets: html, txt
    ---
    @chapter{First Chapter}
    @section{Section One-One}
    @chapter{Second Chapter}
    @section{Section Two-One}
    @chapter{Third Chapter}
    """))

    target_filepath = tmpdir.join('txt').join('main.txt')

    doc = Document(str(src_filepath), str(tmpdir))
    doc.render()

    # Check the labels
    label_man = doc.context['label_manager']

    # There should be 6 labels: 1 for the document, 3 for chapters,
    # 2 for sections
    assert len(label_man.labels) == 6

    # Check the formatted string of the labels
    chapter_labels = label_man.get_labels(kinds='branch')
    assert len(chapter_labels) == 3

    key = """
    First Chapter


    Section One-One


    Second Chapter


    Section Two-One


    Third Chapter



    """

    assert target_filepath.read() == strip_leading_space(key)

    # Next try assigning a different default header label in the context
    src_filepath.write(strip_leading_space("""
    ---
    targets: html, txt
    label_fmts: 
        heading_branch: $label.tree_number. $label.title
        heading_section: $label.tree_number. $label.title
        heading_subsection: $label.tree_number. $label.title
        heading_subsubsection: $label.tree_number. $label.title
    ---
    @chapter{First Chapter}
    @section{Section One-One}
    @chapter{Second Chapter}
    @section{Section Two-One}
    @chapter{Third Chapter}
    """))
    doc.render()

    key = """
    1. First Chapter


    1.1. Section One-One


    2. Second Chapter


    2.1. Section Two-One


    3. Third Chapter



    """
    assert target_filepath.read() == strip_leading_space(key)


def test_heading_labels_html(tmpdir):
    """Tests the production of heading html with labels."""

    # Create a mock document
    tmpdir.join('src').mkdir()
    src_filepath = tmpdir.join('src').join('text.dm')

    src = """
    ---
    targets: html
    ---
    """
    src_filepath.write(strip_leading_space(src))

    doc = Document(str(src_filepath), str(tmpdir))
    label_man = doc.context['label_manager']

    # 1. Test with default labels

    markups = {
        '@chapter{Chapter 1}': '<h1 id="br:text-dm-chapter-1">\n'
                               '  <span class="branch"><span class="number">1.</span> Chapter 1</span>\n'
                               '</h1>\n',
        '@section{Section 1}': '<h2 id="sec:text-dm-section-1">\n'
                               '  <span class="section"><span class="number">1.</span> Section 1</span>\n'
                               '</h2>\n',
        '@subsection{Section 2}': '<h3 id="subsec:text-dm-section-2">\n'
                                  '  <span class="subsection"><span class="number">1.</span> Section 2</span>\n'
                                  '</h3>\n',
        '@subsubsection{Section 3}': '<h4 id="subsubsec:text-dm-section-3">\n'
                                     '  <span class="subsubsection"><span class="number">1.</span> Section 3</span>\n'
                                     '</h4>\n',
        '@h1{Chapter 1}': '<h1 id="br:text-dm-chapter-1">\n'
                          '  <span class="branch"><span class="number">1.</span> Chapter 1</span>\n'
                          '</h1>\n',
        '@h2{Section 2}': '<h2 id="sec:text-dm-section-2">\n'
                          '  <span class="section"><span class="number">1.</span> Section 2</span>\n'
                          '</h2>\n',
        '@h3{Section 3}': '<h3 id="subsec:text-dm-section-3">\n'
                          '  <span class="subsection"><span class="number">1.</span> Section 3</span>\n'
                          '</h3>\n',
        '@h4{Section 4}': '<h4 id="subsubsec:text-dm-section-4">\n'
                          '  <span class="subsubsection"><span class="number">1.</span> Section 4</span>\n'
                          '</h4>\n',
        '@chapter': '<h1 id="br:text-dm-1">\n'
                    '  <span class="branch"><span class="number">1.</span> </span>\n'
                    '</h1>\n',
        '@chapter{}': '<h1 id="br:text-dm-1">\n'
                      '  <span class="branch"><span class="number">1.</span> </span>\n'
                      '</h1>\n',
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        doc.reset_contexts()
        heading = process_ast(src, context=doc.context)
        label_man.register_labels()
        assert heading.html == html

    # 2. Test with 'nolabel' specified

    markups = {
        '@section[nolabel]{Section 1}': '<h2>Section 1</h2>\n',
        '@subsection[nolabel]{Section 2}': '<h3>Section 2</h3>\n',
        '@subsubsection[nolabel]{Section 3}': '<h4>Section 3</h4>\n',
        '@h1[nolabel]{Section 1}': '<h1>Section 1</h1>\n',
        '@h2[nolabel]{Section 2}': '<h2>Section 2</h2>\n',
        '@h3[nolabel]{Section 3}': '<h3>Section 3</h3>\n',
        '@h4[nolabel]{Section 4}': '<h4>Section 4</h4>\n',
    }

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        doc.reset_contexts()
        heading = process_ast(src, context=doc.context)
        label_man.register_labels()

        assert heading.html == html


def test_heading_labels_tex(tmpdir):
    """Tests the production of heading tex with labels."""

    # Create a mock document
    tmpdir.join('src').mkdir()
    src_filepath = tmpdir.join('src').join('text.dm')

    src = """
    ---
    targets: html
    ---
    """
    src_filepath.write(strip_leading_space(src))

    doc = Document(str(src_filepath), str(tmpdir))
    label_man = doc.context['label_manager']

    # 1. Test with default labels

    markups = {
        '@chapter{Chapter 1}': ('\n\\setcounter{chapter}{1}\n'
                                '\\chapter{Chapter 1} '
                                '\\label{br:text-dm-chapter-1}\n\n'),
        '@section{Section 1}': ('\n\\setcounter{section}{1}\n'
                                '\\section{Section 1} '
                                '\\label{sec:text-dm-section-1}\n\n'),
        '@subsection{Section 2}': ('\n\\setcounter{subsection}{1}\n'
                                   '\\subsection{Section 2} '
                                   '\\label{subsec:text-dm-section-2}\n\n'),
        '@subsubsection{Section 3}': ('\n\\setcounter{subsubsection}{1}\n'
                                      '\\subsubsection{Section 3} '
                                      '\\label{subsubsec:text-dm-section-3}\n\n'),
        '@h2{Section 2}': ('\n\\setcounter{section}{1}\n'
                           '\\section{Section 2} '
                           '\\label{sec:text-dm-section-2}\n\n'),
        '@h3{Section 3}': ('\n\\setcounter{subsection}{1}\n'
                           '\\subsection{Section 3} '
                           '\\label{subsec:text-dm-section-3}\n\n'),
        '@h4{Section 4}': ('\n\\setcounter{subsubsection}{1}\n'
                           '\\subsubsection{Section 4} '
                           '\\label{subsubsec:text-dm-section-4}\n\n'),
        '@h5{Section 5}': '\\paragraph{Section 5}',
        '@chapter': ('\n\\setcounter{chapter}{1}\n'
                     '\\chapter{} \\label{br:text-dm-1}\n\n'),
        '@chapter{}': ('\n\\setcounter{chapter}{1}\n'
                       '\\chapter{} \\label{br:text-dm-1}\n\n'),
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, tex in markups.items():
        doc.reset_contexts()
        root = process_ast(src, context=doc.context)
        label_man.register_labels()
        assert root.tex == tex

    # 2. Test with 'nolabel' specified

    markups = {
        '@section[nolabel]{Section 1}': '\n\\section{Section 1}\n\n',
        '@subsection[nolabel]{Section 2}': '\n\\subsection{Section 2}\n\n',
        '@subsubsection[nolabel]{Section 3}': '\n\\subsubsection{Section 3}\n\n',
        '@h2[nolabel]{Section 2}': '\n\\section{Section 2}\n\n',
        '@h3[nolabel]{Section 3}': '\n\\subsection{Section 3}\n\n',
        '@h4[nolabel]{Section 4}': '\n\\subsubsection{Section 4}\n\n',
        '@h5{Section 5}': '\\paragraph{Section 5}',
    }

    # Generate a tag for each and compare the generated html to the answer key
    for src, tex in markups.items():
        doc.reset_contexts()
        root = process_ast(src, context=doc.context)
        label_man.register_labels()

        assert root.tex == tex
