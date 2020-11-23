"""
Tests for the 'init' CLI subcommand
"""
import pathlib

from click.testing import CliRunner

from disseminate.cli import main
from disseminate.cli.init import is_empty


def test_cli_is_empty(tmpdir):
    """Test the is_empty function"""
    # Check an empty directory
    assert is_empty(tmpdir)

    # Make the directory non-empty
    test_file = pathlib.Path(tmpdir) / 'test'
    test_file.touch()

    assert not is_empty(tmpdir)
    assert not is_empty(test_file)


def test_cli_init_listing():
    """Test the CLI init subcommand for listing project starters"""
    runner = CliRunner()

    # Retrieve the listing
    result = runner.invoke(main, ['init'])

    assert result.exit_code == 0

    # Check that some of the starters are present
    assert 'books/tufte/textbook1' in result.output


def test_cli_init_detailed():
    """Test the CLI init subcommand for showing detailed information on a
    project starter."""
    runner = CliRunner()

    # Retrieve the detailed information
    result = runner.invoke(main, ['init', 'books/tufte/textbook1', '--info'])

    assert result.exit_code == 0

    # Check the detailed information
    for line in ('books/tufte/textbook1',
                 'Description',
                 'A textbook template that includes chapters',
                 'Template',
                 'books/tufte',
                 'Files',
                 'src/textbook.dm',
                 'src/chap1/chapter1.dm'):
        assert line in result.output


def test_cli_init_missing():
    """Test the CLI init subcommand for a project starter name that does not
    exist."""
    runner = CliRunner()

    # Retrieve the detailed information
    result = runner.invoke(main, ['init', 'books/missing', '--info'])

    assert result.exit_code == 2
    assert ("Error: Invalid value: The project starter with name "
            "'books/missing' could not be found") in result.output


def test_cli_init_clone(tmpdir):
    """Test the CLI init subcommand to clone a project starter."""
    tmpdir = pathlib.Path(tmpdir)
    runner = CliRunner()

    # Clone the project starter
    assert is_empty(tmpdir)
    result = runner.invoke(main, ['init', 'books/tufte/textbook1', '-o',
                                  tmpdir])
    assert result.exit_code == 0

    # Check the cloned directory
    assert not is_empty(tmpdir)
    assert (tmpdir / 'src' / 'textbook.dm').is_file()

    # Try it again. A prompt should show up to ask whether to write to a
    # non-empty directory
    result = runner.invoke(main, ['init', 'books/tufte/textbook1', '-o',
                                  tmpdir])
    assert result.exit_code == 0
    print(result.output)
    assert all(i in result.output for i in ("The directory",
                                            str(tmpdir.name),
                                            "is not empty"))

