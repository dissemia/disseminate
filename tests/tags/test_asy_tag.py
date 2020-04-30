"""
Test the asy tag.
"""
import pytest

from disseminate.tags import Tag


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
    assert html == '<img src="media/test_c838921f79c0.svg">\n'

    # Check the build
    context['targets'] |= {'html'}
    html_builder = doc.context['builders']['.html']
    assert html_builder.build(complete=True) == 'missing (outfilepath)'
    assert not img.infilepath().exists()


# html targets

def test_asy_html(doc):
    """Test the handling of html with the asy tag."""
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
    assert img.html == '<img src="media/test_a270b9e4ed3f.svg">\n'

    # Check the build
    html_builder = doc.context['builders']['.html']
    assert html_builder.build(complete=True) == 'done'
    assert img.infilepath().exists()

    assert '<svg' in img.infilepath().read_text()
    assert 'width="200pt" height="200pt"' in img.infilepath().read_text()


def test_asy_html_attribute(doc):
    """Test the handling of html with the asy tag including attributes"""
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
    assert img.html != '<img src="media/test_a270b9e4ed3f.svg">\n'

    # A new filename with an attribute should be different
    assert img.html == '<img src="media/test_8cf890d444f0.svg">\n'

    # Check the build
    html_builder = doc.context['builders']['.html']
    assert html_builder.build(complete=True) == 'done'
    assert img.infilepath().exists()

    # The svg file should have different dimensions
    assert '<svg' in img.infilepath().read_text()
    assert 'width="200pt" height="200pt"' not in img.infilepath().read_text()
    assert 'width="500px" height="500px"' in img.infilepath().read_text()


# tex target

def test_asy_tex(doc):
    """Test the handling of tex with the asy tag."""
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
    img_filepath = target_root / 'tex' / 'media' / 'test_80940aa73734.pdf'
    suffix = img_filepath.suffix
    base = img_filepath.with_suffix('')
    filepath = "{{{base}}}{suffix}".format(base=base, suffix=suffix)

    assert img.tex == '\\includegraphics{{{}}}'.format(filepath)
