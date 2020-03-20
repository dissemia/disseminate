"""
Tests for the build environment.
"""
from disseminate.builders.environment import Environment
from disseminate.paths import SourcePath, TargetPath


def test_environment_simple_build(tmpdir):
    """Test an environment simple build"""
    # 1. tests/builders/target_builders/example1/
    # ├── dummy.dm
    # ├── dummy.html
    # └── dummy.tex
    src_filepath = SourcePath(project_root='tests/builders/target_builders/'
                                           'example1/',
                              subpath='dummy.dm')
    env = Environment(src_filepath=src_filepath, target_root=tmpdir)

    # Try the build and check the generated files
    env.build()

    tp_html = TargetPath(target_root=tmpdir, target='html',
                         subpath='dummy.html')
    tp_key = TargetPath(target_root='tests/builders/target_builders/example1',
                         subpath='dummy.html')
    assert tp_html.is_file()
    assert tp_html.read_text() == tp_key.read_text()

    tp_tex = TargetPath(target_root=tmpdir, target='tex',
                        subpath='dummy.tex')
    tp_key = TargetPath(target_root='tests/builders/target_builders/example1',
                        subpath='dummy.tex')
    assert tp_tex.is_file()
    assert tp_tex.read_text() == tp_key.read_text()
