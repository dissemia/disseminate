"""Disseminate is a document processor and generation engine.
"""

from setuptools import setup, find_packages
from codecs import open
from os import path
from glob import glob
from os.path import basename, dirname, join, splitext


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='disseminate',  # Required
    version='0.1',
    description='A document processor and generation engine',
    long_description=long_description,
    # url='https://github.com/pypa/sampleproject',
    author='Justin L Lorieau',
    classifiers=[  
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    # keywords='sample setuptools development',  # Optional
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=['regex', 'jinja2',  'pyyaml'],
    extras_require={  # Optional
        'dev': ['sphinx', 'sphinx_rtd_theme', 'numpydoc'],
        'test': ['pytest', 'tox'],
    },
)
