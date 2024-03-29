"""
Tests for navigation tags.
"""
import pathlib

from disseminate.tags.navigation import Next, Prev, Pdflink


ex1_root = pathlib.Path('tests') / 'tags' / 'examples' / 'toc_ex1'


def add_headings(*docs, wait):
    """Write a section heading to each of the document src file and re-load."""
    for count, doc in enumerate(docs):
        # append to the current text
        wait()
        text = doc.src_filepath.read_text()
        text += "\n@section{" + str(count) + "}\n"
        doc.src_filepath.write_text(text)
        doc.load()


# html tests

def test_prev_heading_label_html(doctree, wait):
    """Test the prev tag for html targets with heading labels"""

    # Get the documents from the doctree
    doc1, doc2, doc3 = doctree.documents_list(only_subdocuments=False)

    # Next add headings to the documents
    add_headings(doc1, doc2, doc3, wait=wait)

    # Create a next tag for each document
    prev1 = Prev(name='prev', content='prev', attributes='',
                 context=doc1.context)
    assert prev1.html == ''

    prev2 = Prev(name='prev', content='prev', attributes='',
                 context=doc2.context)
    assert (prev2.html ==
            '<a href="test.html#sec:test-dm-0" class="ref">0</a>')

    prev3 = Prev(name='prev', content='prev', attributes='',
                 context=doc3.context)
    assert (prev3.html ==
            '<a href="test2.html#sec:test2-dm-1" class="ref">1</a>')


def test_next_heading_label_html(doctree, wait):
    """Test the next tag for html targets with heading labels"""

    # Get the documents from the doctree
    doc1, doc2, doc3 = doctree.documents_list(only_subdocuments=False)

    # Next add headings to the documents
    add_headings(doc1, doc2, doc3, wait=wait)

    # Create a next tag for each document
    next1 = Next(name='next', content='next', attributes='',
                 context=doc1.context)
    assert (next1.html ==
            '<a href="test2.html#sec:test2-dm-1" class="ref">1</a>')

    next2 = Next(name='next', content='next', attributes='',
                 context=doc2.context)
    assert (next2.html ==
            '<a href="test3.html#sec:test3-dm-2" class="ref">2</a>')

    next3 = Next(name='next', content='next', attributes='',
                 context=doc3.context)
    assert next3.html == ''


def test_prev_context_html(doctree, wait):
    """Test the 'prev' entry in the context"""

    # Get the documents from the doctree
    doc1, doc2, doc3 = doctree.documents_list(only_subdocuments=False)

    for doc in (doc1, doc2, doc3):
        assert 'prev' in doc.context

    # First test out the context entries when no headings are available.
    # These should return empty strings
    assert 'prev_html' not in doc1.context
    assert 'prev_html' not in doc2.context
    assert 'prev_html' not in doc3.context

    # Next add headings to the documents
    add_headings(doc1, doc2, doc3, wait=wait)

    assert doc1.context['prev'].html == ''
    assert (doc2.context['prev'].html ==
            '<a href="test.html#sec:test-dm-0" class="ref">0</a>')
    assert (doc3.context['prev'].html ==
            '<a href="test2.html#sec:test2-dm-1" class="ref">1</a>')


def test_next_context_html(doctree, wait):
    """Test the 'next' entry in the context"""

    # Get the documents from the doctree
    doc1, doc2, doc3 = doctree.documents_list(only_subdocuments=False)

    for doc in (doc1, doc2, doc3):
        assert 'next' in doc.context

    # First test out the context entries when no headings are available.
    # These should return empty strings
    assert 'next_html' not in doc1.context
    assert 'next_html' not in doc2.context
    assert 'next_html' not in doc3.context

    # Next add headings and these should be properly formatted
    add_headings(doc1, doc2, doc3, wait=wait)

    assert (doc1.context['next'].html ==
            '<a href="test2.html#sec:test2-dm-1" class="ref">1</a>')
    assert (doc2.context['next'].html ==
            '<a href="test3.html#sec:test3-dm-2" class="ref">2</a>')
    assert doc3.context['next'].html == ''


def test_navigation_missing_target_html(doctree, wait):
    """Test the 'next' entry when the next document does not have an html
    target"""

    # Get the documents from the doctree
    doc1, doc2, doc3 = doctree.documents_list(only_subdocuments=False)

    for doc in (doc1, doc2, doc3):
        assert 'next' in doc.context

    # Next add headings to the documents
    add_headings(doc1, doc2, doc3, wait=wait)

    # The next behavior should work as normally
    assert (doc1.context['next'].html ==
            '<a href="test2.html#sec:test2-dm-1" class="ref">1</a>')
    assert (doc2.context['next'].html ==
            '<a href="test3.html#sec:test3-dm-2" class="ref">2</a>')
    assert doc3.context['next'].html == ''

    # Now remove the '.html' target for doc2. The @next tag for doc1 should
    # now point to doc3.
    doc2.src_filepath.write_text("""
    ---
    targets: tex
    ---
    @section{1}
    """)
    print('here')
    doc2.load()

    assert (doc1.context['next'].html ==
            '<a href="test3.html#sec:test3-dm-2" class="ref">2</a>')
    assert doc2.context['next'].html == ''
    assert doc3.context['next'].html == ''

    # The @prev tag should act accordingly
    assert doc1.context['prev'].html == ''
    assert doc2.context['prev'].html == ''
    assert (doc3.context['prev'].html ==
            '<a href="test.html#sec:test-dm-0" class="ref">0</a>')


def test_pdflink(load_example):
    """Test the pdflink tag."""

    # 1. The 'tests/tags/examples/toc_ex1' directory contains three markup
    #    files:
    #    file1.dm, in the root folder, and file21.dm and file2.dm in the 'sub'
    #    folder. The 'file1.dm' includes 'file21.dm' and 'file22.dm'.
    #    The file1.dm has pdf has a target
    doc = load_example(ex1_root / 'file1.dm')

    # Create the pdflink tag
    pdf = Pdflink(name='pdflink', content='', attributes='',
                  context=doc.context)
    assert pdf.html == '../pdf/file1.pdf'
