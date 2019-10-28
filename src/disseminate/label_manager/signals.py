"""
Signals for processing labels.
"""
from ..signals import signal

label_register = signal('label_register', doc="A signal sent when labels are "
                        "to be registered. Receivers take registered labels "
                        "(a list of labels) and collected labels (dict of "
                        "labels)")
