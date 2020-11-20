"""
Tests for the 'init' CLI subcommand
"""
from click.testing import CliRunner

from disseminate.cli import main


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
    for line in ('Description',
                 'A textbook template that includes chapters',
                 'Template',
                 'books/tufte',
                 'Files',
                 'src/textbook.dm',
                 'src/chap1/chapter1.dm'):
        assert line in result.output
