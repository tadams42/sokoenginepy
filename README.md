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

It provides two almost identical implementations:

- `sokoneginepy` - Python implementation and package
- `libsokoengine` - C++ library with API that is 99.99% identical to Python

On Linux, Python package can also be optionally built with native extensions so that it
utilizes `libsokoengine` for raw speed.

`libsokoengine` can be built completely independently, and consumed by native C++
clients.

## Why?

- experimenting with [Boost.Graph] in C++ and [NetworkX] in Python
- experimenting with [pybind11]
- playing with Sokoban file formats; conversion and validation, especially for Hexoban
  variant
- ...

## Install

`sokoenginepy` package from [PyPi]:

```sh
pip install sokoenginepy
```

- `libsokoengine` can be built from source code, details are in `INSTALL.md`
- `sokoenginepy`  can be optionally built with native C++ extensions, details are in
  `INSTALL.md`

## Documentation

- [Python usage tutorial](https://sokoenginepy.readthedocs.io/en/latest/tutorial.html)
- [Python docs](http://sokoenginepy.readthedocs.io/en/latest/)
- [C++ docs](http://tadams42.github.io/sokoenginepy/)

[SokobanYASC]: https://sourceforge.net/projects/sokobanyasc/
[Boost.Graph]: https://www.boost.org/doc/libs/1_78_0/libs/graph/doc/index.html
[NetworkX]: https://networkx.org/
[pybind11]: http://pybind11.readthedocs.io/en/stable/index.html
