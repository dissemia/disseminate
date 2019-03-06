"""
Test the img tag.
"""
from disseminate.ast import process_ast
from disseminate.dependency_manager import DependencyManager
from disseminate import SourcePath, TargetPath


def test_img_attribute(tmpdir, context_cls):
    """Test the correct processing of attributes in an image tag."""
    project_root = SourcePath(project_root='tests/tags/img_example1')
    target_root = TargetPath(target_root=tmpdir)

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(project_root=project_root,
                            target_root=target_root)
    context = context_cls(dependency_manager=dep)

    # Generate the markup
    src = "@img[width=100]{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context)

    assert root.name == 'img'
    assert root.attributes == (('width', '100'),)


# html target

def test_img_html(tmpdir, context_cls):
    """Test the handling of html with the img tag."""
    # Setup the paths
    project_root = SourcePath(project_root='tests/tags/img_example1')
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(project_root=project_root,
                            target_root=target_root)

    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    paths = [project_root]
    context = context_cls(dependency_manager=dep, src_filepath=src_filepath,
                          paths=paths)

    # Generate the markup
    src = "@img{sample.pdf}"

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">\n  '
    root_end = '\n</span>\n'

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context)

    assert root.html == '<img src="/html/sample.svg"/>\n'

    # Now test an html-specific attribute
    # Generate the markup
    src = "@img[html.width=100 tex.height=20]{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context)

    assert root.html == '<img width="100" src="/html/sample.svg"/>\n'


# tex targets

def test_img_tex(tmpdir, context_cls):
    """Test the handling of LaTeX with the img tag."""
    project_root = SourcePath(project_root='tests/tags/img_example1')
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(project_root=project_root,
                            target_root=target_root)

    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    paths = [project_root]
    context = context_cls(dependency_manager=dep, src_filepath=src_filepath,
                          paths=paths)

    # Generate the markup
    src = "@img{sample.pdf}"
    tex = "\\includegraphics{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=context)

    # Remove the root tag
    root_tex = root.tex
    assert root_tex == tex

    # Now test an tex-specific attribute
    # Generate the markup
    src = "@img[html.width=100 tex.height=20]{sample.pdf}"
    tex = "\\includegraphics[height=20]{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=context)

    # Remove the root tag
    root_tex = root.tex
    assert root_tex == tex
