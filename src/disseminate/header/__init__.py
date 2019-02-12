"""
The header module converts header strings to dicts for context objects
(:obj:`BaseContext <disseminate.context.context.BaseContext>`).

The header sub-module has the following responsibilities:

1. *Header parsing*. Interpret a string in YAML format and convert it to a dict
   for the context.
"""

from .header import parse_header_str, load_header
