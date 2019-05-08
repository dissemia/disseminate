"""
Test the ProcessContentLabels class
"""
import pytest

from disseminate.label_manager.processors import (ProcessContentLabels)
from disseminate.label_manager.types import ContentLabel


def test_process_content_labels_processor_part(context_cls):
    """Test the ProcessContentLabels processor with 'part' headings."""

    context = context_cls()

    # Create some heading labels
    label1 = ContentLabel(doc_id='a', id='a', kind=('heading', 'part'),
                          mtime=None, title='a')
    label2 = ContentLabel(doc_id='a', id='a.a', kind=('heading', 'chapter'),
                          mtime=None, title='a.a')
    label3 = ContentLabel(doc_id='a', id='a.a.a', kind=('heading', 'section'),
                          mtime=None, title='a.a.a')
    label4 = ContentLabel(doc_id='a', id='a.a.a.a',
                          mtime=None, kind=('heading', 'subsection'),
                          title='a.a.a.a')

    # Give the labels mock orders (usually set by the OrderLabels processor)
    label1.order = (1, 1)
    label2.order = (2, 1)
    label3.order = (3, 1)
    label4.order = (4, 1)

    # Setup the processors
    processor = ProcessContentLabels(context=context)

    # Process the labels
    registered_labels = [label1, label2, label3, label4]
    processor(registered_labels=registered_labels)

    # Check the values of the labels
    assert label1.part_label == label1
    assert label1.chapter_label is None
    assert label1.section_label is None
    assert label1.subsection_label is None
    assert label1.subsubsection_label is None
    assert label1.part_number == 1
    assert label1.part_title == 'a'
    assert label1.chapter_number == ''
    assert label1.chapter_title == ''
    assert label1.section_number == ''
    assert label1.section_title == ''
    assert label1.subsection_number == ''
    assert label1.subsection_title == ''
    assert label1.tree_number == '1'

    assert label2.part_label == label1
    assert label2.chapter_label == label2
    assert label2.section_label is None
    assert label2.subsection_label is None
    assert label2.subsubsection_label is None
    assert label2.part_number == 1
    assert label2.part_title == 'a'
    assert label2.chapter_number == 1
    assert label2.chapter_title == 'a.a'
    assert label2.section_number == ''
    assert label2.section_title == ''
    assert label2.subsection_number == ''
    assert label2.subsection_title == ''
    assert label2.tree_number == '1.1'

    assert label3.part_label == label1
    assert label3.chapter_label == label2
    assert label3.section_label == label3
    assert label3.subsection_label is None
    assert label3.subsubsection_label is None
    assert label3.part_number == 1
    assert label3.part_title == 'a'
    assert label3.chapter_number == 1
    assert label3.chapter_title == 'a.a'
    assert label3.section_number == 1
    assert label3.section_title == 'a.a.a'
    assert label3.subsection_number == ''
    assert label3.subsection_title == ''
    assert label3.tree_number == '1.1.1'

    assert label4.part_label == label1
    assert label4.chapter_label == label2
    assert label4.section_label == label3
    assert label4.subsection_label == label4
    assert label4.subsubsection_label is None
    assert label4.part_number == 1
    assert label4.part_title == 'a'
    assert label4.chapter_number == 1
    assert label4.chapter_title == 'a.a'
    assert label4.section_number == 1
    assert label4.section_title == 'a.a.a'
    assert label4.subsection_number == 1
    assert label4.subsection_title == 'a.a.a.a'
    assert label4.tree_number == '1.1.1.1'


def test_process_content_labels_processor_chapter(context_cls):
    """Test the ProcessContentLabels processor with 'chapter' headings."""

    context = context_cls()

    # Create some heading labels
    label1 = ContentLabel(doc_id='a', id='a', kind=('heading', 'chapter'),
                          mtime=None, title='a')
    label2 = ContentLabel(doc_id='a', id='a.a', kind=('heading', 'section'),
                          mtime=None, title='a.a')
    label3 = ContentLabel(doc_id='a', id='a.a.a',
                          kind=('heading', 'subsection'),
                          mtime=None, title='a.a.a')
    label4 = ContentLabel(doc_id='a', id='a.a.a.a',
                          mtime=None, kind=('heading', 'subsubsection'),
                          title='a.a.a.a')

    # Give the labels mock orders (usually set by the OrderLabels processor)
    label1.order = (1, 1)
    label2.order = (2, 1)
    label3.order = (3, 1)
    label4.order = (4, 1)

    # Setup the processors
    processor = ProcessContentLabels(context=context)

    # Process the labels
    registered_labels = [label1, label2, label3, label4]
    processor(registered_labels=registered_labels)

    # Check the values of the labels
    assert label1.part_label is None
    assert label1.chapter_label == label1
    assert label1.section_label is None
    assert label1.subsection_label is None
    assert label1.subsubsection_label is None
    assert label1.part_number == ''
    assert label1.part_title == ''
    assert label1.chapter_number == 1
    assert label1.chapter_title == 'a'
    assert label1.section_number == ''
    assert label1.section_title == ''
    assert label1.subsection_number == ''
    assert label1.subsection_title == ''
    assert label1.tree_number == '1'

    assert label2.part_label is None
    assert label2.chapter_label == label1
    assert label2.section_label == label2
    assert label2.subsection_label is None
    assert label2.subsubsection_label is None
    assert label2.part_number == ''
    assert label2.part_title == ''
    assert label2.chapter_number == 1
    assert label2.chapter_title == 'a'
    assert label2.section_number == 1
    assert label2.section_title == 'a.a'
    assert label2.subsection_number == ''
    assert label2.subsection_title == ''
    assert label2.tree_number == '1.1'

    assert label3.part_label is None
    assert label3.chapter_label == label1
    assert label3.section_label == label2
    assert label3.subsection_label == label3
    assert label3.subsubsection_label is None
    assert label3.part_number == ''
    assert label3.part_title == ''
    assert label3.chapter_number == 1
    assert label3.chapter_title == 'a'
    assert label3.section_number == 1
    assert label3.section_title == 'a.a'
    assert label3.subsection_number == 1
    assert label3.subsection_title == 'a.a.a'
    assert label3.tree_number == '1.1.1'

    assert label4.part_label is None
    assert label4.chapter_label == label1
    assert label4.section_label == label2
    assert label4.subsection_label == label3
    assert label4.subsubsection_label == label4
    assert label4.part_number == ''
    assert label4.part_title == ''
    assert label4.chapter_number == 1
    assert label4.chapter_title == 'a'
    assert label4.section_number == 1
    assert label4.section_title == 'a.a'
    assert label4.subsection_number == 1
    assert label4.subsection_title == 'a.a.a'
    assert label4.tree_number == '1.1.1.1'
