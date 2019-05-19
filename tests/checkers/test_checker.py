"""Test for the Checker base class."""
import pytest

from disseminate.checkers import Checker, All, Any


def test_checker_find_executables():
    """Test the find_executables method."""

    # A python executable should be available
    path = Checker.find_executable('python')
    assert path is not None

    # Try a missing executable
    path = Checker.find_executable('missing4321')
    assert path is None


def test_checker_check_executables():
    """Test the check_required function."""

    # Setup a checker with a required_executable
    checker = Checker('test')

    # No error raised
    checker.check_executables()

    # Add executables, one present and one missing, all must be present
    checker = Checker('test',
                      All('executables',
                          'missing4321', 'python'))
    checker.check_executables()
    executables = checker['executables']

    assert executables['missing4321'].available is False
    assert executables['python'].available is True
    assert executables.available is False  # Not all available
    assert checker.available is False

    # Add executables, one present and one missing, any must be present
    checker = Checker('test',
                      Any('executables',
                          'missing4321', 'python'))
    checker.check_executables()
    executables = checker['executables']

    assert executables['missing4321'].available is False
    assert executables['python'].available is True
    assert executables.available is True  # any are available
    assert checker.available is True
