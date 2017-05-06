#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from __future__ import absolute_import, print_function

import io
import re
from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import find_packages, setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name="sokoenginepy",
    version='0.5.0',
    license="GPLv3",
    description="Sokoban and variants game engine",
    long_description='%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst'))
    ),
    author="Tomislav Adamic",
    author_email="tomislav.adamic@gmail.com",
    url="https://github.com/tadamic/sokoenginepy",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 3 :: Only',
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ],
    keywords=[
        'game', 'sokoban', 'hexoban', 'octoban', 'trioban'
    ],
    # List run-time dependencies HERE.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'pytz >=2016.6.1',
        'pyparsing >=2.1.0',
        'networkx >=1.11',
        # Alternative that is A LOT faster but install through pip is not supported
        # 'graph-tool >=2.11'
        'cached-property >=1.2.0'
    ],
    # List additional groups of dependencies HERE (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev]
    extras_require={
        'dev': [
            'pycodestyle >= 2.0.0',  # (formerly called pep8)
            'mccabe >= 0.5.0',
            'pylint >= 1.6.0',
            'yapf >= 0.11.0',
            'bumpversion >= 0.5.3',
            'isort',

            # IPython stuff
            'ipython >= 5.0.0',
            'jupyter >= 1.0.0',
            'ipdb >= 0.10.0',

            # Docs and viewers
            'sphinx >= 1.4.0',
            'sphinx_rtd_theme >= 0.1.9',

            # py.test stuff
            'pytest-colordots >= 0.1.0',
            'colored-traceback >= 0.2.0',
            'pytest >= 3.0.0',
            'pytest-spec >= 1.0.0',
            'pytest-cov >= 2.3.0',
            'pytest-runner',  # Needed for `python setup.py test` to work
            'check-manifest >= 0.33.0',
            'coverage >= 4.2.0',
            'pytest-benchmark >= 3.0.0',
            'factory-boy >= 2.8.0',
            'faker >= 0.6.0',
        ]
    },
    # If there are data files included in your packages that need to be
    # installed, specify them HERE.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={'sokoenginepy': ['res/*'],},
)
