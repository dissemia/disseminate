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
    assert len(target_builders) == 4

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

    txt_builders = [b for b in target_builders
                    if b.__class__.__name__ == 'TxtBuilder']
    assert txt_builders

    # Check the paths
    tp_html = TargetPath(target_root=tmpdir, target='html',
                         subpath='dummy.html')
    assert html_builders[0].outfilepath == tp_html

    tp_tex = TargetPath(target_root=tmpdir, target='tex', subpath='dummy.tex')
    assert tex_builders[0].outfilepath == tp_tex

    tp_pdf = TargetPath(target_root=tmpdir, target='pdf', subpath='dummy.pdf')
    assert pdf_builders[0].outfilepath == tp_pdf

    tp_txt = TargetPath(target_root=tmpdir, target='txt', subpath='dummy.txt')
    assert txt_builders[0].outfilepath == tp_txt


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
    assert env.build() == 'done'

    tp_html = TargetPath(target_root=tmpdir, target='html',
                         subpath='dummy.html')
    tp_key = TargetPath(target_root='tests/builders/examples/ex3',
                        subpath='dummy.html')
    assert tp_html.is_file()
    assert tp_html.read_text() == tp_key.read_text()

    tp_txt = TargetPath(target_root=tmpdir, target='txt', subpath='dummy.txt')
    tp_key = TargetPath(target_root='tests/builders/examples/ex3',
                        subpath='dummy.txt')
    assert tp_txt.is_file()
    assert tp_txt.read_text() == tp_key.read_text()

    tp_tex = TargetPath(target_root=tmpdir, target='tex', subpath='dummy.tex')
    tp_key = TargetPath(target_root='tests/builders/examples/ex3',
                        subpath='dummy.tex')
    assert tp_tex.is_file()
    assert tp_tex.read_text() == tp_key.read_text()

    tp_pdf = TargetPath(target_root=tmpdir, target='pdf', subpath='dummy.pdf')
    assert tp_pdf.is_file()
    assert b'PDF' in tp_pdf.read_bytes()


def test_create_environments():
    """Test the create_environments method."""
    # Create environments from the tests directory

    # 1. Check a basic example with and without relative paths (ex3)
    # │   ├── dummy.dm
    # │   ├── dummy.html
    # │   ├── dummy.tex
    # │   └── dummy.txt
    for root_path in ('tests/builders/examples',
                      'tests/builders/examples/ex1/..',):
        envs = Environment.create_environments(root_path=root_path)
        env_ex3 = [env for env in envs if env.project_root.match('ex3')][0]
        assert env_ex3.target_root.resolve().match('builders/examples/ex3')
        src_filepath = env_ex3.root_document.src_filepath
        assert src_filepath.project_root.resolve().match('builders/examples/'
                                                         'ex3')
        assert str(src_filepath.subpath) == 'dummy.dm'

    # 2. Check an example in which the project_root is in a src file (ex5)│  
    # └── src
    # │       ├── index.dm
    # │       └── media
    # │           └── images
    # │               └── NMR
    # │                   └── hsqc_bw.pdf
    envs = Environment.create_environments(root_path='tests/builders/examples')
    env_ex5 = [env for env in envs if env.project_root.match('ex5/src')][0]

    assert str(env_ex5.project_root) == 'tests/builders/examples/ex5/src'
    assert str(env_ex5.target_root) == 'tests/builders/examples/ex5'
    src_filepath = env_ex5.root_document.src_filepath
    assert str(src_filepath.project_root) == 'tests/builders/examples/ex5/src'
    assert str(src_filepath.subpath) == 'index.dm'

    # 3. Check an example with a nested directory structure (ex6)
    #     ├── index.dm
    #     ├── sub1
    #     │   └── index.dm
    #     ├── sub2
    #     │   ├── index.dm
    #     │   └── subsub2
    #     │       └── index.dm
    #     └── sub3
    #         └── index.dm
    envs = Environment.create_environments(root_path='tests/builders/examples')
    env_ex6 = [env for env in envs if env.project_root.match('ex6')][0]

    # None of the subdirectories should have an environment: just the root
    assert len([env for env in envs if env.project_root.match('sub1')]) == 0
    assert len([env for env in envs if env.project_root.match('sub2')]) == 0
    assert len([env for env in envs if env.project_root.match('sub3')]) == 0
    assert len([env for env in envs if env.project_root.match('subsub2')]) == 0

    assert str(env_ex6.project_root) == 'tests/builders/examples/ex6'
    assert str(env_ex6.target_root) == 'tests/builders/examples/ex6'
    src_filepath = env_ex6.root_document.src_filepath
    assert str(src_filepath.project_root) == 'tests/builders/examples/ex6'
    assert str(src_filepath.subpath) == 'index.dm'

    # There should be 4 subdocuments
    num = len(env_ex6.root_document.documents_list(only_subdocuments=True,
                                                   recursive=True))
    assert num == 4

    # 4. Try an example in which the src_filepath for the root_document is
    #    specified directly.
    envs = Environment.create_environments(root_path='tests/builders/examples/'
                                                     'ex6/index.dm')
    env_ex6 = [env for env in envs if env.project_root.match('ex6')][0]

    assert str(env_ex6.project_root) == 'tests/builders/examples/ex6'
    assert str(env_ex6.target_root) == 'tests/builders/examples/ex6'
    src_filepath = env_ex6.root_document.src_filepath
    assert str(src_filepath.project_root) == 'tests/builders/examples/ex6'
    assert str(src_filepath.subpath) == 'index.dm'

