"""
Test the asy tag

These tests also serve to test the rendering of an image from inline code or
from a specified file.
"""
from disseminate.tags import Tag
from disseminate.builders.exceptions import BuildError


def test_asy_invalid_html(doc):
    """Test the @asy tag with invalid contents ."""
    context = doc.context

    # Generate the markup
    src = "@asy{asy}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    # Load the html
    html = img.html
    assert html == '<img src="media/test_42424e473037.svg">\n'

    # Check the build
    context['targets'] |= {'html'}
    html_builder = doc.context['builders']['.html']

    # Check the build. Asymptote may fail with an exit code of 0 and not
    # generate a file, or it may exit with a code not equal to 0.
    try:
        status = html_builder.build(complete=True)
    except BuildError:
        status = 'build error'

    assert status in {'missing (outfilepath)', 'build error'}
    

# html targets

def test_asy_inline_html(doc):
    """Test the handling of html with the asy tag with inline asy code."""
    context = doc.context

    # Generate the markup
    src = """@asy{
        size(200);                                                                                                                                             
                                                                                                                                                       
        draw(unitcircle);  }"""

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert img.html == '<img src="media/test_afa49f1699c4.svg">\n'

    # Check the build
    html_builder = doc.context['builders']['.html']
    assert html_builder.build(complete=True) == 'done'  # build successful
    outfilepath = img._outfilepaths['.html']
    assert outfilepath.exists()  # file was created

    assert '<svg' in outfilepath.read_text()
    assert 'width="200pt" height="200pt"' in outfilepath.read_text()


def test_asy_file_html(doc):
    """Test the handling of html with the asy tag with an asy file."""
    context = doc.context
    target_root = context['target_root']

    # Generate the markup
    src = """@asy{tests/tags/examples/asy_ex1/test.asy}"""

    # Generate a tag and compare the generated tex to the answer key
    body = Tag(name='body', content=src, attributes='', context=context)
    img = body.content

    # Check the rendered tag and that the asy and svg files were properly
    # created
    assert (img.html ==
            '<img src="media/tests/tags/examples/asy_ex1/test.svg">\n')

    # Check the build
    html_builder = doc.context['builders']['.html']
    assert html_builder.build(complete=True) == 'done'  # build successful

    outfilepath = img._outfilepaths['.html']
    assert (outfilepath ==
            target_root / 'html' / 'media' / 'tests' / 'tags' / 'examples' /
            'asy_ex1' / 'test.svg')
    assert outfilepath.exists()  # file was created

    # Make sure incorrect paths haven't been created
    assert not (target_root / 'media').is_dir()

    assert '<svg' in outfilepath.read_text()
    assert 'width="200pt" height="200pt"' in outfilepath.read_text()


def test_asy_attribute_inline_html(doc):
    """Test the handling of html with the asy tag including attributes with
    inline asy code"""
    context = doc.context

    # Generate the markup
    src = """@asy[scale=2.0]{
        size(200);                                                                                                                                             

        draw(unitcircle);  }"""

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    # Check the rendered tag and that the asy and svg files were properly
    # created
    # The filename should not match the value without the attribute
    assert img.html != '<img src="media/test_afa49f1699c4.svg">\n'

    # A new filename with an attribute should be different
    assert img.html == '<img src="media/test_58d2cba4c837.svg">\n'

    # Check the build
    html_builder = doc.context['builders']['.html']
    assert html_builder.build(complete=True) == 'done'  # build successful
    outfilepath = img._outfilepaths['.html']
    assert outfilepath.exists()  # file was created

    # The svg file should have different dimensions
    assert '<svg' in outfilepath.read_text()
    assert 'width="200pt" height="200pt"' not in outfilepath.read_text()
    assert 'width="500px" height="500px"' in outfilepath.read_text()


# tex target

def test_asy_inline_tex(doc):
    """Test the handling of tex with the asy tag with inline asy code."""
    context = doc.context

    # Generate the markup
    src = """@asy[scale=2.0]{
            size(200);                                                                                                                                             

            draw(unitcircle);  }"""

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    # Check the rendered tag and that the asy and svg files were properly
    # created. The filename is wrapped in curly braces to account for filenames
    # with periods and other special characters
    target_root = doc.target_root
    img_filepath = target_root / 'tex' / 'media' / 'test_1c56ea679f0d.pdf'
    suffix = img_filepath.suffix
    base = img_filepath.with_suffix('')
    filepath = "{{{base}}}{suffix}".format(base=base, suffix=suffix)

    assert img.tex == '\\includegraphics{{{}}}'.format(filepath)


def test_asy_inline_target_order(doc):
    """Test the behavior of the asy tag with different orders of target
    renderings. This can find bugs in path caching. Test with inline asy code"""
    context = doc.context
    target_root = doc.target_root

    # Generate the markup
    src = """@asy[scale=2.0]{
            size(200);                                                    
                                                                                                     

            draw(unitcircle);  }"""

    # 1. Test tex then html.
    #    Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    tex_filepath = target_root / 'tex' / 'media' / 'test_63a3c6007dd1.pdf'
    suffix = tex_filepath.suffix
    base = tex_filepath.with_suffix('')
    filepath = "{{{base}}}{suffix}".format(base=base, suffix=suffix)

    assert img.tex == '\\includegraphics{{{}}}'.format(filepath)
    assert img.html == '<img src="media/test_63a3c6007dd1.svg">\n'

    # 2. Test html then tex
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    assert img.html == '<img src="media/test_63a3c6007dd1.svg">\n'
    assert img.tex == '\\includegraphics{{{}}}'.format(filepath)
