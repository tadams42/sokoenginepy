# sokoenginepy - Sokoban and variants game engine

[![PyPI](https://img.shields.io/pypi/s/sokoenginepy.svg)](https://img.shields.io/pypi/s/sokoenginepy.svg)
[![TravisCI](https://travis-ci.org/tadamic/sokoenginepy.svg?branch=development)](https://travis-ci.org/tadamic/sokoenginepy)
[![Language](http://img.shields.io/badge/language-Python3-lightgrey.svg)](https://www.python.org/)
[![License](http://img.shields.io/badge/license-GPLv3-brightgreen.svg)](http://opensource.org/licenses/GPL-3.0)
[![Coverage Status](https://coveralls.io/repos/tadamic/sokoenginepy/badge.png?branch=development)](https://coveralls.io/r/tadamic/sokoenginepy?branch=development)

sokoenginepy is game engine for Sokoban and variants written in Python and
loaded with features:

- implements game logic for `Sokoban`, `Hexoban`, `Trioban` and `Octoban` variants
    - supports `Sokoban+` for all implemented variants
    - supports `Multiban` (muliple pushers on board) for all variants
- two game engines implementations
    - fast and memory lightweight with single step undo/redo
    - somewhat slower and larger with unlimited movement undo/redo
- reading and writing level collections
    - fully compatible with [SokobanYASC] .sok file format and variants (.xsb, .tsb, .hsb, .txt)

sokoenginepy was inspired by [SokobanYASC], [JSoko] and [MazezaM]

## Install

Installing sokoenginepy should be as simple as::

    pip install sokoenginepy

Note that sokoenginepy requires Python 3.3 or newer.

[SokobanYASC]:http://sourceforge.net/projects/sokobanyasc/
[JSoko]:http://www.sokoban-online.de/
[MazezaM]:http://webpages.dcu.ie/~tyrrelma/MazezaM/
