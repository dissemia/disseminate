"""Disseminate

A document processing system and static site generator for textbooks, books,
novels, articles, reports and essays.

Documentation: https://docs.dissemia.org/projects/disseminate/en/latest
Github: https://github.com/dissemia/disseminate
PyPI: https://pypi.org/project/disseminate/

Disseminate
Copyright (C) 2017-2021 Dissemia Foundatian,
Justin Lorieau <justin at lorieau dot com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

License: AGPL-3.0-only
"""

from setuptools import setup, find_packages
from codecs import open
import os


here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get the version number and package information.  The __version__.py
# file is executed so that the disseminate package is not loaded.  At
# this point, the C/C++ extensions may not be built, and loading the
# package will lead to an ImportError. This approach circumvents this problem.
__version__ = None  # This is a version string
VERSION = None  # This is a 5-item version tuple
exec(open("./src/disseminate/__version__.py").read())

# Organize classifiers
if VERSION[3] == 'alpha':
    classifiers = ['Development Status :: 3 - Alpha', ]
elif VERSION[3] == 'beta':
    classifiers = ['Development Status :: 4 - Beta', ]
elif VERSION[3] == 'rc':
    classifiers = ['Development Status :: 4 - Beta', ]
elif VERSION[3] == 'final':
    classifiers = ['Development Status :: 5 - Production/Stable', ]
else:
    classifiers = []


classifiers += [
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Science/Research',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Text Processing',
    'Topic :: Text Processing :: General',
    'Topic :: Text Processing :: Markup',
    'Topic :: Text Processing :: Markup :: HTML',
    'Topic :: Text Processing :: Markup :: LaTeX',
    'Topic :: Internet :: WWW/HTTP :: Site Management',
    'Topic :: Software Development :: Documentation']


setup(
    name='disseminate',  # Required
    version=__version__,
    url='https://docs.dissemia.org/projects/disseminate/en/latest',
    project_urls={
        'Documentation': ('https://docs.dissemia.org/projects/'
                          'disseminate/en/latest'),
        'GitHub Project': 'https://github.com/dissemia/disseminate',
        'Issue Tracker': 'https://github.com/dissemia/disseminate/issues'
    },
    description='A document processor and generation engine',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Justin L Lorieau, Dissemia Foundation',
    license='AGPLv3',
    classifiers=classifiers,
    keywords='document processor academic publishing',
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,  # include MANIFEST.in
    install_requires=[
        'regex>=2018.11.22',         # No license, replaced with re
        'jinja2>=3.0',               # 3-clause BSD
        'lxml>=4.3.0',               # BSD license
        'python-slugify>=2.0.1',     # MIT license
        'pdfCropMargins>=0.1.4',     # GPL v3
        # The following are needed for the CLI
        'click>=7.0',                # 3-clause BSD license
        # The following are needed for the preview function
        'tornado>=6.1',
        # The following is needed for the @code tag
        'pygments>=2.6',             # BSD 2 license
        'diskcache>=4.1',
        'pathvalidate>=2.2'],
    extras_require={  # Optional
        'dev': ['sphinx', 'sphinx_rtd_theme', 'sphinx-click', 'numpydoc',
                'asv'],
        'test': ['pytest', 'pytest-cov', 'tox', 'coverage', 'flake8',
                 'epubcheck>=0.4'],
        'termcolor': ['termcolor']  # MIT license
    },
    scripts=['scripts/dm', ],
    entry_points={
        'console_scripts': [
            'dm = disseminate.cli:main'],
        'pygments.lexers': [
            'dmlexer = disseminate.utils.pygments.dm:DmLexer'
        ]
    }
)
