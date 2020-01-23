"""
A receiver to identify duplicate labels.
"""
from itertools import chain

from ..signals import label_register
from ..exceptions import DuplicateLabel


@label_register.connect_via(order=100)
def duplicate_labels(registered_labels, collected_labels, *args, **kwargs):
    """Find duplicates in the collected_labels with those of labels that
    are already registered.

    This processor will find labels from different documents (with different
    doc_ids) that have the same id in the collected_labels. CitationLabels are
    excluded in this wrapped function.

    Parameters
    ----------
    registered_labels : List[:obj:`Label <.types.Label>`]
        The list of labels that have been vetted, processed and registered.
    collected_labels : Dict[str, List[:obj:`Label <types.Label>`]]
        The new labels that have been added but not yet registered. These
        will be tested for labels with duplicate ids in the registered
        labels. The keys are doc_id strings and the values are lists of
        labels.

    Raises
    ------
    DuplicateLabel
        Exception raised if a label in the collected_labels has an id that is
        already registered for another document (with a different doc_id).
    """
    # First get a mapping of the registered label ids and their
    # corresponding doc_ids
    label_ids = {label.id: label.doc_id for label in registered_labels}

    # Go through the collected labels and see if there are labels with ids
    # that have already been assigned to other doc_ids--provided the label
    # doesn't have a kind listed in the exclude_kinds parameter.
    filtered_labels = list(chain(*collected_labels.values()))
    duplicated_ids = [label for label in filtered_labels
                      if label.id in label_ids and
                      label_ids[label.id] != label.doc_id]

    # Raise an exception if duplicate ids were found.
    if len(duplicated_ids) > 0:
        msg = ("Label identifiers should be unique for all documents in a "
               "project. The following label identifers are used in "
               "multiple documents: "
               "{}".format(", ".join([l.id for l in duplicated_ids])))
        raise DuplicateLabel(msg)
