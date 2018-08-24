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
import tempfile
from glob import glob
from os.path import basename, dirname, join, splitext

import setuptools
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


class SokoenginepyExtension(Extension):
    """
    Describes ``sokoenginepyext`` native C++ extension for ``sokoenginepy``.

    On ``Linux``, ``pip install sokoenginepy`` will try to configure and build
    native extension. If this fails, extension will not be installed but package
    still will be.

    On all other systems, native extension is not supported and will not be
    configured or built - only Python code will be installed by ``pip``.
    """

    NAME = 'sokoenginepyext'

    SHOULD_TRY_BUILD = (
        # We support building only on Linux...
        os.name == 'posix'

        # ... and not on Read The Docs
        and os.environ.get('READTHEDOCS', 'false').lower() not in [
            'yes', 'true', 'y', '1'
        ]

        # ... and allow build to be controlled by SOKOENGINEPYEXT_BUILD
        # environment variable
        and os.environ.get('SOKOENGINEPYEXT_BUILD', 'true').lower() in [
            'yes', 'true', 'y', '1'
        ]
    )

    IS_DEBUG = os.environ.get('SOKOENGINEPYEXT_DEBUG', 'false').lower() in [
        'yes', 'true', 'y', '1'
    ]

    CXXFLAGS = [
        '-std=c++14',
        '-Wno-sign-compare',
        '-fvisibility=hidden'
    ] + (
        [
            '-g3',
            '-O0',
            '-UNDEBUG',
            '-DDEBUG'
        ]
        if IS_DEBUG else
        [
            '-O3',
            # Link time optimization is cool, but wreaks havoc in my current
            # dev env (Ubuntu 17.10, gcc 7.2, Python 3.6.2)
            # '-flto'
        ]
    )

    LDFLAGS = [
    ] + (
        [
        ]
        if IS_DEBUG else
        [
            # Link time optimization is cool, but wreaks havoc in my current
            # dev env (Ubuntu 17.10, gcc 7.2, Python 3.6.2)
            # '-flto'
        ]
    )

    SRC_DIR = 'lib/libsokoengine/src'
    EXT_DIR = 'lib/libsokoengine/ext'
    LIB_DIR = 'lib/libsokoengine/lib'

    SOURCES = [
        os.path.join(dir_path, file_name)
        for top_dir in [SRC_DIR, EXT_DIR]
        for dir_path, directories, files in os.walk(top_dir)
        for file_name in files
        if file_name.endswith('.cpp')
    ]

    def __init__(self):
        super().__init__(
            name=self.NAME,
            sources=self.SOURCES,
            include_dirs=(
                [
                    dir_path
                    for dir_path, directories, files in os.walk(self.SRC_DIR)
                ] + [
                    dir_path
                    for dir_path, directories, files in os.walk(self.EXT_DIR)
                ] + [
                    self.LIB_DIR,
                    self._pybind11_include_dir(user=False),
                    self._pybind11_include_dir(user=True)
                ]
            ),
            language='c++',
            optional=True,
            extra_compile_args=self.CXXFLAGS,
            extra_link_args=self.LDFLAGS
        )

    BOOST_HEADERS = list({
        line.strip()
        for file_path in SOURCES
        for line in open(file_path, 'r')
        if '#include <boost' in line
    })

    @classmethod
    def configure(cls, compiler):
        """
        Should be ran before trying to compile the extension.

        - Fetches some of the compile time dependencies (ie. header-only C++
        libraries that we don't want to distribute as part of our library
        since they are available from GitHub).
        - Checks for system wide headers by compiling small snippets of code
        against them

        Returns:
            bool: True if everything is OK and extension can be compiled. False
                if extension was not selected for build or some of
                configuration steps fail.
        """

        if not cls.SHOULD_TRY_BUILD:
            return False

        print("configuring '{}' extension".format(cls.NAME))

        boost_ok = True
        with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
            f.write("\n".join(sorted(cls.BOOST_HEADERS)) + "\n")
            f.write('int main (int argc, char **argv) { return 0; }')
            f.flush()
            try:
                compiler.compile([f.name])
            except setuptools.distutils.errors.CompileError:
                boost_ok = False

        if not boost_ok:
            print((
                "'{}' extension build was requested but it will be skipped "
                "because Boost headers are missing."
            ).format(cls.NAME))
            return False

        cppitertools_dir = os.path.join(
            os.path.abspath(cls.LIB_DIR), 'cppitertools'
        )
        if not os.path.exists(cppitertools_dir):
            print('Cloning cppitertools...')
            os.system(
                'git clone https://github.com/ryanhaining/cppitertools.git "{}"'.format(
                    cppitertools_dir
                )
            )

        print("successfully configured '{}' native extension".format(cls.NAME))

        return True

    class _pybind11_include_dir:
        """
        Hack to postpone importing and calling on ``pybind11`` until it
        is actually installed.

        https://github.com/pybind/python_example/blob/master/setup.py
        https://github.com/pybind/python_example/issues/16
        """

        def __init__(self, user=False):
            self.user = user

        def __str__(self):
            import pybind11
            return pybind11.get_include(self.user)


class BuildExt(build_ext):
    def build_extensions(self):
        if (
            'sokoenginepyext' in [ext.name for ext in self.extensions]
            and SokoenginepyExtension.configure(self.compiler)
        ):
            self.extensions = [
                ext for ext in self.extensions if ext.name != 'sokoenginepyext'
            ]

        return super().build_extensions()


setup(
    name='sokoenginepy',
    version='0.5.3',
    license='GPLv3',
    description='Sokoban and variants game engine',
    long_description='%s\n%s' % (
        re.compile(
            '^' + re.escape('[//]: # (start-badges)') + '.*^'
            + re.escape('[//]: # (end-badges)'), re.M | re.S
        ).sub('', read('README.md')),
        # re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
        ''
    ),
    # In the future this will correctly render Markdown on PyPi:
    # long_description_content_type='text/markdown',
    author='Tomislav Adamic',
    author_email='tomislav.adamic@gmail.com',
    url='https://github.com/tadams42/sokoenginepy',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Games/Entertainment :: Puzzle Games',
    ],
    keywords=[
        'game', 'sokoban', 'hexoban', 'octoban', 'trioban'
    ],
    # List run-time dependencies HERE.  These will be installed by pip when
    # your project is installed. For an analysis of 'install_requires' vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'pytz >=2016.6.1',
        'pyparsing >=2.1.0',
        'networkx <2.0.0',
        'cached-property >=1.2.0',
        'pybind11>=2.2.0'
    ],
    # List additional groups of dependencies HERE (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev]
    extras_require={
        'docs': [
            'sphinx >= 1.4',
            'sphinx_rtd_theme',
            'm2r >= 0.1.14',
        ],
        'dev': [
            'pycodestyle',
            'pylint',
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
            'm2r',

            # py.test stuff
            'pytest >= 3.0.0',
            'pytest-pythonpath',
            'colored-traceback',
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
    ext_modules=[SokoenginepyExtension()],
    cmdclass={'build_ext': BuildExt}
)
