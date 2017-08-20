#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from __future__ import absolute_import, print_function

import io
import os
import re
from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import Extension, find_packages, setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


def configure_native_extension():
    # TODO: configure script for native extension should:
    #     - figure out Python version under which we are installing
    #     - find Boost.Python for that version
    #     - be portable
    LIBBOOST_PYTHON = (
        'boost_python-py35'
        if os.path.exists('/usr/lib/x86_64-linux-gnu/libboost_python-py35.so')
        else None
    )

    if LIBBOOST_PYTHON:
        libsokoengine = Extension(
            name='libsokoengine',
            sources=[
                os.path.join('src', 'libsokoengine', file_name) for file_name in [
                    'direction.cpp',
                    'board_cell.cpp',
                    'atomic_move.cpp',
                    'board_graph.cpp',
                    'tessellation_base.cpp',
                    'sokoban_tessellation.cpp',
                    'hexoban_tessellation.cpp',
                    'octoban_tessellation.cpp',
                    'trioban_tessellation.cpp',
                ]
            ] + [
                os.path.join('src', 'ext', file_name) for file_name in [
                    'export_common.cpp',
                    'export_direction.cpp',
                    'export_board_cell.cpp',
                    'export_atomic_move.cpp',
                    'export_board_graph.cpp',
                    'export_tessellations.cpp',
                    'export_libsokoengine.cpp',
                ]
            ],
            libraries=[LIBBOOST_PYTHON, 'boost_graph'],
            include_dirs=[
                'src',
                os.path.join('src', 'libsokoengine'),
                os.path.join('src', 'ext')
            ],
            language='c++',
            extra_compile_args=[
                '-std=c++14',
                '-Wno-overloaded-virtual',
                '-Wno-sign-compare',
                '-Wno-unused-parameter',
                '-Wno-attributes'
            ],
            optional=True
        )
        return [libsokoengine]

    return []

setup(
    name="sokoenginepy",
    version='0.4.3',
    license="GPLv3",
    description="Sokoban and variants game engine",
    long_description='%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst'))
    ),
    author="Tomislav Adamic",
    author_email="tomislav.adamic@gmail.com",
    url="https://github.com/tadams42/sokoenginepy",
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
        'cached-property >=1.2.0'
    ],
    # List additional groups of dependencies HERE (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev]
    extras_require={
        'dev': [
            'pycodestyle',
            # 'mccabe',
            # 'pylint',
            'yapf',
            'bumpversion',
            'isort',
            'check-manifest',

            # IPython stuff
            'ipython',
            'jupyter',
            'ipdb',

            # Docs and viewers
            'sphinx',
            'sphinx_rtd_theme',

            # py.test stuff
            'pytest >= 3.0.0',
            'pytest-pythonpath',
            'colored-traceback',
            # 'pytest-colordots',
            'pytest-spec',
            'pytest-sugar',
            'pytest-cov',
            'pytest-benchmark',
            'pytest-mock',

            'coverage',
            'factory-boy',
            'faker',
        ]
    },
    # If there are data files included in your packages that need to be
    # installed, specify them HERE.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={'sokoenginepy': ['res/*'],},
    ext_modules=configure_native_extension()
)
