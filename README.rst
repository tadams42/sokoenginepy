sokoenginepy - Sokoban and variants game engine
***********************************************

.. image:: https://img.shields.io/pypi/l/sokoenginepy.svg
    :target: http://opensource.org/licenses/GPL-3.0
    :alt: License

.. image:: https://img.shields.io/pypi/v/sokoenginepy.svg
    :target: https://pypi.python.org/pypi/sokoenginepy
    :alt: PyPI Release

.. image:: https://img.shields.io/pypi/pyversions/sokoenginepy.svg
    :target: https://pypi.python.org/pypi/sokoenginepy
    :alt: Supported Python versions

.. image:: https://readthedocs.org/projects/sokoenginepy/badge/?version=latest
    :target: https://sokoenginepy.readthedocs.org/
    :alt: Documentation

.. image:: https://travis-ci.org/tadamic/sokoenginepy.svg?branch=development
    :target: https://travis-ci.org/tadamic/sokoenginepy
    :alt: TravisCI status

.. image:: https://api.codacy.com/project/badge/Coverage/492a7c08b97e4dbe991b0190dd3abf02
    :target: https://www.codacy.com/app/tomislav-adamic/sokoenginepy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tadamic/sokoenginepy&amp;utm_campaign=Badge_Coverage
    :alt: Tests coverage

.. image:: https://api.codacy.com/project/badge/Grade/492a7c08b97e4dbe991b0190dd3abf02
    :target: https://www.codacy.com/app/tomislav-adamic/sokoenginepy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tadamic/sokoenginepy&amp;utm_campaign=Badge_Grade
    :alt: Code quality

sokoenginepy is game engine for Sokoban and variants written in Python and
loaded with features:

- implements game logic for ``Sokoban``, ``Hexoban``, ``Trioban`` and ``Octoban`` variants
    - supports ``Sokoban+`` for all implemented variants
    - supports ``Multiban`` (muliple pushers on board) for all variants
- two game engines implementations
    - fast and memory lightweight with single step undo/redo
    - somewhat slower and larger with unlimited movement undo/redo
- reading and writing level collections
    - fully compatible with `SokobanYASC`_ .sok file format and variants (.xsb, .tsb, .hsb, .txt)

sokoenginepy was inspired by `SokobanYASC`_, `JSoko`_, `MazezaM`_

Installing
----------

Installing sokoenginepy should be as simple as

.. code-block:: sh

    pip install sokoenginepy


Using
-----

- For quick glance of features and usage check the `Tutorial`_.
- For in-depth docs of whole package see `API Reference`_.


.. _SokobanYASC: http://sourceforge.net/projects/sokobanyasc/
.. _JSoko: http://www.sokoban-online.de/
.. _MazezaM: http://webpages.dcu.ie/~tyrrelma/MazezaM/
.. _Sokobano: http://sokobano.de/en/index.php
.. _Sokoban for Windows: http://www.sourcecode.se/sokoban/
.. _Tutorial: https://sokoenginepy.readthedocs.io/en/development/tutorial.html
.. _API reference: https://sokoenginepy.readthedocs.io/en/development/api.html
