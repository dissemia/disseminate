"""
Signals for target builders
"""
from ...signals import signal

add_file = signal("add_file",
                  doc="Add a file dependency to a target builder. Takes "
                      "parameters, context, in_ext, target and use_cache.")

add_dependencies = signal("add_dependencies",
                          doc="Collect and add a parameter dependencies to a "
                              "target builder. Takes a context.")
