"""
Signals for target builders
"""
from ...signals import signal

add_file = signal("add_file",
                  doc="Add a file dependency to a target builder. Takes "
                      "parameters, context, in_ext, target and use_cache.")

find_builder = signal("find_builder",
                      doc="Given a document context and a target, find the "
                          "corresponding target builder.")
