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

document_render = signal('document_render',
                         doc="Signal sent when a document's targets are "
                         "being rendered to their final target files. "
                         "Receivers take a document parameter.")

document_tree_updated = signal('document_tree_updated',
                               doc="Signal sent when a root document or one "
                               "of its sub-documents was re-loaded. Takes a "
                               "root document as a parameter.")
