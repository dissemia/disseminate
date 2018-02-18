"""
Test the img tag.
"""
from disseminate.ast import process_ast
from disseminate.dependency_manager import DependencyManager


def test_img_attribute(tmpdir):
    """Test the correct processing of attributes in an image tag."""
    target_root = str(tmpdir)

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(project_root='tests/tags/img_example1',
                            target_root=target_root)
    global_context = {'_dependencies': dep}

    # Generate the markup
    src = "@img[width=100]{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast([src], global_context=global_context)

    img = root.content[1]
    assert img.name == 'img'
    assert img.attributes == (('width', '100'),)


def test_img_html(tmpdir):
    """Test the handling of html with the img tag."""
    target_root = str(tmpdir)

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(project_root='tests/tags/img_example1',
                            target_root=target_root)
    global_context = {'_dependencies': dep}

    # Generate the markup
    src = "@img{sample.pdf}"
    html = '<img src="/sample.svg"/>'  # create an svg by default

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">'
    root_end = '</span>\n'

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast([src], global_context=global_context)

    # Remove the root tag
    root_html = root.html()

    # Remove the root tag
    root_html = root_html[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    assert root_html == html

    # Now test an html-specific attribute
    # Generate the markup
    src = "@img[html.width=100 tex.height=20]{sample.pdf}"
    html = '<img width="100" src="/sample.svg"/>'  # create an svg by default

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">'
    root_end = '</span>\n'

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast([src], global_context=global_context)

    # Remove the root tag
    root_html = root.html()

    # Remove the root tag
    root_html = root_html[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end
    assert root_html == html


def test_img_tex(tmpdir):
    """Test the handling of LaTeX with the img tag."""
    target_root = str(tmpdir)

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(project_root='tests/tags/img_example1',
                            target_root=target_root)
    global_context = {'_dependencies': dep}

    # Generate the markup
    src = "@img{sample.pdf}"
    tex = "\\includegraphics{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast([src], global_context=global_context)

    # Remove the root tag
    root_tex = root.tex()
    assert root_tex == tex

    # Now test an tex-specific attribute
    # Generate the markup
    src = "@img[html.width=100 tex.height=20]{sample.pdf}"
    tex = "\\includegraphics[height=20]{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast([src], global_context=global_context)

    # Remove the root tag
    root_tex = root.tex()
    assert root_tex == tex
