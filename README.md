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
- movement implementation
- reading and writing of level collections in `.sok`, `.xsb`, `.tsb`, `.hsb` and `.txt`
  file formats

It provides two implementations:

- `sokoenginepy` - pure Python implementation
- `libsokoengine` - C++ library that re-implements most of the Python stuff in C++

## Install

- `sokoenginepy` package from [PyPi]:

   ```sh
   pip install sokoenginepy
   ```

- `libsokoengine` library (completely optional):

   ```sh
   sudo apt install git build-essential libboost-graph-dev cmake libdw-dev \
     binutils-dev doxygen
   git clone https://github.com/tadams42/sokoenginepy.git
   cd sokoenginepy/
   cmake --preset "debug"
   cd build/debug/
   make && make install
   ```

C++ library is completely optional. On Linux, Python package may utilize it for raw
speed. It can also be built independently and consumed by other C++ projects via
[cmake]. For more elaborate details, see [INSTALL.md](./INSTALL.md)

## Why?

- experimenting with [Boost.Graph] in C++ and [NetworkX] in Python
- experimenting with [pybind11]
- playing with Sokoban file formats; conversion and validation, especially for Hexoban
  variant
- ...

## Documentation

- [Tutorial - Python](./docs/tutorial_python.md)
- [Tutorial - C++](./docs/tutorial_cpp.md)
- [Python docs](http://sokoenginepy.readthedocs.io/en/latest/)
- [C++ docs](http://tadams42.github.io/sokoenginepy/)

[Boost.Graph]: https://www.boost.org/doc/libs/1_78_0/libs/graph/doc/index.html
[NetworkX]: https://networkx.org/
[pybind11]: http://pybind11.readthedocs.io/en/stable/index.html
[PyPi]: https://pypi.org/
[cmake]: https://cmake.org/
