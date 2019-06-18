"""
Test the PythonChecker class.
"""
import pytest

from disseminate.checkers import PythonChecker


@pytest.mark.environment
def test_python_checker_check_executables():
    """Test the check_executables method for the PythonChecker.

    This tests is for the environment to make sure it's setup and installed
    correctly. It is run before other tests.
    """
    checker = PythonChecker()
    checker.check_executables()
    executables = checker['executables']

    assert executables.available


@pytest.mark.environment
def test_python_checker_check_packages():
    """Test the check_packages_pip method for the PythonChecker.

    This tests is for the environment to make sure it's setup and installed
    correctly. It is run before other tests.
    """
    checker = PythonChecker()
    checker.check_packages()
    packages = checker['packages']
    assert packages.available
