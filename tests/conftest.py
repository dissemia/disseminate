import copy
import io
import os
import shutil
from time import sleep
from collections import namedtuple
import pathlib

import pytest

from disseminate.context import BaseContext
from disseminate.attributes import Attributes
from disseminate.paths import SourcePath, TargetPath
from disseminate.document import Document
from disseminate.builders import Environment
from disseminate.server.server import create_app


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
    src_filepath.touch()

    # Create a new environment so that context is stored on the env instead as
    # weakref (default)
    class TestEnvironment(Environment):
        context = None

    env = TestEnvironment(src_filepath=src_filepath, target_root=target_root)
    return env


@pytest.fixture
def load_example(env_cls, tmpdir):
    """Return a function that returns a document from an example path"""
    # Setup the paths
    tmpdir = pathlib.Path(tmpdir)
    target_root = TargetPath(target_root=tmpdir)

    def _load_example(example_path):
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


# server fixtures

@pytest.yield_fixture
def app(tmpdir):
    project_path = tmpdir.join('example7')
    shutil.copytree('tests/document/example7', project_path)
    app = create_app(in_path=str(project_path))
    app.config['PROJECTPATH'] = project_path
    yield app


@pytest.fixture
def test_client(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))