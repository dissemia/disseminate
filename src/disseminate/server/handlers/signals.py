"""
A request handler for rendering the signals.
"""
from .server import ServerHandler
from ...signals.signals import signals
from ...utils.string import stub


class SignalHandler(ServerHandler):
    """A request handler for the signals"""

    def get(self):
        # Get the signals
        signals_dict = self.signals_to_dict(signal_namespace=signals)

        self.render('signals.html', signals=signals_dict)

    def signals_to_dict(self, signal_namespace):
        """Given a list of processor classes, prepare a list of dicts listing
        the sub-processors
        Parameters
        ----------
        signal_namespace : :obj:`.signals.signals.Namespace`
        """
        signals_list = []

        # Sort the processor_clses
        for count, (name, signal) in enumerate(signal_namespace.items(), 1):
            d = dict()

            # populate the meta data
            d['name'] = name

            # Get the docstring (first line), if available
            if getattr(signal, '__doc__', None) is not None:
                docstring = stub(signal.__doc__)
                d['doc'] = docstring

            # Get the receivers for the signal
            receiver_items = signal.receivers_dict().items()
            receivers = list(enumerate(sorted(receiver_items)))
            receiver_list = d.setdefault('receivers', [])

            for count, (order, receiver) in receivers:
                r = dict()
                r['name'] = receiver.__name__
                r['order'] = order

                if receiver.__doc__ is not None:
                    docstring = stub(receiver.__doc__)
                    r['doc'] = docstring

                receiver_list.append(r)

            signals_list.append(d)

        return signals_list
