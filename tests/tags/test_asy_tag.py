"""
Test the asy tag.
"""
from disseminate.ast import process_ast
from disseminate.dependency_manager import DependencyManager
from disseminate import settings


def test_asy_html(tmpdir):
    """Test the handling of html with the asy tag."""
    # Since this tag requires creating a cache directory, we will copy the
    # project_root to a temporary directory
    project_root = str(tmpdir.join('src'))
    target_root = str(tmpdir)

    # First, we'll test the case when asy code is used directly in the tag.
    # We will not use a document_src_filepath in the global_context, since
    # when this is missing, it is used in generating the cached filename

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(project_root=project_root,
                            target_root=target_root)
    context = {'dependency_manager': dep,
               'project_root': project_root,
               'target_root': target_root}

    # Generate the markup
    src = """@asy{
        size(200);                                                                                                                                             
                                                                                                                                                       
        draw(unitcircle);  }"""

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=context)

    # get the root tag
    root_html = root.html()

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">\n  '
    root_end = '\n</span>\n'

    # Remove the root tag
    root_html = root.html()[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert root_html == '<img src="/media/69a34c39e1.svg"/>'
    assert tmpdir.ensure(settings.media_dir, '69a34c39e1.svg')
    assert tmpdir.ensure('.html', settings.media_dir, '69a34c39e1.svg')

    # Second, we'll test the case when asy code is used directly in the tag.
    # We will now use a src_filepath of the markup document in the
    # local_context, since it is not used in generating the cached filename

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag. We'll place the project root
    # in 'src'
    dep = DependencyManager(project_root=project_root,
                            target_root=target_root)
    context = {'dependency_manager': dep,
               'project_root': 'src',
               'target_root': target_root}

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=context)

    # get the root tag
    root_html = root.html()

    # Remove the root tag
    root_html = root.html()[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert root_html == '<img src="/media/chapter/test_69a34c39e1.svg"/>'
    assert tmpdir.ensure(settings.media_dir, 'chapter', 'test_69a34c39e1.svg')
    assert tmpdir.ensure('.html', settings.media_dir, 'cahpter',
                         'test_69a34c39e1.svg')


def test_asy_html_attribute(tmpdir):
    """Test the handling of html with the asy tag including attributes"""

    # Since this tag requires creating a cache directory, we will copy the
    # project_root to a temporary directory
    project_root = str(tmpdir.join('src'))
    target_root = str(tmpdir)

    # First, we'll test the case when asy code is used directly in the tag.
    # We will not use a document_src_filepath in the global_context, since
    # when this is missing, it is used in generating the cached filename

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(project_root=project_root,
                            target_root=target_root,
                            segregate_targets=True)
    global_context = {'_dependencies': dep,
                      '_project_root': project_root,
                      '_target_root': target_root}
    local_context = {'_targets': {'.html': 'test.html'}}

    # Generate the markup
    src = """@asy[scale=2.0]{
        size(200);                                                                                                                                             

        draw(unitcircle);  }"""

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, local_context=local_context,
                       global_context=global_context)

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">\n  '
    root_end = '\n</span>\n'

    # Remove the root tag
    root_html = root.html()[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert root_html == '<img src="/media/cd0ec1067e_scale2.0.svg"/>'
    assert tmpdir.ensure(settings.media_dir, 'cd0ec1067e_scale2.0.svg')
    assert tmpdir.ensure('.html', settings.media_dir, 'cd0ec1067e_scale2.0.svg')
