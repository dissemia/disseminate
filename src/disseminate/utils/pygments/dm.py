"""
A Lexer for disseminate (.dm) source files.
"""
import re

from pygments.lexer import RegexLexer, bygroups, using
from pygments.lexers.data import YamlLexer
from pygments.token import *


class DmLexer(RegexLexer):
    name = 'Disseminate'
    aliases = ['dm']
    filenames = ['*.dm']

    flags = re.IGNORECASE | re.DOTALL
    tokens = {
        'root': [
            (r'(-{3,})[^-]+(-{3,})', using(YamlLexer)),
            (r'[^@]+', Text),
            (r'(@)'
             r'(?P<tag>[A-Za-z0-9][\w]*)'
             r'(?P<attributes>\[[^\]]+\])?'
             r'(?P<open>{)?', bygroups(Punctuation, Name.Tag, Name.Attribute, Text)),
        ],
    }
