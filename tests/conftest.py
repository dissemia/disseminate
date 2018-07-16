import copy
import pytest

from disseminate.context import BaseContext


@pytest.fixture
def context_cls():
    """Returns a copy of the context class."""
    CopyContext = copy.deepcopy(BaseContext)
    return CopyContext