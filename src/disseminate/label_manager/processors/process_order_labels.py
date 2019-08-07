"""
A label processor to order labels.
"""
from collections import Counter

from .process_labels import ProcessLabels


class OrderLabels(ProcessLabels):
    """A label processor to set the order attributes of labels.
    """

    order = 300

    def __call__(self, registered_labels, *args, **kwargs):
        """Set the order of registered_labels.

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

        Parameters
        ----------
        registered_labels : List[:obj:`disseminate.label_manager.Label`]
            The list of registered_labels that have been vetted, processed and
            registered.
        exclude_labels : tuple of :class:`disseminate.labels.Label`
            Labels that match the specified classes will not be ordered.
            Presumably
            they'll be ordered by another function.
        """
        # Keep track of the counts for each kind
        count = Counter()

        # Retrieve the label_resets.
        if 'label_resets' in self.context:
            reset_counts = self.context['label_resets']
        else:
            reset_counts = dict()

        # Process labels that should not be filtered out and those with
        # a kind listed.
        filtered_labels = [label for label in self.filter(registered_labels)
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
