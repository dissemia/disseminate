"""
A listing of the external dependencies.
"""
from .checkers.types import All, Any, Optional


python_deps = All('python',
                  Any('executables',
                      'python3.6', 'python3.7'),
                  All('packages',
                      'regex>=2018.11.22', 'jinja2>=2.10', 'lxml>=4.3.0',
                      'python-slugify>=2.0.1', 'click>=7.0',
                      'pdfCropMargins>=0.1.4', 'sanic>=19.0',))

image_deps = Optional('image external dependencies',
                      Optional('executables',
                               'asy', 'pdf2svg', 'pdf-crop-margins',
                               'rsvg-convert'))

pdf_deps = All('pdf',
               All('executables',
                   Any('compilers',
                       'pdflatex', 'xelatex', 'lualatex'),
                   Any('package_managers',
                       'kpsewhich',)),
               All('packages',
                   'graphicx', 'caption', 'amsmath', 'mathtools', 'bm',
                   'hyperref', 'enumitem', 'geometry', 'xcolor'),
               Optional('fonts',
                        'ecrm1200'),
               Optional('classes',
                        'article', 'report', 'tufte-book', ),
               )
