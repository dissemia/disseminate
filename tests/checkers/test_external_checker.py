"""Tests for external dependency checkers."""
import pytest

from disseminate.checkers import ImageExtChecker


@pytest.mark.environment
def test_image_external_checker_check_executables():
    """Check the executables for the image external checker."""
    checker = ImageExtChecker()
    checker.check_executables()
    executables = checker['executables']

    assert executables.available
