import copy
import pytest
import io
from collections import namedtuple

from disseminate.context import BaseContext
from disseminate.attributes import Attributes
from disseminate.paths import SourcePath, TargetPath
from disseminate.document import Document


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


@pytest.fixture(scope='function')
def context_cls():
    """Returns a copy of the context class."""
    CopyContext = copy.deepcopy(BaseContext)
    return CopyContext


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


@pytest.fixture(scope='function')
def doc(tmpdir):
    """Returns a test document"""
    # Setup the paths
    src_filepath = SourcePath(project_root=tmpdir, subpath='test.dm')
    target_root = TargetPath(target_root=tmpdir)

    # Create the source file
    src_filepath.touch()

    # Create and return the document
    return Document(src_filepath=src_filepath, target_root=target_root)


@pytest.fixture(scope='function')
def doctree(tmpdir):
    """Returns a document that is a document tree with 2 sub-documents."""
    # Setup the paths
    src_filepath1 = SourcePath(project_root=tmpdir, subpath='test1.dm')
    src_filepath2 = SourcePath(project_root=tmpdir, subpath='test2.dm')
    src_filepath3 = SourcePath(project_root=tmpdir, subpath='test3.dm')
    target_root = TargetPath(target_root=tmpdir)

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

    # Create and return the document
    return Document(src_filepath=src_filepath1, target_root=target_root)


@pytest.fixture(scope='function')
def doc_cls():
    return Document


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
