"""
Tags for headings
"""
from disseminate import Document
from disseminate.tags import Tag
from disseminate.tags.headings import Chapter
from disseminate.utils.tests import strip_leading_space


def test_heading_labels(context_cls):
    """Test the setting and of heading identifiers and labels."""

    context = context_cls()

    # 1. Create chapter headings without a doc_id and and content
    br1 = Chapter(name='chapter', content='', attributes='', context=context)
    assert br1.get_id() == 'ch:1'
    assert br1.attributes == {'id': 'ch:1'}
    assert br1.attributes['id'] == 'ch:1'

    # 2. Create chapter headings with a doc_id
    context.reset()
    context['doc_id'] = 'src/test.dm'
    br2 = Chapter(name='chapter', content='', attributes='', context=context)
    assert br2.get_id() == 'ch:src-test-dm-1'
    assert br2.attributes == {'id': 'ch:src-test-dm-1'}
    assert br2.attributes['id'] == 'ch:src-test-dm-1'

    # 3. Create chapter headings with a doc_id and content
    context.reset()
    context['doc_id'] = 'src/test.dm'
    br3 = Chapter(name='chapter', content='Introduction', attributes='',
                 context=context)
    assert br3.get_id() == 'ch:src-test-dm-introduction'
    assert br3.attributes == {'id': 'ch:src-test-dm-introduction'}
    assert br3.attributes['id'] == 'ch:src-test-dm-introduction'

    # 4. Create chapter headings with an id specified
    context.reset()
    context['doc_id'] = 'src/test.dm'
    br4 = Chapter(name='chapter', content='Introduction',
                 attributes='id=myid', context=context)
    assert br4.get_id() == 'myid'
    assert br4.attributes == {'id': 'myid'}
    assert br4.attributes['id'] == 'myid'


def test_heading_with_macros(context_cls):
    """Test the heading tags that use macros."""

    # 1. Test a basic macro
    context = context_cls(**{'@test': 'This is my test'})

    text = """
    @chapter{@test}
    """
    root = Tag(name='root', content=text, attributes='', context=context)
    chap = root.content[1]

    assert chap.name == 'chapter'
    assert chap.content == 'This is my test'
    assert chap.get_id() == 'ch:this-is-my-test'

    # 2. Test a macro with tags
    context = context_cls(**{'@test': 'This is @b{my} test'})

    text = """
        @chapter{@test}
        """
    root = Tag(name='root', content=text, attributes='', context=context)
    chap = root.content[1]

    assert chap.name == 'chapter'
    assert chap.content[0] == 'This is '
    assert chap.content[1].name == 'b'
    assert chap.content[1].content == 'my'
    assert chap.content[2] == ' test'
    assert chap.get_id() == 'ch:this-is-my-test'

    # 3. Test a macro for a header entry that forms a tag.
    context = context_cls(**{'@title': 'This is @b{my} test'})

    text = """
    @chapter{@title}
    """
    root = Tag(name='root', content=text, attributes='', context=context)
    chap = root.content[1]

    assert isinstance(chap, Chapter)
    assert chap.name == 'chapter'

    assert chap.content[0] == 'This is '
    assert chap.content[1].name == 'b'
    assert chap.content[1].content == 'my'
    assert chap.content[2] == ' test'
    assert chap.get_id() == 'ch:this-is-my-test'
    assert root.txt == '\n    This is my test\n    '
    assert chap.txt == 'This is my test'


def test_heading_with_substituted_content(context_cls):
    """Test heading tags with substituted content."""

    # 1. Test a basic example without substitution
    context = context_cls()
    title = Chapter(name='title', content='', attributes=tuple(),
                    context=context)

    assert title.txt == ''

    # 2. Test with a substituted content from the context with a simple string
    #    substitution.
    context['title'] = 'My title'
    title = Chapter(name='title', content='', attributes=tuple(),
                    context=context)

    assert title.txt == 'My title'
    assert title.html == '<h2 id="ch:my-title">My title</h2>\n'

    # 3. Test with a substituted content from the context with formatting
    context['title'] = 'My @b{title}'
    title = Chapter(name='title', content='', attributes=tuple(),
                    context=context)

    assert title.txt == 'My title'
    assert title.html == '<h2 id="ch:my-title">My <strong>title</strong></h2>\n'


def test_heading_labels_formatting(tmpdir):
    """Test the formatting of labels for headings."""

    # 1. Test basic heading formats without tree numbers
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
    chapter_labels = label_man.get_labels(kinds='chapter')
    assert len(chapter_labels) == 3

    key = """
    First Chapter


    Section One-One


    Second Chapter


    Section Two-One


    Third Chapter



    """

    assert target_filepath.read() == strip_leading_space(key)

    # 2. Test chapter-subsubsection headings with tree numbers
    src_filepath.write(strip_leading_space("""
    ---
    targets: html, txt
    label_fmts: 
        heading_chapter: @label.tree_number. @label.title
        heading_section: @label.tree_number. @label.title
        heading_subsection: @label.tree_number. @label.title
        heading_subsubsection: @label.tree_number. @label.title
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

    # 2. Test part-subsubsection headings with tree numbers
    src_filepath.write(strip_leading_space("""
        ---
        targets: html, txt
        label_fmts: 
            heading_part: @label.tree_number. @label.title
            heading_chapter: @label.tree_number. @label.title
            heading_section: @label.tree_number. @label.title
            heading_subsection: @label.tree_number. @label.title
            heading_subsubsection: @label.tree_number. @label.title
        ---
        @part{First Part}
        @chapter{First Chapter}
        @section{Section One-One}
        @chapter{Second Chapter}
        @section{Section Two-One}
        @chapter{Third Chapter}
        """))
    doc.render()

    key = """
    1. First Part
    
    
    1.1. First Chapter


    1.1.1. Section One-One


    1.2. Second Chapter


    1.2.1. Section Two-One


    1.3. Third Chapter



    """
    assert target_filepath.read() == strip_leading_space(key)


# html targets

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
        '@part{Part 1}': '<h1 id="part:text-dm-part-1">\n'
                         '  <span class="part"><span class="number">1.</span> Part 1</span>\n'
                         '</h1>\n',
        '@chapter{Chapter 1}': '<h2 id="ch:text-dm-chapter-1">\n'
                               '  <span class="chapter"><span class="number">1.</span> Chapter 1</span>\n'
                               '</h2>\n',
        '@section{Section 1}': '<h3 id="sec:text-dm-section-1">\n'
                               '  <span class="section"><span class="number">1.</span> Section 1</span>\n'
                               '</h3>\n',
        '@subsection{Section 2}': '<h4 id="subsec:text-dm-section-2">\n'
                                  '  <span class="subsection"><span class="number">1.</span> Section 2</span>\n'
                                  '</h4>\n',
        '@subsubsection{Section 3}': '<h5 id="subsubsec:text-dm-section-3">\n'
                                     '  <span class="subsubsection"><span class="number">1.</span> Section 3</span>\n'
                                     '</h5>\n',
        '@h1{Chapter 1}': '<h1 id="title:text-dm-chapter-1">\n'
                          '  <span class="title">Chapter 1</span>\n'
                          '</h1>\n',
        '@h2{Chapter 2}': '<h2 id="ch:text-dm-chapter-2">\n'
                          '  <span class="chapter"><span class="number">1.</span> Chapter 2</span>\n'
                          '</h2>\n',
        '@h3{Section 3}': '<h3 id="sec:text-dm-section-3">\n'
                          '  <span class="section"><span class="number">1.</span> Section 3</span>\n'
                          '</h3>\n',
        '@h4{Section 4}': '<h4 id="subsec:text-dm-section-4">\n'
                          '  <span class="subsection"><span class="number">1.</span> Section 4</span>\n'
                          '</h4>\n',
        '@h5{Section 5}': '<h5 id="subsubsec:text-dm-section-5">\n'
                          '  <span class="subsubsection"><span class="number">1.</span> Section 5</span>\n'
                          '</h5>\n',
        '@chapter': '<h2 id="ch:text-dm-1">\n'
                    '  <span class="chapter"><span class="number">1.</span> </span>\n'
                    '</h2>\n',
        '@chapter{}': '<h2 id="ch:text-dm-1">\n'
                      '  <span class="chapter"><span class="number">1.</span> </span>\n'
                      '</h2>\n',
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        doc.reset_contexts()
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        heading = root.content
        label_man.register_labels()
        assert heading.html == html

    # 2. Test with 'nolabel' specified

    markups = {
        '@section[nolabel]{Section 1}': '<h3>Section 1</h3>\n',
        '@subsection[nolabel]{Section 2}': '<h4>Section 2</h4>\n',
        '@subsubsection[nolabel]{Section 3}': '<h5>Section 3</h5>\n',
        '@h1[nolabel]{Section 1}': '<h1>Section 1</h1>\n',
        '@h2[nolabel]{Section 2}': '<h2>Section 2</h2>\n',
        '@h3[nolabel]{Section 3}': '<h3>Section 3</h3>\n',
        '@h4[nolabel]{Section 4}': '<h4>Section 4</h4>\n',
    }

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        doc.reset_contexts()
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        heading = root.content
        label_man.register_labels()

        assert heading.html == html


# tex targets

def test_heading_labels_tex(tmpdir):
    """Tests the production of heading tex with labels."""

    # Create a mock document
    tmpdir.join('src').mkdir()
    src_filepath = tmpdir.join('src').join('text.dm')

    src = """
    ---
    targets: tex
    ---
    """
    src_filepath.write(strip_leading_space(src))

    doc = Document(str(src_filepath), str(tmpdir))
    label_man = doc.context['label_manager']

    # 1. Test with default labels

    markups = {
        '@part{Part 1}': ('\n\\setcounter{part}{1}\n'
                          '\\part{Part 1} '
                          '\\label{part:text-dm-part-1}\n\n'),
        '@chapter{Chapter 1}': ('\n\\setcounter{chapter}{1}\n'
                                '\\chapter{Chapter 1} '
                                '\\label{ch:text-dm-chapter-1}\n\n'),
        '@section{Section 1}': ('\n\\setcounter{section}{1}\n'
                                '\\section{Section 1} '
                                '\\label{sec:text-dm-section-1}\n\n'),
        '@subsection{Section 2}': ('\n\\setcounter{subsection}{1}\n'
                                   '\\subsection{Section 2} '
                                   '\\label{subsec:text-dm-section-2}\n\n'),
        '@subsubsection{Section 3}': ('\n\\setcounter{subsubsection}{1}\n'
                                      '\\subsubsection{Section 3} '
                                      '\\label{subsubsec:text-dm-section-3}\n\n'),
        '@h2{Section 2}': ('\n\\setcounter{chapter}{1}\n'
                           '\\chapter{Section 2} '
                           '\\label{ch:text-dm-section-2}\n\n'),
        '@h3{Section 3}': ('\n\\setcounter{section}{1}\n'
                           '\\section{Section 3} '
                           '\\label{sec:text-dm-section-3}\n\n'),
        '@h4{Section 4}': ('\n\\setcounter{subsection}{1}\n'
                           '\\subsection{Section 4} '
                           '\\label{subsec:text-dm-section-4}\n\n'),
        '@h5{Section 5}': ('\n\\setcounter{subsubsection}{1}\n'
                           '\\subsubsection{Section 5} '
                           '\\label{subsubsec:text-dm-section-5}\n\n'),
        '@h6{Section 6}': '\\paragraph{Section 6}',
        '@chapter': ('\n\\setcounter{chapter}{1}\n'
                     '\\chapter{} \\label{ch:text-dm-1}\n\n'),
        '@chapter{}': ('\n\\setcounter{chapter}{1}\n'
                       '\\chapter{} \\label{ch:text-dm-1}\n\n'),
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, tex in markups.items():
        doc.reset_contexts()
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        heading = root.content
        label_man.register_labels()
        assert heading.tex == tex

    # 2. Test with 'nolabel' specified

    markups = {
        '@section[nolabel]{Section 1}': '\n\\section{Section 1}\n\n',
        '@subsection[nolabel]{Section 2}': '\n\\subsection{Section 2}\n\n',
        '@subsubsection[nolabel]{Section 3}': '\n\\subsubsection{Section 3}\n\n',
        '@h2[nolabel]{Section 2}': '\n\\chapter{Section 2}\n\n',
        '@h3[nolabel]{Section 3}': '\n\\section{Section 3}\n\n',
        '@h4[nolabel]{Section 4}': '\n\\subsection{Section 4}\n\n',
        '@h5[nolabel]{Section 5}': '\n\\subsubsection{Section 5}\n\n',
        '@h6{Section 6}': '\\paragraph{Section 6}',
    }

    # Generate a tag for each and compare the generated html to the answer key
    for src, tex in markups.items():
        doc.reset_contexts()
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        heading = root.content
        label_man.register_labels()

        assert heading.tex == tex
