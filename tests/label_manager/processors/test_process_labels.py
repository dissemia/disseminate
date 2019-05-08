"""
Test the ProcessLabels class
"""
from disseminate.label_manager.processors import ProcessLabels
from disseminate.label_manager.types import ContentLabel, Label


def test_process_label_processors(context_cls):
    """Test the processors method of the ProcessLabels class"""

    context = context_cls()

    # Create a mock sub-class of the ProcessLabels
    # 1. First, try filtering based on includes
    class SubProcessLabels(ProcessLabels):
        pass

    processors = ProcessLabels.processors(context=context)

    # At least 1 processor should be listed, and 1 of them should be the
    # SubProcessLabels
    assert len(processors) > 0

    subprocess = [p for p in processors if
                  isinstance(p, SubProcessLabels)]
    assert len(subprocess) == 1
    assert id(subprocess[0].context) == id(context)


def test_process_labels_filter(context_cls):
    """Test the filter method of the ProcessLabels class."""

    context = context_cls()

    # Create a mock sub-class of the ProcessLabels
    # 1. First, try filtering based on includes
    class SubProcessLabels(ProcessLabels):

        includes = {ContentLabel}

    labels = [Label(doc_id='test1', id='test1', kind=(), mtime=-1),
              ContentLabel(doc_id='test2', id='test2', kind=(), mtime=-1,
                           title='test2'),
              ContentLabel(doc_id='test3', id='test3', kind=(), mtime=-1,
                           title='test3')]

    sub = SubProcessLabels(context=context)
    filtered = sub.filter(labels)

    assert len(filtered) == 2
    assert filtered[0] == labels[1]
    assert filtered[1] == labels[2]

    # 2. Next, try filtering based on includes and excludes
    SubProcessLabels.excludes = {ContentLabel}
    filtered = sub.filter(labels)

    assert len(filtered) == 0

    # 3. Next, try filtering based on excludes
    SubProcessLabels.includes = None

    filtered = sub.filter(labels)

    assert len(filtered) == 1
    assert filtered[0] == labels[0]
