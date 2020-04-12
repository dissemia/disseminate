"""
Test the img tag.
"""
import pathlib

import pytest

from disseminate.tags import Tag, TagError
from disseminate.dependency_manager import DependencyManager
from disseminate.paths import SourcePath, TargetPath


@pytest.fixture
def img_context1(tmpdir, context_cls):
    """A context for the image tag using tests/tags/img_example1."""
    project_root = SourcePath(project_root='tests/tags/img_example1')
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')

    # Setup the root context
    paths = [pathlib.Path('.').absolute(),
             pathlib.Path('.').absolute() / project_root]
    context = context_cls(project_root=project_root, target_root=target_root,
                          paths=paths, src_filepath=src_filepath)

    # Setup the dependency manager in the global context. This is needed
    # to find and convert images by the img tag.
    dep = DependencyManager(root_context=context)
    context['dependency_manager'] = dep

    return context


def test_img_filepath(img_context1):
    """Test the identification of image filepaths."""
    project_root = img_context1['project_root']

    # 1. Test a relative path
    src = "@img{sample.pdf}"
    root = Tag(name='root', content=src, attributes='', context=img_context1)
    img = root.content
    assert img.infile_filepath().match('sample.pdf')

    # 2. Test a absolute path
    src = "@img{{{}}}".format(project_root.absolute() / 'sample.pdf')
    root = Tag(name='root', content=src, attributes='', context=img_context1)
    img = root.content
    assert img.infile_filepath().match('sample.pdf')

    # 3. Test a missing file. Raises a TagError
    src = "@img{missing.pdf}"
    root = Tag(name='root', content=src, attributes='', context=img_context1)
    img = root.content
    with pytest.raises(TagError):
        img.infile_filepath()


def test_img_mtime(doc):
    """Test the correct modification time for images referenced by
    an @img tag."""
    # Copy an image to the temporary directory
    img_src = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
</svg"""
    src_path = doc.src_filepath.parent
    img_filepath = src_path / 'test.svg'
    img_filepath.write_text(img_src)

    # Create an image tag
    src = "@img{{{}}}".format(str(img_filepath))

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    img = root.content

    # Check the mtimes
    assert img.mtime == img_filepath.stat().st_mtime
    assert root.mtime == img.mtime  # root should be at least as late as @img
    assert root.mtime > doc.mtime  # and the root tag is later than the src file


def test_img_attribute(img_context1):
    """Test the correct processing of attributes in an image tag."""
    # 1. A simple example with the width of an image as an attribute
    src = "@img[width=100]{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=img_context1)
    img = root.content

    assert img.name == 'img'
    assert img.attributes == {'width': '100'}


# html target

def test_img_html(img_context1):
    """Test the handling of html with the img tag."""

    # 1. Test tests/tags/img_example1
    src = "@img{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=img_context1)
    img = root.content

    assert img.html == '<img src="/html/sample.svg">\n'

    # Now test an html-specific attribute
    # Generate the markup
    src = "@img[width.html=100% height.tex=20%]{sample.pdf}"

    # Generate a tag and compare the generated text to the answer key
    root = Tag(name='root', content=src, attributes='', context=img_context1)
    img = root.content
    assert img.html == '<img src="/html/sample.svg" style="width: 100.0%">\n'

    # Check the converted file
    dep = img_context1['dependency_manager']
    src_filepath = img_context1['src_filepath']
    sample_svg_dep = [dep for dep in dep.dependencies[src_filepath]
                      if dep.dest_filepath.match('html/sample.svg')]
    assert len(sample_svg_dep) == 1
    assert sample_svg_dep[0].dep_filepath.exists()


# tex targets

def test_img_tex(img_context1):
    """Test the handling of LaTeX with the img tag."""
    target_root = img_context1['target_root']

    # 1. Test tests/tags/img_example1
    src = "@img{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=img_context1)
    img = root.content

    # Get the image infile_filepath and wrap it in curly braces to avoid problems
    # with unusual filenames, like those with periods
    img_filepath = target_root / 'tex' / 'sample.pdf'
    suffix = img_filepath.suffix
    base = img_filepath.with_suffix('')
    filepath = "{{{base}}}{suffix}".format(base=base, suffix=suffix)

    assert img.tex == "\\includegraphics{{{}}}".format(filepath)

    # Check the copied file
    assert img_filepath.exists()

    # 2. Test attributes
    src = "@img[width=100%]{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=img_context1)
    img = root.content

    assert img.tex == ("\\includegraphics[width=1.0\\textwidth]"
                       "{{{}}}".format(filepath))

    # 3. Now test an tex-specific attribute
    # Generate the markup
    src = "@img[width.html=100 height.tex=20]{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=img_context1)
    img = root.content

    assert img.tex == "\\includegraphics[height=20]{{{}}}".format(filepath)
