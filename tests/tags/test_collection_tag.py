"""
Test the collection tag.
"""
import pytest

from disseminate import Document, settings
from disseminate.tags.collection import Collection


@pytest.fixture(scope='function')
def doctree(tmpdir, wait):
    """Setup a root document with two sub-documents"""
    # Create temp files
    src_path = tmpdir.join('src').mkdir()
    src_filepath1 = src_path.join('main.dm')
    src_filepath2 = src_path.join('sub1.dm')
    src_filepath3 = src_path.join('sub2.dm')

    # Write the files. A 1us sleep is placed between writes to offset the
    # mtimes of the 3 files for systems with at least 1 microsecond time
    # resolution
    src_filepath1.write("""
    ---
    targets: html, tex
    include:
      sub1.dm
      sub2.dm
    ---
    @chapter{one}
    @collection
    """)
    wait()  # sleep time offset needed for different mtimes

    src_filepath2.write("""
    @chapter{two}
    """)
    wait()  # sleep time offset needed for different mtimes

    src_filepath3.write("""
    @chapter{three}
    """)
    wait()  # sleep time offset needed for different mtimes

    # Load the root document
    doc = Document(src_filepath1, str(tmpdir))
    return doc


def test_collection_mtime(doctree):
    """Test the calculation of the modification time for the collection tag."""

    # Get the mtimes for the 3 documents.
    docs = doctree.documents_list()
    assert len(docs) == 3

    src_filepath1 = docs[0].context['src_filepath']
    src_filepath2 = docs[1].context['src_filepath']
    src_filepath3 = docs[2].context['src_filepath']

    mtime1 = src_filepath1.stat().st_mtime
    mtime2 = src_filepath2.stat().st_mtime
    mtime3 = src_filepath3.stat().st_mtime
    assert mtime1 < mtime2 < mtime3

    # Get the collection tag from the root document. Its mtime should correspond
    # to the latest one: mtime3.
    body_attr = settings.body_attr
    root1 = doctree.context[body_attr]
    tag = root1.content[1]  # collection time
    assert tag.mtime == mtime3


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
    assert root1.tex == ('\\setcounter{chapter}{1}\n'
                         '\\chapter{Chapter 1. one} \\label{ch:main-dm-one}\n'
                         '\\setcounter{chapter}{2}\n'
                         '\\chapter{Chapter 2. two} \\label{ch:sub1-dm-two}')


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
    assert root1.tex == ('\\setcounter{chapter}{1}\n'
                         '\\chapter{Chapter 1. one} \\label{ch:main-dm-one}\n'
                         '\\setcounter{chapter}{2}\n'
                         '\\chapter{Chapter 2. two} \\label{ch:sub1-dm-two}\n'
                         '\\setcounter{chapter}{3}\n'
                         '\\chapter{Chapter 3. three} '
                         '\\label{ch:sub2-dm-three}')


# html target

def test_collection_html(doctree):
    """Test the generation of html collections"""

    # The context body for the main document should only have the body of the
    # main document
    body_attr = settings.body_attr
    root1 = doctree.context[body_attr]

    key = """<span class="body">
  <h2 id="ch:main-dm-one"><span class="label">Chapter 1. </span>one</h2>
  <span class="collection">
<span class="body"><h2 id="ch:sub1-dm-two"><span class="label">Chapter 2. </span>two</h2></span>
<span class="body"><h2 id="ch:sub2-dm-three"><span class="label">Chapter 3. </span>three</h2></span></span>
</span>
"""
    assert root1.html == key

    # Create a collections tag and see if it includes the subdocuments
    tag = Collection(name='collection', content='', attributes=tuple(),
                     context=doctree.context)

    key = """<span class="collection">
<span class="body"><h2 id="ch:sub1-dm-two"><span class="label">Chapter 2. </span>two</h2></span>
<span class="body"><h2 id="ch:sub2-dm-three"><span class="label">Chapter 3. </span>three</h2></span></span>
"""
    assert tag.html == key

    # Now remove the collection tag to the root document. The sub-documents
    # shouldn't be included
    src_filepath1 = doctree.context['src_filepath']
    src_filepath1.write_text("""
    ---
    targets: html
    include:
      sub1.dm
      sub2.dm
    ---
    @chapter{one}
    """)
    doctree.load()

    root1 = doctree.context[body_attr]

    key = """<span class="body">
  <h2 id="ch:main-dm-one"><span class="label">Chapter 1. </span>one</h2>
</span>
"""
    assert root1.html == key
