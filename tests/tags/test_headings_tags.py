"""
Tags for headings
"""
import pytest

from disseminate.tags import Tag
from disseminate.tags.headings import Chapter
from disseminate.utils.tests import strip_leading_space


def test_heading_labels(doc, context_cls):
    """Test the setting and of heading identifiers and labels."""

    context = context_cls()

    # 1. Create a chapter heading without a doc_id and and content. This should
    #    raise and exception
    with pytest.raises(AssertionError):
        # A 'doc_id' is needed to create the label id tag
        br1 = Chapter(name='chapter', content='', attributes='',
                      context=context)

    # 2. Create a chapter heading without a label_manager
    context['doc_id'] = 'test'
    with pytest.raises(AssertionError):
        br2 = Chapter(name='chapter', content='', attributes='',
                      context=context)

    # 3. Now create a heading label with a context that includes a 'doc_id'
    #    and a 'label_manager'.
    context = doc.context
    br3 = Chapter(name='chapter', content='', attributes='',
                  context=context)
    assert br3.label_id == 'ch:test-dm-1'
    assert br3.attributes['id'] == 'ch:test-dm-1'

    # 4. Create chapter headings with a doc_id
    context.reset()
    context['doc_id'] = 'src/test.dm'
    br4 = Chapter(name='chapter', content='', attributes='', context=context)
    assert br4.label_id == 'ch:src-test-dm-1'
    assert br4.attributes['id'] == 'ch:src-test-dm-1'

    # 5. Create chapter headings with a doc_id and content
    context.reset()
    context['doc_id'] = 'src/test.dm'
    br5 = Chapter(name='chapter', content='Introduction', attributes='',
                  context=context)
    assert br5.label_id == 'ch:src-test-dm-introduction'
    assert br5.attributes['id'] == 'ch:src-test-dm-introduction'

    # 6. Create chapter headings with an id specified
    context.reset()
    context['doc_id'] = 'src/test.dm'
    br6 = Chapter(name='chapter', content='Introduction',
                  attributes='id=myid', context=context)
    assert br6.label_id == 'myid'
    assert br6.attributes['id'] == 'myid'


def test_heading_with_macros(doc):
    """Test the heading tags that use macros."""

    # Get the context from a test document with a 'doc_id' and 'label_manager'
    context = doc.context
    context['@test'] = 'This is my test'

    # 1. Test a basic macro
    text = """
    @chapter{@test}
    """
    root = Tag(name='root', content=text, attributes='', context=context)
    chap = root.content[1]

    assert chap.name == 'chapter'
    assert chap.content == 'This is my test'
    assert chap.label_id == 'ch:test-dm-this-is-my-test'

    # 2. Test a macro with tags
    context['@test'] = 'This is @b{my} test'

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
    assert chap.label_id == 'ch:test-dm-this-is-my-test'

    # 3. Test a macro for a header entry that forms a tag.
    context['@title'] = 'This is @b{my} test'

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
    assert chap.label_id == 'ch:test-dm-this-is-my-test'
    assert root.txt == '\n    Chapter 1. This is my test\n    '
    assert chap.txt == 'Chapter 1. This is my test'


def test_heading_with_substituted_content(doc):
    """Test heading tags with substituted content."""

    # Get the context from a test document with a 'doc_id' and 'label_manager'
    context = doc.context

    # 1. Test a basic example without substitution
    title = Chapter(name='title', content='', attributes=tuple(),
                    context=context)
    assert title.txt == 'Chapter 1. '

    # 2. Test with a substituted content from the context with a simple string
    #    substitution.
    context['title'] = 'My title'
    title = Chapter(name='title', content='', attributes=tuple(),
                    context=context)
    assert title.txt == 'Chapter 1. My title'
    assert title.html == ('<h2 id="ch:test-dm-my-title">'
                          '<span class="label">Chapter 1. </span>'
                          'My title</h2>\n')

    # 3. Test with a substituted content from the context with formatting
    context['title'] = 'My @b{title}'
    title = Chapter(name='title', content='', attributes=tuple(),
                    context=context)
    assert title.txt == 'Chapter 1. My title'
    assert title.html == ('<h2 id="ch:test-dm-my-title">'
                          '<span class="label">Chapter 1. </span>'
                          'My <strong>title</strong></h2>\n')


def test_heading_labels_formatting(doc):
    """Test the formatting of labels for headings."""

    # 1. Test basic heading with new label format
    doc.context['label_fmts']['heading_chapter'] = "My Chapter @label.number! "
    root = Tag(name='root', content='@chapter{one}', attributes='',
               context=doc.context)
    chapter = root.content

    assert chapter.txt == 'My Chapter 1! one'

    # Check that a chapter label was created
    label_manager = doc.context['label_manager']
    chapter_labels = label_manager.get_labels(kinds='chapter')
    assert len(chapter_labels) == 1


def test_heading_labels_nolabel(doc):
    """Test headings with the 'nolabel' attribute."""

    # 1. Test basic heading with new label format
    doc.context['label_fmts']['heading_chapter'] = "My Chapter @label.number! "
    root = Tag(name='root', content='@chapter[nolabel]{one}', attributes='',
               context=doc.context)
    chapter = root.content

    assert chapter.txt == 'one'

    # Check that no chapter label was created
    label_manager = doc.context['label_manager']
    chapter_labels = label_manager.get_labels(kinds='chapter')
    assert len(chapter_labels) == 0


# default targets

def test_heading_newline_preservation_default(doc):
    """Test heading labels and the preservation of newlines around the tag
    for default targets."""

    # Get the label manager and context from the document
    context = doc.context

    # 1. Test without surrounding newlines
    src = '@chapter{Chapter 1}'
    root = Tag(name='root', content=src, attributes='', context=context)
    assert root.txt == 'Chapter 1. Chapter 1'

    # 2. Test with surrounding newlines
    src = '\n@chapter{Chapter 1}\n'
    root = Tag(name='root', content=src, attributes='', context=context)
    assert root.txt == ('\n'
                        'Chapter 1. Chapter 1'
                        '\n')

    # 3. Test with double newlines, used for paragraphs
    src = '\n\n@chapter{Chapter 1}\n\n'
    root = Tag(name='root', content=src, attributes='', context=context)
    assert root.txt == ('\n\n'
                        'Chapter 1. Chapter 1'
                        '\n\n')


# tex targets

def test_heading_labels_tex(doc):
    """Tests the production of heading tex with labels."""

    # Get the label manager and context from the document
    context = doc.context

    # 1. Test with default labels
    markups = {
        '@part{Part 1}': '\\setcounter{part}{1}\n'
                         '\\part{Part 1. Part 1} '
                         '\\label{part:test-dm-part-1}',
        '@chapter{Chapter 1}': '\\setcounter{chapter}{1}\n'
                               '\\chapter{Chapter 1. Chapter 1} '
                               '\\label{ch:test-dm-chapter-1}',
        '@section{Section 1}': '\\setcounter{section}{1}\n'
                               '\\section{1. Section 1} '
                               '\\label{sec:test-dm-section-1}',
        '@subsection{Section 2}': '\\setcounter{subsection}{1}\n'
                                  '\\subsection{1. Section 2} '
                                  '\\label{subsec:test-dm-section-2}',
        '@subsubsection{Section 3}': '\\setcounter{subsubsection}{1}\n'
                                     '\\subsubsection{1. Section 3} '
                                     '\\label{subsubsec:test-dm-section-3}',
        '@h2{Section 2}': '\\setcounter{chapter}{1}\n'
                          '\\chapter{Chapter 1. Section 2} '
                          '\\label{ch:test-dm-section-2}',
        '@h3{Section 3}': '\\setcounter{section}{1}\n'
                          '\\section{1. Section 3} '
                          '\\label{sec:test-dm-section-3}',
        '@h4{Section 4}': '\\setcounter{subsection}{1}\n'
                          '\\subsection{1. Section 4} '
                          '\\label{subsec:test-dm-section-4}',
        '@h5{Section 5}': '\\setcounter{subsubsection}{1}\n'
                          '\\subsubsection{1. Section 5} '
                          '\\label{subsubsec:test-dm-section-5}',
        '@h6{Section 6}': '\\paragraph{Section 6}',
        '@chapter': '\\setcounter{chapter}{1}\n'
                    '\\chapter{Chapter 1. } \\label{ch:test-dm-1}',
        '@chapter{}': '\\setcounter{chapter}{1}\n'
                      '\\chapter{Chapter 1. } \\label{ch:test-dm-1}',
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, tex in markups.items():
        doc.reset_contexts()
        root = Tag(name='root', content=src, attributes='', context=context)
        heading = root.content
        assert heading.tex == tex


def test_heading_newline_preservation_tex(doc):
    """Test heading labels and the preservation of newlines around the tag
    for tex targets."""

    # Get the label manager and context from the document
    context = doc.context

    # 1. Test without surrounding newlines
    src = '@chapter{Chapter 1}'
    root = Tag(name='root', content=src, attributes='', context=context)
    assert root.tex == ('\\setcounter{chapter}{1}\n'
                        '\\chapter{Chapter 1. Chapter 1} '
                        '\\label{ch:test-dm-chapter-1}')

    # 2. Test with surrounding newlines
    src = '\n@chapter{Chapter 1}\n'
    root = Tag(name='root', content=src, attributes='', context=context)
    assert root.tex == ('\n'
                        '\\setcounter{chapter}{1}\n'
                        '\\chapter{Chapter 1. Chapter 1} '
                        '\\label{ch:test-dm-chapter-1}'
                        '\n')

    # 3. Test with double newlines, used for paragraphs
    src = '\n\n@chapter{Chapter 1}\n\n'
    root = Tag(name='root', content=src, attributes='', context=context)
    assert root.tex == ('\n\n'
                        '\\setcounter{chapter}{1}\n'
                        '\\chapter{Chapter 1. Chapter 1} '
                        '\\label{ch:test-dm-chapter-1}'
                        '\n\n')


# html targets

def test_heading_labels_html(doc):
    """Tests the production of heading html with labels."""

    # Get the label manager and context from the document
    context = doc.context

    # 1. Test with default labels

    markups = {
        '@part{Part 1}': '<h1 id="part:test-dm-part-1">'
                         '<span class="label">Part 1. </span>Part 1</h1>\n',
        '@chapter{Chapter 1}': '<h2 id="ch:test-dm-chapter-1">'
                               '<span class="label">Chapter 1. </span>'
                               'Chapter 1</h2>\n',
        '@section{Section 1}': '<h3 id="sec:test-dm-section-1">'
                               '<span class="label">1. </span>'
                               'Section 1</h3>\n',
        '@subsection{Section 2}': '<h4 id="subsec:test-dm-section-2">'
                                  '<span class="label">1. </span>'
                                  'Section 2</h4>\n',
        '@subsubsection{Section 3}': '<h5 id="subsubsec:test-dm-section-3">'
                                     '<span class="label">1. </span>'
                                     'Section 3</h5>\n',
        '@h1{Chapter 1}': '<h1 id="title:test-dm-chapter-1">'
                          '<span class="label"/>Chapter 1</h1>\n',
        '@h2{Chapter 2}': '<h2 id="ch:test-dm-chapter-2">'
                          '<span class="label">Chapter 1. </span>'
                          'Chapter 2</h2>\n',
        '@h3{Section 3}': '<h3 id="sec:test-dm-section-3">'
                          '<span class="label">1. </span>Section 3</h3>\n',
        '@h4{Section 4}': '<h4 id="subsec:test-dm-section-4">'
                          '<span class="label">1. </span>Section 4</h4>\n',
        '@h5{Section 5}': '<h5 id="subsubsec:test-dm-section-5">'
                          '<span class="label">1. </span>Section 5</h5>\n',
        '@chapter': '<h2 id="ch:test-dm-1">\n'
                    '  <span class="label">Chapter 1. </span>\n'
                    '</h2>\n',
        '@chapter{}': '<h2 id="ch:test-dm-2">\n'
                      '  <span class="label">Chapter 1. </span>\n'
                      '</h2>\n',
               }

    # Generate a tag for each and compare the generated html to the answer key
    for src, html in markups.items():
        root = Tag(name='root', content=src, attributes='', context=context)
        heading = root.content
        assert heading.html == html


def test_heading_newline_preservation_html(doc):
    """Test heading labels and the preservation of newlines around the tag
    for html targets."""

    # Get the label manager and context from the document
    context = doc.context

    # 1. Test without surrounding newlines
    src = '@chapter{Chapter 1}'
    root = Tag(name='root', content=src, attributes='', context=context)
    assert root.html == ('<span class="root">\n'
                         '  <h2 id="ch:test-dm-chapter-1">'
                         '<span class="label">Chapter 1. </span>'
                         'Chapter 1</h2>\n'
                         '</span>\n')

    # 2. Test with surrounding newlines
    src = '\n@chapter{Chapter 1}\n'
    root = Tag(name='root', content=src, attributes='', context=context)
    assert root.html == ('<span class="root">\n'
                         '<h2 id="ch:test-dm-chapter-1">'
                         '<span class="label">Chapter 1. </span>'
                         'Chapter 1</h2>\n'
                         '</span>\n')

    # 3. Test with double newlines, used for paragraphs
    src = '\n\n@chapter{Chapter 1}\n\n'
    root = Tag(name='root', content=src, attributes='', context=context)
    assert root.html == ('<span class="root">\n\n'
                         '<h2 id="ch:test-dm-chapter-1">'
                         '<span class="label">Chapter 1. </span>'
                         'Chapter 1</h2>\n\n'
                         '</span>\n')
