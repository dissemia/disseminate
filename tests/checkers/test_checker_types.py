"""Test the Checker types."""
import pytest

from disseminate.checkers.types import Any, All


def test_checker_type_flatten():
    """Test the flatten iterator of checkers."""

    # Create a SoftwareDependencyList tree.
    required = All('tex',
                   Any('executables',
                       'pdflatex', 'xelatex'),
                   All('packages',
                       'package1', 'package2')
                   )

    flat = required.flatten()
    assert flat[0] == (1, required[0])
    assert flat[1] == (2, required[0][0])
    assert flat[2] == (2, required[0][1])
    assert flat[3] == (1, required[1])
    assert flat[4] == (2, required[1][0])
    assert flat[5] == (2, required[1][1])
    assert len(flat) == 6


def test_checker_type_available():
    """Test the available method of Checker types."""

    # Create a SoftwareDependencyList tree.
    required = All('tex',
                   Any('executables',
                       'pdflatex', 'xelatex'),
                   All('packages',
                       'package1', 'package2')
                   )

    # The availabilities are currently all set to None
    assert required.available is False

    # Test the sub-dependencies
    executables = required['executables']
    packages = required['packages']

    assert executables.available is False
    assert packages.available is False

    # Set the software dependencies
    executables['pdflatex'].available = True
    assert executables.available is True  # Any matches

    packages['package1'].available = True
    assert packages.available is False  # All not matched

    packages['package2'].available = True
    assert packages.available is True  # All matched

    assert required.available is True  # All matched

    # Test list-like properties
    assert len(required) == 2
    assert len(executables) == 2
    assert len(packages) == 2

    assert 'executables' in required
    assert 'missing' not in required

    with pytest.raises(KeyError):
        required['missing']

    # Test keys
    assert required.keys() == ['executables', 'packages']
    assert executables.keys() == ['pdflatex', 'xelatex']
    assert packages.keys() == ['package1', 'package2']
