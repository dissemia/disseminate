"""
A listing of the external dependencies.
"""
from .checkers.types import All, Any, Optional


python_deps = All('python',
                  Any('executables',
                      'python3.6', 'python3.7', 'python3.8', 'python3.9'),
                  All('packages',
                      'regex>=2018.11.22', 'jinja2>=2.11', 'lxml>=4.3.0',
                      'python-slugify>=2.0.1', 'pdfCropMargins>=0.1.4',
                      'click>=7.0', 'tornado>=6.1', 'pygments >=2.6',
                      'diskcache>=4.1', 'pathvalidate>=2.2'))

image_deps = Optional('image external dependencies',
                      Optional('executables',
                               'asy', 'convert', 'pdf2svg', 'pdf-crop-margins',
                               'rsvg-convert'))

pdf_deps = All('pdf',
               All('executables',
                   Any('compilers',
                       'pdflatex', 'xelatex', 'lualatex'),
                   Any('package_managers',
                       'kpsewhich',)),
               All('packages',
                   'graphicx', 'caption', 'amsmath', 'mathtools', 'bm',
                   'easylist', 'fancyvrb',
                   'hyperref', 'enumitem', 'geometry', 'xcolor'),
               Optional('fonts',
                        'ecrm1200', 'tcrm1200'),
               Optional('classes',
                        'article', 'report', 'tufte-book', ),
               )
