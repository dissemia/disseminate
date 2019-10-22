"""
A receiver to transfer labels from the collected labels to registered labels.
"""
from ..signals import label_register


@label_register.connect_via(order=200)
def transfer_labels(registered_labels, collected_labels, root_context,
                    *args, **kwargs):
    """Transfer collected labels to the labels registry list and reorder
    labels according to their corresponding document's order.

    Parameters
    ----------
    registered_labels : List[:obj:`disseminate.label_manager.Label`]
        The list of labels that have been vetted, processed and registered.
    collected_labels : Dict[str, List[:obj:`disseminate.labels.Label`]]
        The new labels that have been added but not yet registered. These
        will be tested for labels with duplicate ids in the registered
        labels. The keys are doc_id strings and the values are lists of
        labels.
    """
    assert root_context.is_valid('root_document')
    # Reconstruct the labels list from existing, registered labels and
    # collected labels. These should have the same order as the documents.

    # get a listing of doc_ids from the root_document
    # Get the doc_ids from the root document
    root_document = root_context.root_document
    doc_ids = root_document.doc_ids

    # Create a dict of doc_ids and the order of the documents
    doc_id_orders = {count: doc_id for count, doc_id in enumerate(doc_ids)}

    # Organize the registered labels by doc_id
    registered_labels_dict = dict()
    for label in registered_labels:
        labels_list = registered_labels_dict.setdefault(label.doc_id, [])
        labels_list.append(label)

    # Create an updated, ordered list of registered labels
    new_labels = []

    for count, doc_id in sorted(doc_id_orders.items()):
        if doc_id in collected_labels:
            new_labels += collected_labels.pop(doc_id)
        elif doc_id in registered_labels_dict:
            new_labels += registered_labels_dict[doc_id]

    # Transfer the labels
    registered_labels.clear()
    registered_labels += new_labels
