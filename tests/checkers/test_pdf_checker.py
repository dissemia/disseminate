"""
Test the TexChecker class.
"""
import pytest

from disseminate.checkers import PdfChecker


@pytest.mark.environment
def test_pdf_checker_check_executables():
    """Test the check_packages_kpsewhich method for the TexChecker.

    This tests is for the environment to make sure it's setup and installed
    correctly. It is run before other tests.
    """
    checker = PdfChecker()
    checker.check_executables()
    executables = checker['executables']
    compilers = executables['compilers']

    assert compilers.available
    assert executables.available


@pytest.mark.environment
def test_pdf_checker_check_packages():
    """Test the check_packages method for the TexChecker.

    This tests is for the environment to make sure it's setup and installed
    correctly. It is run before other tests.
    """
    checker = PdfChecker()
    checker.check_packages()
    packages = checker['packages']
    fonts = checker['fonts']

    assert packages.available
    assert fonts.available


@pytest.mark.environment
def test_pdf_checker_check_classes():
    """Test the check_classes method for the TexChecker.

    This tests is for the environment to make sure it's setup and installed
    correctly. It is run before other tests.
    """
    checker = PdfChecker()
    checker.check_classes()
    classes = checker['classes']
    assert classes.available

    # The article and report classes should be installed
    assert classes['article'].available
    assert classes['report'].available


def test_pdf_checker_check_packages_kpsewhich():
    """Test the check_packages_kpsewhich method for the TexChecker.
    """
    checker = PdfChecker()
    checker.check_packages_kpsewhich()
    packages = checker['packages']
    assert packages.available
