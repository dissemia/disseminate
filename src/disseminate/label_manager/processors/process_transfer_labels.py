"""
A label processor to transfer labels from collected_labels to regsistered
labels.
"""
from .process_labels import ProcessLabels


class TransferLabels(ProcessLabels):
    """A label processor to transfer labels from the collected_labels to
    the registered labels.

    Transfer collected (and unregistered) labels from the collected_labels
    dict to the list of registered labels.
    """

    order = 200

    @property
    def doc_ids(self):
        # The context should be a valid DocumentContext
        assert (self.context.is_valid('root_document') and
                hasattr(self.context, 'root_document'))

        # Get the doc_ids from the root document
        root_document = self.context.root_document
        return root_document.doc_ids

    def __call__(self, registered_labels, collected_labels, *args, **kwargs):
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
        doc_ids : list of str
            An ordered list of the document identifiers.
        """
        # Reconstruct the labels list from existing, registered labels and
        # collected labels. These should have the same order as the documents.

        # Create a dict of doc_ids and the order of the documents
        doc_id_orders = {count: doc_id
                         for count, doc_id in enumerate(self.doc_ids)}

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
