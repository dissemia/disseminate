"""
Tests for the build environment.
"""
from disseminate.builders.environment import Environment
from disseminate.paths import SourcePath, TargetPath


def test_environment_setup1(tmpdir):
    """Test the setup of an environment using example1"""
    # 1. tests/builders/examples/ex3/
    # ├── dummy.dm
    # ├── dummy.html
    # └── dummy.tex
    src_filepath = SourcePath(project_root='tests/builders/examples/ex3',
                              subpath='dummy.dm')
    env = Environment(src_filepath=src_filepath, target_root=tmpdir)

    target_builders = set(env.collect_target_builders())
    assert len(target_builders) == 3

    # Check that the correct builders were inserted in the context
    html_builders = [b for b in target_builders
                     if b.__class__.__name__ == 'HtmlBuilder']
    assert html_builders

    tex_builders = [b for b in target_builders
                     if b.__class__.__name__ == 'TexBuilder']
    assert tex_builders

    pdf_builders = [b for b in target_builders
                    if b.__class__.__name__ == 'PdfBuilder']
    assert pdf_builders
    assert pdf_builders[0]._tex_builder == tex_builders[0]

    # Check the paths
    tp_html = TargetPath(target_root=tmpdir, target='html',
                         subpath='dummy.html')
    assert html_builders[0].outfilepath == tp_html

    tp_tex = TargetPath(target_root=tmpdir, target='tex', subpath='dummy.tex')
    assert tex_builders[0].outfilepath == tp_tex

    tp_pdf = TargetPath(target_root=tmpdir, target='pdf', subpath='dummy.pdf')
    assert pdf_builders[0].outfilepath == tp_pdf


def test_environment_simple_build1(tmpdir):
    """Test an environment simple build from example 1"""
    # 1. tests/builders/examples/ex3/
    # ├── dummy.dm
    # ├── dummy.html
    # └── dummy.tex
    src_filepath = SourcePath(project_root='tests/builders/examples/ex3',
                              subpath='dummy.dm')
    env = Environment(src_filepath=src_filepath, target_root=tmpdir)

    # Try the build and check the generated files
    env.build()

    tp_html = TargetPath(target_root=tmpdir, target='html',
                         subpath='dummy.html')
    tp_key = TargetPath(target_root='tests/builders/examples/ex3',
                        subpath='dummy.html')
    assert tp_html.is_file()
    assert tp_html.read_text() == tp_key.read_text()

    tp_tex = TargetPath(target_root=tmpdir, target='tex', subpath='dummy.tex')
    tp_key = TargetPath(target_root='tests/builders/examples/ex3',
                        subpath='dummy.tex')
    assert tp_tex.is_file()
    assert tp_tex.read_text() == tp_key.read_text()

    tp_pdf = TargetPath(target_root=tmpdir, target='pdf', subpath='dummy.pdf')
    assert tp_pdf.is_file()
    assert b'PDF' in tp_pdf.read_bytes()
