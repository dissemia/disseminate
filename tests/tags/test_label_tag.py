"""
Test the Label tag.
"""
import pytest

from disseminate.tags.label import (generate_label_id, create_label,
                                    LabelAnchor, LabelTag)
from disseminate.label_manager import ContentLabel


def test_generate_label_id(mocktag_cls, context_cls):
    """Test the generate_label_id function."""

    context = context_cls(doc_id='tester')

    # 1. Test basic string content
    tag1 = mocktag_cls(name='label', content='My title', attributes='',
                       context=context)
    assert generate_label_id(tag1) == "tester-my-title"

    # 2. Test an extent string content
    tag2 = mocktag_cls(name='label',
                       content='This is my title. It has 2 lines,',
                       attributes='', context=context)
    assert generate_label_id(tag2) == "tester-this-is-my-title"

    # 3. Test a non-string content
    tag3 = mocktag_cls(name='label',
                       content=['This is my title.', ' It has 2 lines'],
                       attributes='', context=context)
    assert generate_label_id(tag3) == "tester-this-is-my-title"

    # 4. Test with short title
    tag4 = mocktag_cls(name='label', content='This is my title. It has 2 lines,',
                       attributes='short="small title"', context=context)
    assert generate_label_id(tag4) == "tester-small-title"

    # 5. Test with a specific id
    tag5 = mocktag_cls(name='label', content='This is my title. It has 2 lines,',
                       attributes='id=xrd13', context=context)
    assert generate_label_id(tag5) == "xrd13"

    # 6. Test with an empty content
    # 6.1. (Without a context with a 'doc_id' entry, an error is raised.

    tag6 = mocktag_cls(name='label', content='', attributes='',
                       context=dict())
    with pytest.raises(AttributeError):
        generate_label_id(tag6)

    # 6.2. Try with a correctly configured context
    tag6 = mocktag_cls(name='label', content='', attributes='',
                       context=context)
    assert generate_label_id(tag6) == "tester-1"


def test_create_label(doc, mocktag_cls):
    """Test the create_label function."""

    # Get the context and label_manager from the doc
    context = doc.context
    label_manager = context['label_manager']

    # 1. Test a basic heading label
    tag1 = mocktag_cls(name='label', content='My title', attributes='',
                       context=context)
    label1_id = create_label(tag=tag1, kind=())
    label1 = label_manager.get_label(label1_id)
    assert label1_id == 'test-dm-my-title'
    assert isinstance(label1, ContentLabel)
    assert label1.title == 'My title'

    # 2. Test an extended string in the content
    tag2 = mocktag_cls(name='label',
                       content='This is my title. It has 2 lines,',
                       attributes='',
                       context=context)
    label2_id = create_label(tag=tag2, kind=())
    label2 = label_manager.get_label(label2_id)
    assert label2_id == 'test-dm-this-is-my-title'
    assert isinstance(label2, ContentLabel)
    assert label2.title == 'This is my title'

    # 3. Test with a specified id
    tag3 = mocktag_cls(name='label',
                       content='This is my title. It has 2 lines,',
                       attributes='id=xrd43a',
                       context=context)
    label3_id = create_label(tag=tag3, kind=())
    label3 = label_manager.get_label(label3_id)
    assert label3_id == 'xrd43a'
    assert isinstance(label3, ContentLabel)
    assert label3.title == 'This is my title'


# Test tex targets

def test_labelanchor_tex(doc, mocktag_cls):
    """Test the LabelAnchor tag with tex targets."""

    # Get the context from the doc. The doc context has a label_manager
    # built-in.
    context = doc.context

    # 1. Test a basic label
    tag1 = mocktag_cls(name='label', content='My title', attributes='',
                       context=context)
    label1_id = create_label(tag=tag1, kind=())
    assert isinstance(label1_id, str)

    labelanchor1 = LabelAnchor(name='label', content=label1_id, attributes='',
                               context=context)
    assert labelanchor1.tex == '\\label{test-dm-my-title}'


def test_labeltag_tex(doc, mocktag_cls):
    """Test the LabelTag with tex targets."""

    # Get the context from the doc. The doc context has a label_manager
    # built-in.
    context = doc.context

    # 1. Test a label tag with a basic kind. kind = ('heading', 'chapter')
    context['label_fmts']['heading'] = '@label.title'
    kind = ('heading',)
    tag1 = mocktag_cls(name='label', content='My title', attributes='',
                       context=context)
    label1_id = create_label(tag=tag1, kind=kind)

    labeltag1 = LabelTag(name='label', content=label1_id, attributes='',
                         context=context)
    assert labeltag1.tex == 'My title'

    # 2. Test a label tag with a different label format, including the chapter
    #    number. kind = ('heading', 'chapter_number')
    context['label_fmts']['heading_chapter'] = 'Chapter @label.chapter_number '
    kind = ('heading', 'chapter')
    tag2 = mocktag_cls(name='label', content='My title', attributes='',
                       context=context)
    label2_id = create_label(tag=tag2, kind=kind)

    labeltag2 = LabelTag(name='label', content=label2_id, attributes='',
                         context=context)
    assert labeltag2.tex == 'Chapter 1 '  # chapter number not assigned


# Test html targets

def test_labelanchor_html(doc, mocktag_cls):
    """Test the LabelAnchor tag with html targets."""

    # Get the context from the doc. The doc context has a label_manager
    # built-in.
    context = doc.context

    # 1. Test a basic label
    tag1 = mocktag_cls(name='label', content='My title', attributes='',
                       context=context)
    label1_id = create_label(tag=tag1, kind=())
    assert isinstance(label1_id, str)

    labelanchor1 = LabelAnchor(name='label', content=label1_id, attributes='',
                               context=context)
    assert labelanchor1.html == '<span id="test-dm-my-title"></span>\n'


def test_labeltag_html(doc, mocktag_cls):
    """Test the LabelTag with html targets."""

    # Get the context from the doc. The doc context has a label_manager
    # built-in.
    context = doc.context

    # 1. Test a label tag with a basic kind. kind = ('heading', 'chapter')
    context['label_fmts']['heading'] = '@label.title'
    kind = ('heading',)
    tag1 = mocktag_cls(name='label', content='My title', attributes='',
                       context=context)
    label1_id = create_label(tag=tag1, kind=kind)

    labeltag1 = LabelTag(name='label', content=label1_id, attributes='',
                         context=context)
    assert labeltag1.html == '<span class="label">My title</span>\n'

    # 2. Test a label tag with a different label format, including the chapter
    #    number. kind = ('heading', 'chapter_number')
    context['label_fmts']['heading_chapter'] = 'Chapter @label.chapter_number '
    kind = ('heading', 'chapter')
    tag2 = mocktag_cls(name='label', content='My title', attributes='',
                       context=context)
    label2_id = create_label(tag=tag2, kind=kind)

    labeltag2 = LabelTag(name='label', content=label2_id, attributes='',
                         context=context)
    # chapter number not assigned
    assert labeltag2.html == '<span class="label">Chapter 1 </span>\n'
