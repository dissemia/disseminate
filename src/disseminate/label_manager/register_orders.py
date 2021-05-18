"""
Function(s) for setting the label order attributes.
"""

from collections import Counter


def reorder_and_purge_labels_by_doc_id(labels, root_context):
    """Reorder labels by doc_id and remove labels that refer to a doc_id for
    a document that no longer exists.

    Parameters
    ----------
    labels : Dict[Tuple[str,str], :obj:`Label <.label_manager.types.Label>`]
        A list of labels where the key is the (doc_id, label_id) and the values
        are the label objects.
    root_context : :obj:`.document.DocumentContext`
        The context for the root document.
    """

    # Get the order of doc_ids from the root_context
    root_doc = root_context.root_document
    if root_doc is not None:
        # Use the doc_ids from the project
        doc_ids = root_doc.doc_ids if root_doc is not None else []
    else:
        # Use the doc_ids from the labels themselves
        doc_ids = [label.doc_id for label in labels.values()]

    # Remove labels that aren't listed in the doc_ids
    filtered_labels = filter(lambda l: l.doc_id in doc_ids, labels.values())

    # Sort filtered labels by doc_id
    reordered_labels = sorted([(count, label)
                               for count, label in enumerate(filtered_labels)],
                              key=lambda k: (doc_ids.index(k[1].doc_id), k[0]))

    # Repopulate the labels dict (which should be an ordered dict)
    labels.clear()
    for count, label in reordered_labels:
        labels[label.doc_id, label.id] = label


def register_orders(labels, root_context, **kwargs):
    """Set the order attributes of labels.

    - The order is a tuple of integers that indicate the order or a label
      for the given kind.

      ex: a label may have a kind = ('heading', 'chapter') and an order
      of (3, 2). This indicates that the label is the 3rd heading and the
      2nd chapter.

    - This function may use the 'label_resets' entry in the context.
      This should be a dict with keys that are the kinds that reset other
      kind counters. The values are iterables of kinds whose counters are
      reset.

      ex: {'chapter': {'section', 'subsection', 'subsubsection'}}
      In this case, labels with a kind of 'chapter' will reset the counter
      for the 'section', 'subsection' and 'subsubsection' counters.

      Note that the 'heading' kind is not reset, and its order is maintained
      for the correct ordering of labels, even if the chapter/section/
      subsection counts are reset.

    - This function uses reorder_and_purge_labels_by_doc_id, which removes
      labels with a doc_id for documents that no longer exist.

    Parameters
    ----------
    labels : Dict[Tuple[str,str], :obj:`Label <.label_manager.types.Label>`]
        A list of labels where the key is the (doc_id, label_id) and the values
        are the label objects.
    root_context : :obj:`.document.DocumentContext`
        The context for the root document.
    """
    # Reorder labels
    reorder_and_purge_labels_by_doc_id(labels, root_context)

    # Keep track of the counts for each kind
    count = Counter()

    # Retrieve the label_resets.
    if 'label_resets' in root_context:
        reset_counts = root_context['label_resets']
    else:
        reset_counts = dict()

    # Process labels with a kind listed.
    filtered_labels = [label for label in labels.values()
                       if label.kind is not None]
    for label in filtered_labels:

        # Get the count for each of the kind items
        order = []
        for k in label.kind:
            # Increment the count for the kind
            count[k] += 1

            # Reset counters, if specified
            if k in reset_counts:
                for i in reset_counts[k]:
                    count[i] = 0

            # Append the count
            order.append(count[k])

        label.order = tuple(order)
