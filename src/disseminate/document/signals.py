"""
Signals for document events
"""

from ..signals import signal

document_created = signal('document_created',
                          doc="Signal sent after document creation. "
                              "Receivers take a document parameter.")
document_deleted = signal('document_deleted',
                          doc="Signal sent before a document is deleted. "
                          "Receivers take a document parameter.")
document_onload = signal('document_onload',
                         doc="Signal sent when a document is loaded. "
                         "Receivers take a document or document context "
                         "parameter.")
