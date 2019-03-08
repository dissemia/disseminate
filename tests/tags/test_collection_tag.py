"""
Test the collection tag.
"""
import pytest

from disseminate import Document, settings
from disseminate.tags.collection import Collection


@pytest.fixture
def doc(tmpdir):
    """Setup a root document with two sub-documents"""
    # Create temp files
    src_path = tmpdir.join('src').mkdir()
    src_filepath1 = src_path.join('main.dm')
    src_filepath2 = src_path.join('sub1.dm')
    src_filepath3 = src_path.join('sub2.dm')

    # Write the files
    src_filepath1.write("""
    ---
    targets: html, tex
    include:
      sub1.dm
      sub2.dm
    ---
    @chapter{one}
    @collection""")
    src_filepath2.write("""
    @chapter{two}""")
    src_filepath3.write("""
    @chapter{three}""")

    # Load the root document
    doc = Document(src_filepath1, str(tmpdir))
    return doc


def test_collection_mtime(doc):
    """Test the calculation of the modification time for the collection tag."""
    # Get the mtimes for the 3 documents.
    docs = doc.documents_list()
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
    root1 = doc.context[body_attr]
    tag = root1.content[1]  # collection time
    assert tag.mtime == mtime3


def test_collection_selective_target(doc):
    """Test the collection tag when one of the sub-documents is not listed as
    a target."""
    # Unpack the subdocuments
    subdocs = doc.documents_list(only_subdocuments=True, recursive=True)
    assert len(subdocs) == 2
    subdoc1, subdoc2 = subdocs

    # Change the target for the 2nd subdocument
    src_filepath3 = subdoc2.context['src_filepath']
    src_filepath3.write_text("""
    ---
    targets: html
    ---
    @chapter{three}""")
    subdoc2.load()  # reload the document

    # Now try rendering the collection for the root document in tex. Since tex
    # is not a listed target for the 2nd sub-document, it's contents (chapter
    # three) should not be listed.
    body_attr = settings.body_attr
    root1 = doc.context[body_attr]
    assert root1.tex == ('\n\\setcounter{chapter}{1}\n'
                         '\\chapter{one} \\label{br:main-dm-one}\n\n\n'
                         '\\setcounter{chapter}{2}\n'
                         '\\chapter{two} \\label{br:sub1-dm-two}\n\n')


# default target

def test_collection_default(doc):
    """Test the generation of default collections"""

    # The context body for the main document should only have the body of the
    # main document
    body_attr = settings.body_attr
    root1 = doc.context[body_attr]
    assert root1.default == ('\none\n\n\n'
                             'two\n\n\n'
                             'three\n\n')


# tex target

def test_collection_tex(doc):
    """Test the generation of default collections"""

    # The context body for the main document should only have the body of the
    # main document
    body_attr = settings.body_attr
    root1 = doc.context[body_attr]
    assert root1.tex == ('\n\\setcounter{chapter}{1}\n'
                         '\\chapter{one} \\label{br:main-dm-one}\n\n\n'
                         '\\setcounter{chapter}{2}\n'
                         '\\chapter{two} \\label{br:sub1-dm-two}\n\n\n'
                         '\\setcounter{chapter}{3}\n'
                         '\\chapter{three} \\label{br:sub2-dm-three}\n\n')


# html target

def test_collection_html(doc):
    """Test the generation of html collections"""

    # The context body for the main document should only have the body of the
    # main document
    body_attr = settings.body_attr
    root1 = doc.context[body_attr]

    key = """<span class="body">
  <h1 id="br:main-dm-one">
    <span class="branch"><span class="number">1.</span> one</span>
  </h1>
  <span class="collection">
    <span class="body">
      <h1 id="br:sub1-dm-two">
        <span class="branch"><span class="number">2.</span> two</span>
      </h1>
    </span>
    <span class="body">
      <h1 id="br:sub2-dm-three">
        <span class="branch"><span class="number">3.</span> three</span>
      </h1>
    </span>
  </span>
</span>
"""

    assert root1.html == key

    # Create a collections tag and see if it includes the subdocuments
    tag = Collection(name='collection', content='', attributes=tuple(),
                     context=doc.context)

    key = """<span class="collection">
  <span class="body">
    <h1 id="br:sub1-dm-two">
      <span class="branch"><span class="number">2.</span> two</span>
    </h1>
  </span>
  <span class="body">
    <h1 id="br:sub2-dm-three">
      <span class="branch"><span class="number">3.</span> three</span>
    </h1>
  </span>
</span>
"""

    assert tag.html == key

    # Now remove the collection tag to the root document. The sub-documents
    # shouldn't be included
    src_filepath1 = doc.context['src_filepath']
    src_filepath1.write_text("""
    ---
    targets: html
    include:
      sub1.dm
      sub2.dm
    ---
    @chapter{one}
    """)
    doc.load()

    root1 = doc.context[body_attr]

    key = """<span class="body">
  <h1 id="br:main-dm-one">
    <span class="branch"><span class="number">1.</span> one</span>
  </h1>
</span>
"""

    assert root1.html == key
