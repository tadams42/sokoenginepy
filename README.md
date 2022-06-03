# sokoenginepy - Sokoban and variants

[![version](https://img.shields.io/pypi/v/sokoenginepy.svg)](https://pypi.org/project/sokoenginepy/)
[![license](https://img.shields.io/pypi/l/sokoenginepy.svg)](https://opensource.org/licenses/GPL-3.0)
[![python_versions](https://img.shields.io/pypi/pyversions/sokoenginepy.svg)](https://pypi.org/project/sokoenginepy/)
[![python_implementations](https://img.shields.io/pypi/implementation/sokoenginepy.svg)](https://pypi.org/project/sokoenginepy/)
[![travis](https://app.travis-ci.com/tadams42/sokoenginepy.svg)](https://app.travis-ci.com/tadams42/sokoenginepy)
[![docs](https://readthedocs.org/projects/sokoenginepy/badge/?style=flat)](http://sokoenginepy.readthedocs.io/en/latest/)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/3dd265ede6bd4c38a2cd1250738a1bfa)](https://app.codacy.com/gh/tadams42/sokoenginepy/dashboard)
[![codecov](https://codecov.io/gh/tadams42/sokoenginepy/branch/development/graph/badge.svg?token=nnJAZHQyz9)](https://codecov.io/gh/tadams42/sokoenginepy)

This project implements various utilities for Sokoban:

- board representation for Sokoban, Hexoban, Trioban and Octoban variants with support
  for Sokoban+ and Multiban for all four variants
- game engine implementation (WIP)
- [SokobanYASC] compatible level collections file reader / writer

It provides two implementations:

- `sokoenginepy` - pure Python implementation
- `libsokoengine` - C++ library

## Install

- `sokoenginepy` package from [PyPi]:

   ```sh
   export SOKOFILEPYEXT_BUILD=false
   export SOKOENGINEPYEXT_BUILD=false
   pip install sokoenginepy
   ```

- `libsokoengine` C++ library (completely optional):

   ```sh
   sudo apt install git build-essential libboost-graph-dev cmake doxygen
   git clone https://github.com/tadams42/sokoenginepy.git
   cd sokoenginepy/
   cmake --preset "debug"
   cd build/debug/
   make && make install
   ```

C++ library is completely optional.

On Linux, it will be built automatically if possible when Python package is installed
and it will be used transparently to improve speed of Python code execution. If building
it fails, Python package will be installed without it.

On any OS, C++ library can also be built independently and consumed from other C++ code
via `cmake`. For more elaborate details, see [INSTALL.md](./INSTALL.md)

## Why?

- experimenting with [Boost.X3] in C++
- experimenting with [Boost.Graph] in C++
- experimenting with [NetworkX] in Python
- experimenting with [pybind11]
- playing with Sokoban file formats; conversion and validation, especially for Hexoban
  variant
- ...

## Documentation

Python and C++ API reference, tutorials and everything else is documented at [Read the
Docs].

[Boost.Graph]: https://www.boost.org/doc/libs/1_78_0/libs/graph/doc/index.html
[Boost.X3]: https://www.boost.org/doc/libs/1_79_0/libs/spirit/doc/x3/html/spirit_x3/preface.html
[NetworkX]: https://networkx.org/
[pybind11]: http://pybind11.readthedocs.io/en/stable/index.html
[PyPi]: https://pypi.org/
[cmake]: https://cmake.org/
[SokobanYASC]: https://sourceforge.net/projects/sokobanyasc/
[Read the Docs]: http://sokoenginepy.readthedocs.io/
