"""
Test the 'render' subcommand from the CLI.
"""
from pathlib import Path
import shutil

from click.testing import CliRunner

from disseminate.cli import main


def test_cli_render_simple_document(tmpdir):
    """Test the CLI render subcommand with a simple document."""
    # Setup the CLI runner and paths
    tmpdir = Path(tmpdir)
    runner = CliRunner()

    # 1. Use 'tests/document/example1' as an example. It contains a single
    #    source file 'dummy.dm' and 2 answer key targets: 'dummy.html' and
    #    'dummy.tex'. Write the generated files an compare them to the
    #    answer keys.
    tmpdir2 = tmpdir / 'test2'
    tmpdir2.mkdir()
    project_root = tmpdir2 / 'src'
    project_root.mkdir()

    src_filepath = project_root / 'dummy.dm'
    shutil.copy('tests/document/example1/dummy.dm', str(src_filepath))

    # run the command
    result = runner.invoke(main, ['render', '-i', str(src_filepath)])

    # Make sure the command was successfully run
    assert result.exit_code == 0

    # Check the generated files.
    target_html = tmpdir2 / 'html' / 'dummy.html'
    assert target_html.is_file()
    assert target_html.stat().st_size > 0

    target_tex = tmpdir2 / 'tex' / 'dummy.tex'
    assert target_tex.is_file()
    assert target_tex.stat().st_size > 0
