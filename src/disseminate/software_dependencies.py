"""
A listing of the external dependencies.
"""
from .checkers.types import All, Any, Optional


pdf_deps = All('pdf',
               All('executables',
                   Any('compilers',
                       'pdflatex', 'xelatex', 'lualatex'),
                   Any('package_managers',
                       'kpsewhich',)),
               All('packages',
                   'graphicx', 'caption', 'amsmath', 'mathtools', 'bm',
                   'hyperref', 'enumitem', 'geometry', 'xcolor'),
               Optional('classes',
                        'article', 'report', 'tufte-book', ),
               )
