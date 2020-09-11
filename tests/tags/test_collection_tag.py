"""
Test the collection tag.
"""
import pytest

from disseminate import settings
from disseminate.document import Document
from disseminate.tags.collection import Collection


@pytest.fixture(scope='function')
def doctree(doctree, wait):
    """Setup a root document with two sub-documents"""
    # Create temp files
    doc1 = doctree
    doc2, doc3 = doctree.documents_list(only_subdocuments=True)
    src_filepath1 = doc1.src_filepath
    src_filepath2 = doc2.src_filepath
    src_filepath3 = doc3.src_filepath

    # Write the files. A 1us sleep is placed between writes to offset the
    # mtimes of the 3 files for systems with at least 1 microsecond time
    # resolution
    src_filepath1.write_text("""
    ---
    targets: html, tex
    include:
      test2.dm
      test3.dm
    ---
    @chapter{one}
    @collection
    """)
    wait()  # sleep time offset needed for different mtimes

    src_filepath2.write_text("""
    @chapter{two}
    """)
    wait()  # sleep time offset needed for different mtimes

    src_filepath3.write_text("""
    @chapter{three}
    """)
    wait()  # sleep time offset needed for different mtimes

    # Load the root document
    doc1.load()
    return doc1


def test_collection_selective_target(doctree):
    """Test the collection tag when one of the sub-documents is not listed as
    a target."""

    # Unpack the subdocuments
    subdocs = doctree.documents_list(only_subdocuments=True, recursive=True)
    assert len(subdocs) == 2
    subdoc1, subdoc2 = subdocs

    # Change the target for the 2nd subdocument
    src_filepath3 = subdoc2.context['src_filepath']
    src_filepath3.write_text("""
    ---
    targets: html
    ---
    @chapter{three}
    """)
    subdoc2.load()  # reload the document

    # Now try rendering the collection for the root document in tex. Since tex
    # is not a listed target for the 2nd sub-document, it's contents (chapter
    # three) should not be listed.
    body_attr = settings.body_attr
    root1 = doctree.context[body_attr]
    assert root1.tex == ('\\setcounter{chapter}{0}\n'
                         '\\chapter{Chapter 1. one} \\label{ch:test-dm-one}\n'
                         '\\setcounter{chapter}{1}\n'
                         '\\chapter{Chapter 2. two} \\label{ch:test2-dm-two}')


# default target

def test_collection_default(doctree):
    """Test the generation of default collections"""

    # The context body for the main document should only have the body of the
    # main document
    body_attr = settings.body_attr
    root1 = doctree.context[body_attr]
    assert root1.default == ('Chapter 1. one\n'
                             'Chapter 2. two\n'
                             'Chapter 3. three')


# tex target

def test_collection_tex(doctree):
    """Test the generation of default collections"""

    # The context body for the main document should only have the body of the
    # main document
    body_attr = settings.body_attr
    root1 = doctree.context[body_attr]
    assert root1.tex == ('\\setcounter{chapter}{0}\n'
                         '\\chapter{Chapter 1. one} \\label{ch:test-dm-one}\n'
                         '\\setcounter{chapter}{1}\n'
                         '\\chapter{Chapter 2. two} \\label{ch:test2-dm-two}\n'
                         '\\setcounter{chapter}{2}\n'
                         '\\chapter{Chapter 3. three} '
                         '\\label{ch:test3-dm-three}')


# html target

def test_collection_html(doctree):
    """Test the generation of html collections"""

    # The context body for the main document should only have the body of the
    # main document
    body_attr = settings.body_attr
    root1 = doctree.context[body_attr]

    key = ('<span class="body">'
             '<h2 id="ch:test-dm-one">'
               '<span class="label">Chapter 1. one</span>'
             '</h2>\n'
             '<span class="collection">\n'
               '<span class="body">'
                 '<h2 id="ch:test2-dm-two">'
                   '<span class="label">Chapter 2. two</span>'
                 '</h2>'
               '</span>\n'
               '<span class="body">'
                 '<h2 id="ch:test3-dm-three">'
                   '<span class="label">Chapter 3. three</span>'
                 '</h2>'
               '</span>'
             '</span>'
           '</span>\n')
    assert root1.html == key

    # Create a collections tag and see if it includes the subdocuments
    tag = Collection(name='collection', content='', attributes=tuple(),
                     context=doctree.context)

    key = ('<span class="collection">\n'
             '<span class="body">'
               '<h2 id="ch:test2-dm-two">'
                 '<span class="label">Chapter 2. two</span>'
               '</h2>'
             '</span>\n'
             '<span class="body">'
               '<h2 id="ch:test3-dm-three">'
                 '<span class="label">Chapter 3. three</span>'
               '</h2>'
             '</span>'
           '</span>\n')
    assert tag.html == key

    # Now remove the collection tag to the root document. The sub-documents
    # shouldn't be included
    src_filepath1 = doctree.context['src_filepath']
    src_filepath1.write_text("""
    ---
    targets: html
    include:
      test2.dm
      test3.dm
    ---
    @chapter{one}
    """)
    doctree.load()

    root1 = doctree.context[body_attr]

    key = """<span class="body"><h2 id="ch:main-dm-one">
<span class="label">Chapter 1. </span>one</h2></span>
"""
    key = ('<span class="body">'
             '<h2 id="ch:test-dm-one">'
               '<span class="label">Chapter 1. one</span>'
             '</h2>'
           '</span>\n')
    assert root1.html == key
