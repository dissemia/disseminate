"""
Test the img tag.
"""
from disseminate.tags import Tag
from disseminate.paths import TargetPath


def test_img_content_as_filepath(load_example):
    """Test the @img tag's content_as_filepath method."""
    doc = load_example('tests/tags/examples/img_ex1/test.dm')
    context = doc.context
    project_root = doc.project_root

    # 1. Test a relative path
    src = "@img{sample.pdf}"
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content
    assert img.content_as_filepath().match('sample.pdf')

    # 2. Test a absolute path
    src = "@img{{{}}}".format(project_root.absolute() / 'sample.pdf')
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content
    assert img.content_as_filepath().match('sample.pdf')

    # 3. Test a missing file. Raises a TagError
    src = "@img{missing.pdf}"
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content
    assert img.content_as_filepath() is None


def test_img_attribute(load_example):
    """Test the correct processing of attributes in an image tag."""
    doc = load_example('tests/tags/examples/img_ex1/test.dm')
    context = doc.context

    # 1. A simple example with the width of an image as an attribute
    src = "@img[width=100]{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    assert img.name == 'img'
    assert img.attributes == {'width': '100'}


# tex targets

def test_img_tex(load_example, is_pdf):
    """Test the handling of LaTeX with the img tag."""
    doc = load_example('tests/tags/examples/img_ex1/test.dm')
    context = doc.context
    env = context['environment']
    target_root = env.target_root
    media_path = env.media_path

    # 1. Test tests/tags/img_example1
    src = "@img{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    # Get the image infile_filepath and wrap it in curly braces to avoid
    # problems with unusual filenames, like those with periods
    img_filepath = target_root / 'tex' / media_path / 'sample.pdf'
    suffix = img_filepath.suffix
    base = img_filepath.with_suffix('')
    filepath = "{{{base}}}{suffix}".format(base=base, suffix=suffix)

    assert img.tex == "\\includegraphics{{{}}}".format(filepath)

    # Build the file
    assert env.build() == 'done'
    assert img_filepath.exists()

    # 2. Test attributes
    src = "@img[width=100%]{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    assert img.tex == ("\\includegraphics[width=1.0\\textwidth]"
                       "{{{}}}".format(filepath))

    # 3. Now test an tex-specific attribute
    # Generate the markup
    src = "@img[width.html=100 height.tex=20]{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    assert img.tex == "\\includegraphics[height=20]{{{}}}".format(filepath)

    # Check the build
    assert is_pdf(img_filepath)


# html target

def test_img_html(load_example):
    """Test the handling of html with the img tag."""
    doc = load_example('tests/tags/examples/img_ex1/test.dm')
    context = doc.context

    # 1. Test tests/tags/img_example1
    src = "@img{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    assert img.html == '<img src="media/sample.svg">\n'  # rel path by default

    # Now test an html-specific attribute
    src = "@img[width.html=100% height.tex=20%]{sample.pdf}"

    # Generate a tag and compare the generated text to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content
    assert img.html == '<img src="media/sample.svg" style="width: 100.0%">\n'

    # Check the build
    env = doc.context['environment']
    img_filepath = TargetPath(target_root=doc.target_root, target='html',
                              subpath="media/sample.svg")
    assert not img_filepath.exists()

    assert env.build() == 'done'
    assert img_filepath.exists()
    assert '<svg' in img_filepath.read_text()


# xhtml target

def test_img_xhtml(load_example, is_xml, is_svg):
    """Test the handling of html with the img tag."""
    doc = load_example('tests/tags/examples/img_ex1/test.dm')
    context = doc.context

    # 1. Test tests/tags/img_example1
    src = "@img{sample.pdf}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    assert img.xhtml == '<img src="media/sample.svg"/>\n'  # rel path by default
    assert is_xml(img.xhtml)

    # Now test an xhtml-specific attribute
    src = "@img[width.xhtml=100% height.html=20%]{sample.pdf}"

    # Generate a tag and compare the generated text to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content
    assert img.xhtml == '<img src="media/sample.svg" style="width: 100.0%"/>\n'
    assert is_xml(img.xhtml)

    # Check the build
    env = doc.context['environment']
    img_filepath = TargetPath(target_root=doc.target_root, target='xhtml',
                              subpath="media/sample.svg")
    assert not img_filepath.exists()

    assert env.build() == 'done'
    assert img_filepath.exists()
    assert is_svg(img_filepath)
