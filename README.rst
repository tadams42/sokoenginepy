============
sokoenginepy
============

.. image:: https://img.shields.io/pypi/v/sokoenginepy.svg
  :target: https://pypi.python.org/pypi/sokoenginepy
  :alt: PyPI release version

.. image:: https://travis-ci.org/tadamic/sokoenginepy.svg?branch=development
  :target: https://travis-ci.org/tadamic/sokoenginepy
  :alt: TravisCI status

.. image:: https://coveralls.io/repos/tadamic/sokoenginepy/badge.svg?branch=development
  :target: https://coveralls.io/github/tadamic/sokoenginepy?branch=development
  :alt: Coveralls status

.. image:: https://readthedocs.org/projects/sokoenginepy/badge/
  :target: http://sokoenginepy.readthedocs.org/
  :alt: Documentation Status

.. image:: https://img.shields.io/badge/language-Python3-blue.svg
  :target: https://www.python.org/
  :alt: Language

.. image:: https://img.shields.io/badge/license-GPLv3-brightgreen.svg
  :target: http://opensource.org/licenses/GPL-3.0
  :alt: License


Sokoban and variants game engine
--------------------------------

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

sokoenginepy was inspired by `SokobanYASC`_, `JSoko`_, `MazezaM`_

Install
-------

Installing sokoenginepy should be as simple as::

    pip install sokoenginepy

Note that sokoenginepy requires Python 3.4 or newer.

.. _SokobanYASC: http://sourceforge.net/projects/sokobanyasc/
.. _JSoko: http://www.sokoban-online.de/
.. _MazezaM: http://webpages.dcu.ie/~tyrrelma/MazezaM/
