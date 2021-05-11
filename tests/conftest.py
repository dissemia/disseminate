import copy
import io
import os
import shutil
from time import sleep
from collections import namedtuple
import pathlib
import xml.dom.minidom
import zipfile
import logging

import pytest
import regex
import lxml.etree

from disseminate.context import BaseContext
from disseminate.attributes import Attributes
from disseminate.paths import SourcePath, TargetPath
from disseminate.document import Document
from disseminate.builders import Environment


def pytest_collection_modifyitems(config, items):
    """Run environment tests first.

    The environment tests check to see if everything needed for the tests is
    properly installed and configured, like pdflatex.
    """
    # Reorder the items to list the tests marked with 'environment' first.
    env_items = [item for item in items if
                 item.get_closest_marker('environment') is not None]
    nonenv_items = [item for item in items if
                 item.get_closest_marker('environment') is None]

    items.clear()
    items += env_items + nonenv_items


@pytest.fixture(scope='session')
def wait():
    """A filesystem sleep time offset for filesystem operations.

    In some tests, files are written sequentially but need to have sequential
    modification times (mtimes) from each other. For lower time resolution
    filesystems, the nanoseconds taken to write sequential files may not be
    enough to generate files with sequentially increasing mtimes. This sleep
    function can be used to offset write operations to files.
    """
    system = os.uname()
    if system.sysname == 'Linux':
        def _wait():
            sleep(10E-3)  # 10ms
    else:
        def _wait():
            pass
    return _wait


@pytest.fixture(scope='function')
def attributes_cls():
    """Returns a copy of the attributes class."""
    CopyAttributes = copy.deepcopy(Attributes)
    return CopyAttributes


@pytest.fixture(scope='function')
def mocktag_cls():
    """Returns a mock Tag class for creating tag objects from namedtuples."""
    # Create a mock tag class
    MockTag = namedtuple('MockTag', 'name attributes content context')
    return MockTag


@pytest.fixture
def env_cls():
    """The build environment class"""
    return Environment


@pytest.fixture
def env(tmpdir):
    """A build environment"""
    # Setup the paths
    tmpdir = pathlib.Path(tmpdir)
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=tmpdir, subpath='test.dm')
    src_filepath.write_text("""
    ---
    targets: html, xhtml, tex, pdf
    ---
    """)

    # Create a new environment so that context is stored on the env instead as
    # weakref (default)
    class TestEnvironment(Environment):
        context = None

    env = TestEnvironment(src_filepath=src_filepath, target_root=target_root)
    return env


@pytest.fixture(scope='function')
def doc(env):
    """Returns a test document"""
    return env.root_document


@pytest.fixture(scope='function')
def doctree(env):
    """Returns a document that is a document tree with 2 sub-documents."""
    root_doc = env.root_document
    project_root = env.project_root

    # Setup the paths
    src_filepath1 = root_doc.src_filepath
    src_filepath2 = SourcePath(project_root=project_root, subpath='test2.dm')
    src_filepath3 = SourcePath(project_root=project_root, subpath='test3.dm')

    # Create the source file
    src_filepath1.write_text("""
    ---
    include:
       test2.dm
       test3.dm
    ---
    """)
    src_filepath2.touch()
    src_filepath3.touch()

    # Reload and return the document
    root_doc.load()
    return root_doc


@pytest.fixture(scope='function')
def doc_cls():
    return Document


@pytest.fixture(scope='function')
def context(doc):
    return doc.context


@pytest.fixture(scope='function')
def context_cls():
    """Returns a copy of the context class."""
    CopyContext = copy.deepcopy(BaseContext)
    return CopyContext


@pytest.fixture
def load_example(env_cls, tmpdir):
    """Return a function that returns a document from an example path"""
    # Setup the paths
    tmpdir = pathlib.Path(tmpdir)
    target_root = TargetPath(target_root=tmpdir)

    def _load_example(example_path, cp_src=False):
        if cp_src:
            src_dir = tmpdir / 'src'
            src_dir.mkdir()
            shutil.copy(example_path, src_dir)
            example_path = src_dir / example_path.name

        env = env_cls(example_path, target_root=target_root)
        return env.root_document
    return _load_example


@pytest.fixture
def url_request(monkeypatch):
    """Mock requests to url.requests so that responses inserted in the
    self.responses dict are returned instead of polling the internet."""

    class MockRequest(object):
        responses = None

        def __init__(self):
            self.responses = dict()

        def urlopen(self, url):
            # Get the url response
            response = self.responses[url]

            # Convert to a text stream
            return io.BytesIO(response.encode())

    import urllib
    mockrequest = MockRequest()
    monkeypatch.setattr(urllib, 'request', mockrequest)

    return mockrequest


@pytest.fixture
def a_in_b():
    """Test whether items in 'a' are in 'b'."""
    def _a_in_b(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            return (all(k in b for k in a.keys()) and
                    all(a[k] == b[k] for k in a.keys()))
        return False

    return _a_in_b


# Tests for formats

@pytest.fixture
def is_pdf():
    """Tests whether the file is a pdf file
    """
    def _is_pdf(pdf_filepath):
        # Retrieve the lines from the file
        with open(pdf_filepath, 'rb') as file:
            chunk = file.read(512)
            return chunk.startswith(b'%PDF-')
    return _is_pdf


@pytest.fixture
def is_svg():
    """Returns true if the given filepath is a valid svg file."""
    def _is_svg(filepath):
        # Load the svg file as xml
        with xml.dom.minidom.parse(str(filepath)) as dom:
            # See if there are svg tags in the xml
            return any(node.tagName == 'svg' or node.tagName == 'SVG'
                       for node in dom.childNodes)
    return _is_svg


@pytest.fixture
def svg_dims():
    """Checks whether the svg filepath matches the given width and/or the
    given height."""
    def _svg_dims(filepath, width=None, height=None, abs=0.1):
        # Load the svg file as xml
        with xml.dom.minidom.parse(str(filepath)) as dom:
            # find the svg tag
            svg_nodes = [node for node in dom.childNodes
                         if node.tagName == 'svg']
            if len(svg_nodes) == 0:
                return None

            svg_node = svg_nodes[0]
            svg_width = svg_node.getAttribute('width') or None
            svg_height = svg_node.getAttribute('height') or None
            print('svg dimensions:', svg_width, svg_height)

            is_matched = True
            for dim, svg_dim in ((width, svg_width), (height, svg_height)):
                if dim is None:  # skip test if not specified
                    continue

                if svg_dim is None:  # svg doesn't have this dimension
                    is_matched &= False
                    continue

                if 'px' in svg_dim:
                    svg_dim = float(svg_dim.strip('px'))
                    dim = float(dim.strip('px'))

                elif 'pt' in svg_dim:
                    svg_dim = float(svg_dim.strip('pt'))
                    dim = float(dim.strip('pt'))

                is_matched &= (svg_dim == pytest.approx(dim, abs=abs))

            return is_matched
    return _svg_dims


xml_parser = None
@pytest.fixture
def is_xml():
    """Tests a string for valid xml.

    Raises
    ------
    :exc:`lxml.etree.XMLSyntaxError`
        If a syntax error was found.
    """
    global xml_parser
    if xml_parser is None:
        xml_parser = lxml.etree.XMLParser()

    def _is_xml(string):
        string = regex.sub(r'&[\#\w]\w*;', '', string)  # strip/ignore entities
        if string.strip():  # only look a non-empty stringss
            lxml.etree.fromstring(string, xml_parser)
        return True

    return _is_xml


@pytest.fixture
def cmp_epub():
    """Compare the files from 2 different epub files.

    Parameters
    ----------
    epubA : Union[str, obj:`pathlib.Path`]
        The filepath to the first epub file to compare
    epubB : Union[str, obj:`pathlib.Path`]
        The filepath to the second epub file to compare
    exclude_crc : Tuple[str]
        A tuple of filenames for files to not compare the CRC hashes.

    Returns
    -------
    same : bool
        True, if the 2 files are the same, False if they aren't.
    """
    def _cmp_epub(epubA, epubB, exclude_crc=('xhtml/content.opf',)):
        with zipfile.ZipFile(epubA) as fileA, zipfile.ZipFile(epubB) as fileB:
            # Get the zipinfos for file A
            zipinfosA = {z.filename: z for z in fileA.infolist()}
            zipinfosB = {z.filename: z for z in fileB.infolist()}

            # Find files in A but not in B and files in B bot not in A
            in_A_not_B = zipinfosA.keys() - zipinfosB.keys()
            in_B_not_A = zipinfosB.keys() - zipinfosA.keys()
            if in_A_not_B:
                msg = "The files '{}' are in '{}' but not '{}"
                logging.error(msg.format(in_A_not_B, epubA, epubB))
                return False
            if in_B_not_A:
                msg = "The files '{}' are in '{}' but not '{}"
                logging.error(msg.format(in_B_not_A, epubB, epubA))
                return False

            # At this point, the files in epubA match those in epubB
            # Compare the CRCs
            for filename in zipinfosA.keys():
                # Skip CRC check if filename is in exclude_crc
                if filename in exclude_crc:
                    continue

                zipinfoA = zipinfosA[filename]
                zipinfoB = zipinfosB[filename]

                if zipinfoA.CRC != zipinfoB.CRC:
                    msg = ("CRCs for file '{}' do not match between '{}' and "
                           "'{}'")
                    logging.error(msg.format(filename, epubA, epubB))
                    return False

        # Survived the gauntlet. The two files match.
        return True

    return _cmp_epub
