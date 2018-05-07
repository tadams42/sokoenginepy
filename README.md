# sokoenginepy - Sokoban and variants game engine

[//]: # (start-badges)

[![version](https://img.shields.io/pypi/v/sokoenginepy.svg)](https://pypi.org/project/sokoenginepy/)
[![license](https://img.shields.io/pypi/l/sokoenginepy.svg)](https://opensource.org/licenses/GPL-3.0)
[![wheel](https://img.shields.io/pypi/wheel/sokoenginepy.svg)](https://pypi.org/project/sokoenginepy/)
[![python_versions](https://img.shields.io/pypi/pyversions/sokoenginepy.svg)](https://pypi.org/project/sokoenginepy/)
[![python_implementations](https://img.shields.io/pypi/implementation/sokoenginepy.svg)](https://pypi.org/project/sokoenginepy/)
[![travis](https://api.travis-ci.org/tadams42/sokoenginepy.svg)](https://travis-ci.org/tadams42/sokoenginepy)
[![docs](https://readthedocs.org/projects/sokoenginepy/badge/?style=flat)](http://sokoenginepy.readthedocs.io/en/latest/)
[![requirements](https://requires.io/github/tadams42/sokoenginepy/requirements.svg?branch=master)](https://requires.io/github/tadams42/sokoenginepy/requirements/?branch=master)
[![codacy_grade](https://api.codacy.com/project/badge/Grade/492a7c08b97e4dbe991b0190dd3abf02)](https://app.codacy.com/app/tadams42/sokoenginepy/dashboard)
[![codacy_coverage](https://api.codacy.com/project/badge/Coverage/492a7c08b97e4dbe991b0190dd3abf02)](https://app.codacy.com/app/tadams42/sokoenginepy/dashboard)

[//]: # (end-badges)

sokoenginepy is game engine for Sokoban and variants, written in Python and loaded with features:

* implements game logic for `Sokoban`, `Hexoban`, `Trioban` and `Octoban` variants
  + supports `Sokoban+` for all implemented variants
  + supports `Multiban` (muliple pushers on board) for all variants
* reading and writing level collections
  + fully compatible with [SokobanYASC] .sok file format and variants (.xsb, .tsb, .hsb, .txt)
* Optional C++ native bindings using [pybind11] and [Boost.Graph] for ultimate speed

`sokoenginepy` was inspired by [SokobanYASC], [JSoko], and MazezaM

## Installing

Installing `sokoenginepy` should be as simple as

~~~sh
pip install sokoenginepy
~~~

This will also compile and install native C++ extension that greatly improves speed of `sokoenginepy` but is available only on Linux for now. To make this happen, you also need this:

~~~sh
sudo apt install python3-dev libboost-graph-dev
~~~

On non-Linux systems, only pure Python gets installed, which gives you exactly same API but with less speed in some of CPU hungry operations.

All other glory details are here: [INSTALL]

## Using

* For quick glance of features and usage check the [Tutorial].
* For in-depth docs of whole package see [API Reference]
* For C++ library API docs see [C++ API Reference]

[pybind11]: http://pybind11.readthedocs.io/en/stable/index.html
[NetworkX]: https://networkx.github.io/
[Boost.Graph]: https://www.boost.org/doc/libs/1_61_0/libs/graph/doc/index.html
[SokobanYASC]: https://sourceforge.net/projects/sokobanyasc/
[JSoko]: https://www.sokoban-online.de/
[Sokobano]: http://sokobano.de/en/index.php
[Sokoban for Windows]: http://www.sourcecode.se/sokoban/
[Tutorial]: https://sokoenginepy.readthedocs.io/en/latest/tutorial.html
[API reference]: https://sokoenginepy.readthedocs.io/en/latest/api.html
[INSTALL]: http://sokoenginepy.readthedocs.io/en/latest/install.html
[C++ API Reference]: http://tadams42.github.io/sokoenginepy/
