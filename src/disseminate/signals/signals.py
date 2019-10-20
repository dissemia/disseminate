import weakref

from .exceptions import DuplicateSignal


class Signal(object):
    """A notification emitter.

    (Inspired by blinker)

    Attributes
    ----------
    receivers : Dict[int, Callable]
        A dict with the order (key) for a receiver (value) to run when the
        signal is emitted.
    """

    name = None
    receivers = None

    def __init__(self, name, doc=None):
        self.name = name
        if doc is not None:
            self.__doc__ = doc

        self.receivers = dict()

    def connect(self, receiver, order, weak=True):
        """Connect a receiver to this signal.

        Parameters
        ----------
        receiver : Callable
            A function that will be executed when this signal is emitted.
        order : int
            The order for this receiver to be run.
        weak : Optional[bool]
            If true, a weak reference will be stored for the receiver.
        """
        if order in self.receivers:
            msg = ("A receiver ({}) with order '{}' already exists in this "
                   "signal")

            raise DuplicateSignal(msg.format(self.receivers[order], order))
        self.receivers[order] = (weakref.ref(receiver) if weak else receiver)

    def connect_via(self, order, weak=True):
        """The decorator for connect"""
        def decorator(fn):
            self.connect(fn, order=order, weak=weak)
            return fn
        return decorator

    def emit(self, **kwargs):
        """Emit (send) the signal and run the receiver functions."""
        for order, receiver in sorted(self.receivers.items()):
            # De-reference receiver, if needed
            receiver = (receiver() if isinstance(receiver, weakref.ref) else
                        receiver)
            receiver(**kwargs)

    def reset(self):
        """Reset the signal to its initial state"""
        self.receivers.clear()


class Namespace(dict):
    """A mapping of signal names to signals."""

    def signal(self, name, doc=None):
        """Return a signal with the given name.

        Parameters
        ----------
        name : str
            The name of the signal
        doc : Optional[str]
            The description documentation for the signal.
        """
        try:
            return self[name]
        except KeyError:
            return self.setdefault(name, Signal(name, doc))


signal = Namespace().signal
