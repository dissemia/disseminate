"""
Tag event signals
"""
import weakref
from types import MethodType

from ..signals import signal

tag_created = signal('tag_created', doc=("A signal emitted when a tag is "
                                         "created. Receivers take a tag "
                                         "parameter."))


def emit(self, tag, **kwargs):
    """A custom emitter that checks which receivers to run based on attributes
    in the tag object."""
    return_values = []
    for order, receiver in sorted(self.receivers.items()):
        # De-reference receiver, if needed
        receiver = (receiver() if isinstance(receiver, weakref.ref) else
                    receiver)

        # Only run the receiver if it exists and the tag doesn't have
        # an attribute with the receiver's name as False.
        # ex: tag.process_content = False
        #     will not run the 'process_content' receiver
        if (receiver is not None and
           getattr(tag, receiver.__name__, True)):  # here is the difference
            return_values.append(receiver(tag=tag, **kwargs))
        else:
            return_values.append(None)
    return return_values


tag_created.emit = MethodType(emit, tag_created)
