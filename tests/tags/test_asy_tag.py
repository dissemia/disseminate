"""
Test the asy tag.
"""
import pytest

from disseminate.tags import Tag
from disseminate.convert import ConverterError


def test_asy_invalid_html(doc):
    """Test the @asy tag with invalid contents ."""
    context = doc.context

    # Generate the markup
    src = "@asy{asy}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    img = root.content

    # An error is raised when trying to generate a target
    for target in ('html', 'tex'):
        with pytest.raises(ConverterError):
            getattr(img, target)


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
    assert img.html == '<img src="media/test_69a34c39e1.svg">\n'


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
    assert img.html == ('<img src="media/test_cd0ec1067e_scale2.0.svg">'
                        '\n')

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
    # created
    target_root = doc.target_root
    img_filepath = target_root / 'tex' / 'media' / 'test_48a82ce699.pdf'
    assert img.tex == '\\includegraphics{{{}}}'.format(img_filepath)
