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
import tempfile
from glob import glob
from os.path import basename, dirname, join, splitext

import setuptools
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ).read()


class fix_pybind11_include_dir:
    """
    Hack to postpone importing and calling on ``pybind11`` until it
    is actually installed.

    https://github.com/pybind/python_example/blob/master/setup.py
    https://github.com/pybind/python_example/issues/16
    """

    def __str__(self):
        import pybind11

        return pybind11.get_include()


class SokoenginepyExtension(Extension):
    """
    Describes ``sokoenginepyext`` native C++ extension for ``sokoenginepy``.

    On ``Linux``, ``pip install sokoenginepy`` will try to configure and build native
    extension. If build fails, ``sokoenginepy`` will be installed without native
    extension. To succeed, boost header have to be in system include path.

    On all other systems, native extension will not be installed.
    """

    NAME = "sokoenginepyext"

    IS_DEBUG = os.environ.get("SOKOENGINEPYEXT_DEBUG", "false").lower() in [
        "yes",
        "true",
        "y",
        "1",
    ]

    SHOULD_TRY_BUILD = (
        # We support building only on Linux...
        os.name == "posix"
        # ... and not on Read The Docs
        and os.environ.get("READTHEDOCS", "false").lower()
        not in ["yes", "true", "y", "1"]
        # ... and allow build to be controlled by SOKOENGINEPYEXT_BUILD
        # environment variable
        and os.environ.get("SOKOENGINEPYEXT_BUILD", "true").lower()
        in ["yes", "true", "y", "1"]
    )

    CXXFLAGS_RELEASE = ["-O3", "-flto", "-UDEBUG", "-DNDEBUG"]

    CXXFLAGS_DEBUG = ["-g3", "-O0", "-UNDEBUG", "-DDEBUG"]

    CXXFLAGS = [
        "-std=c++14",
        "-fvisibility=hidden",
        "-fPIC",
        "-DBOOST_BIND_NO_PLACEHOLDERS",
        "-DBOOST_MULTI_INDEX_DISABLE_SERIALIZATION",
    ] + (CXXFLAGS_DEBUG if IS_DEBUG else CXXFLAGS_RELEASE)

    LDFLAGS = ["-flto"] if not IS_DEBUG else []

    SOURCES = [
        os.path.join(dir_path, file_name)
        for _ in ["src/libsokoengine", "src/sokoenginepyext"]
        for dir_path, directories, files in os.walk(_)
        for file_name in files
        if file_name.endswith(".cpp")
    ]

    def __init__(self):
        super().__init__(
            name=self.NAME,
            sources=self.SOURCES,
            include_dirs=["/tmp/cmake_cache", fix_pybind11_include_dir()]
            + [
                dir_path
                for _ in ["src/libsokoengine", "src/sokoenginepyext"]
                for dir_path, directories, files in os.walk(_)
            ],
            language="c++",
            optional=True,
            extra_compile_args=self.CXXFLAGS,
            extra_link_args=self.LDFLAGS,
        )

    CPPITERTOOLS_DIR = os.path.abspath("/tmp/cmake_cache/cppitertools")

    @classmethod
    def configure(cls, compiler):
        """
        Should be ran before trying to compile the extension.

        - Fetches some of the compile time dependencies (ie. header-only C++
          libraries that we don't want to distribute as part of our library since
          they are available from GitHub).
        - Checks for system wide headers by compiling small snippets of code against
          them

        Returns:
            bool: True if everything is OK and extension can be compiled. False if
                extension was not selected for build or some of configuration steps
                fail.
        """

        if not cls.SHOULD_TRY_BUILD:
            return False

        if not cls._does_boost_compile(compiler):
            return False

        if not cls._fetch_cppitertools():
            return False

        print("successfully configured '{}' native extension".format(cls.NAME))

        return True

    @classmethod
    def _fetch_cppitertools(cls):
        if not os.path.exists(cls.CPPITERTOOLS_DIR):
            print("Cloning cppitertools...")
            os.system(
                'git clone --branch v1.0 https://github.com/ryanhaining/cppitertools.git "{}"'.format(
                    cls.CPPITERTOOLS_DIR
                )
            )
        return True

    @classmethod
    def _does_boost_compile(cls, compiler):
        boost_ok = True
        with tempfile.NamedTemporaryFile("w", suffix=".cpp") as f:
            f.write("\n".join(sorted(cls._BOOST_INCLUDES)) + "\n")
            f.write("int main (int argc, char **argv) { return 0; }")
            f.flush()
            try:
                compiler.compile([f.name])
            except setuptools.distutils.errors.CompileError:
                boost_ok = False

        if not boost_ok:
            print(
                (
                    "'{}' extension build was requested but it will be skipped "
                    "because Boost headers are missing."
                ).format(cls.NAME)
            )
            return False

        return boost_ok

    _BOOST_INCLUDES = list(
        {
            line.strip()
            for file_path in SOURCES
            for line in open(file_path, "r")
            if "#include <boost" in line
        }
    )


class BuildExt(build_ext):
    def build_extensions(self):
        """
        Removes sokoenginepyext from list of extensions if it can't or shouldn't be
        built.
        """
        if "sokoenginepyext" in [
            ext.name for ext in self.extensions
        ] and not SokoenginepyExtension.configure(self.compiler):
            self.extensions = [
                ext for ext in self.extensions if ext.name != "sokoenginepyext"
            ]

        return super().build_extensions()


_DOCS_REQUIRES = [
    "m2r2",
    "sphinx >= 1.4",
    "sphinx_rtd_theme",
]
_TESTS_REQUIRES = [
    "check-manifest",
    "coverage",
    "factory-boy",
    "faker",
    "pytest >= 3.0.0",
    "pytest-mock",
]

setup(
    name="sokoenginepy",
    version="0.5.3",
    license="GPLv3",
    description="Sokoban and variants game engine",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Tomislav Adamic",
    author_email="tomislav.adamic@gmail.com",
    url="https://github.com/tadams42/sokoenginepy",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    python_requires=">= 3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ],
    keywords=["game", "sokoban", "hexoban", "octoban", "trioban"],
    install_requires=[
        "arrow",
        "pyparsing >=2.1.0",
        "networkx >2.5",
        "pybind11>=2.9",
    ],
    extras_require={
        "docs": _DOCS_REQUIRES,
        "tests": _TESTS_REQUIRES,
        "dev": [
            "black",
            "bump2version",
            "colored-traceback",
            # "ipdb",
            "ipython",
            "isort",
            # "jupyter",
            "pytest-benchmark",
            "pytest-spec",
            "twine",
        ]
        + _DOCS_REQUIRES
        + _TESTS_REQUIRES,
    },
    ext_modules=[SokoenginepyExtension()],
    cmdclass={"build_ext": BuildExt},
)
