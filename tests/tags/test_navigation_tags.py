"""
Tests for navigation tags.
"""
from disseminate.tags.navigation import Next, Prev


# html tests

def test_prev_html(doctree):
    """Test the prev tag for html targets"""

    # Get the documents from the doctree
    doc1, doc2, doc3 = doctree.documents_list(only_subdocuments=False)

    # Create a next tag for each document
    prev1 = Prev(name='prev', content='prev', attributes='',
                 context=doc1.context)
    assert prev1.html == ''

    prev2 = Prev(name='prev', content='prev', attributes='',
                 context=doc2.context)
    assert (prev2.html ==
            '<a href="test1.html" class="ref">test1</a>')

    prev3 = Prev(name='prev', content='prev', attributes='',
                 context=doc3.context)
    assert (prev3.html ==
            '<a href="test2.html" class="ref">test2</a>')


def test_next_html(doctree):
    """Test the next tag for html targets"""

    # Get the documents from the doctree
    doc1, doc2, doc3 = doctree.documents_list(only_subdocuments=False)

    # Create a next tag for each document
    next1 = Next(name='next', content='next', attributes='',
                 context=doc1.context)
    assert (next1.html ==
            '<a href="test2.html" class="ref">test2</a>')

    next2 = Next(name='next', content='next', attributes='',
                 context=doc2.context)
    assert (next2.html ==
            '<a href="test3.html" class="ref">test3</a>')

    next3 = Next(name='next', content='next', attributes='',
                 context=doc3.context)
    assert next3.html == ''


def test_prev_context_html(doctree):
    """Test the 'prev' entry in the context"""

    # Get the documents from the doctree
    doc1, doc2, doc3 = doctree.documents_list(only_subdocuments=False)

    for doc in (doc1, doc2, doc3):
        assert 'prev' in doc.context

    assert doc1.context['prev'].html == ''
    assert (doc2.context['prev'].html ==
            '<a href="test1.html" class="ref">test1</a>')
    assert (doc3.context['prev'].html ==
            '<a href="test2.html" class="ref">test2</a>')


def test_next_context_html(doctree):
    """Test the 'next' entry in the context"""

    # Get the documents from the doctree
    doc1, doc2, doc3 = doctree.documents_list(only_subdocuments=False)

    for doc in (doc1, doc2, doc3):
        assert 'next' in doc.context

    assert (doc1.context['next'].html ==
            '<a href="test2.html" class="ref">test2</a>')
    assert (doc2.context['next'].html ==
            '<a href="test3.html" class="ref">test3</a>')
    assert doc3.context['next'].html == ''


def test_navigation_missing_target_html(doctree):
    """Test the 'next' entry when the next document does not have an html
    target"""

    # Get the documents from the doctree
    doc1, doc2, doc3 = doctree.documents_list(only_subdocuments=False)

    for doc in (doc1, doc2, doc3):
        assert 'next' in doc.context

    # The next behavior should work as normally
    assert (doc1.context['next'].html ==
            '<a href="test2.html" class="ref">test2</a>')
    assert (doc2.context['next'].html ==
            '<a href="test3.html" class="ref">test3</a>')
    assert doc3.context['next'].html == ''

    # Now remove the '.html' target for doc2. The @next tag for doc1 should
    # now point to doc3.
    doc2.src_filepath.write_text("""
    ---
    targets: tex
    ---
    """
    )
    doc2.load()

    assert (doc1.context['next'].html ==
            '<a href="test3.html" class="ref">test3</a>')
    assert doc2.context['next'].html == ''
    assert doc3.context['next'].html == ''

    # The @prev tag should act accordingly
    assert doc1.context['prev'].html == ''
    assert doc2.context['prev'].html == ''
    assert (doc3.context['prev'].html ==
            '<a href="test1.html" class="ref">test1</a>')
