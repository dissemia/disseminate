"""
Test the asy tag.
"""
from disseminate.tags import Tag
from disseminate.dependency_manager import DependencyManager
from disseminate.paths import SourcePath, TargetPath


# html target

def test_asy_html(tmpdir, context_cls):
    """Test the handling of html with the asy tag."""

    # Since this tag requires creating a cache directory, we will create the
    # target_root to a temporary directory
    project_root = SourcePath(project_root=tmpdir / 'src')
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')
    target_root = TargetPath(target_root=tmpdir)
    project_root.mkdir()

    # Setup the root context
    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'project_root': SourcePath,
                                    'target_root': TargetPath,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(src_filepath=src_filepath,
                          project_root=project_root,
                          target_root=target_root,
                          paths=[])

    # First, we'll test the case when asy code is used directly in the tag.
    # We will not use a document src_filepath in the context, since
    # when this is missing, it is not used in generating the cached filename

    # Setup the dependency manager in the context. This is needed to find and
    # convert images by the img tag.
    dep = DependencyManager(root_context=context)
    context['dependency_manager'] = dep

    # Generate the markup
    src = """@asy{
        size(200);                                                                                                                                             
                                                                                                                                                       
        draw(unitcircle);  }"""

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert img.html == '<img src="/html/media/test_69a34c39e1.svg">\n'

    # Second, we'll test the case when asy code is used directly in the tag.
    # We will now use a src_filepath of the markup document in the
    # context, since it will be used in generating the cached filename

    # Setup the dependency manager in the context. This is needed
    # to find and convert images by the img tag. We'll place the project root
    # in 'src'
    src_filepath = SourcePath(project_root=project_root,
                              subpath='chapter/test.dm')
    dep = context['dependency_manager']
    context = context_cls(dependency_manager=dep,
                          src_filepath=src_filepath,
                          project_root=project_root,
                          target_root=target_root,
                          paths=[])

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert img.html == ('<img src="/html/media/chapter/test_69a34c39e1.svg">'
                        '\n')


def test_asy_html_attribute(tmpdir, context_cls):
    """Test the handling of html with the asy tag including attributes"""

    # Since this tag requires creating a cache directory, we will create the
    # target_root to a temporary directory
    project_root = SourcePath(project_root=tmpdir / 'src')
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')
    target_root = TargetPath(target_root=tmpdir)
    project_root.mkdir()

    # Setup the root context
    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'project_root': SourcePath,
                                    'target_root': TargetPath,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(src_filepath=src_filepath,
                          project_root=project_root,
                          target_root=target_root,
                          paths=[])

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(root_context=context)
    context['dependency_manager'] = dep

    # Generate the markup
    src = """@asy[scale=2.0]{
        size(200);                                                                                                                                             

        draw(unitcircle);  }"""

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert img.html == ('<img src="/html/media/test_cd0ec1067e_scale2.0.svg">'
                         '\n')


# tex target

def test_asy_tex(tmpdir, context_cls):
    """Test the handling of tex with the asy tag."""

    # Since this tag requires creating a cache directory, we will create the
    # target_root to a temporary directory
    project_root = SourcePath(project_root=tmpdir / 'src')
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')
    target_root = TargetPath(target_root=tmpdir)
    project_root.mkdir()

    # Setup the root context
    context_cls.validation_types = {'dependency_manager': DependencyManager,
                                    'project_root': SourcePath,
                                    'target_root': TargetPath,
                                    'src_filepath': SourcePath,
                                    'paths': list}
    context = context_cls(src_filepath=src_filepath,
                          project_root=project_root,
                          target_root=target_root,
                          paths=[])

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(root_context=context)
    context['dependency_manager'] = dep

    # Generate the markup
    src = """@asy[scale=2.0]{
            size(200);                                                                                                                                             

            draw(unitcircle);  }"""

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    # Check the rendered tag and that the asy and svg files were properly
    # created
    img_filepath = tmpdir / 'tex' / 'media' / 'test_48a82ce699.pdf'
    assert img.tex == '\\includegraphics{{{}}}'.format(img_filepath)
