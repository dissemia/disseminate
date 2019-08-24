"""
Signals for document events
"""

from blinker import signal

document_created = signal('document.created',
                          doc="Signal sent after document creation")
document_deleted = signal('document.deleted',
                          doc="Signal sent before a document is deleted")
