.. sokoenginepy documentation master file, created by
   sphinx-quickstart on Fri Jul 24 19:41:54 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

sokoenginepy - Sokoban and variants game engine
===============================================

|version|

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


Install
-------

Installing sokoenginepy should be as simple as::

    pip install sokoenginepy

Note that sokoenginepy requires Python 3.3 or newer.


User's Guide
------------

.. toctree::
   :maxdepth: 2

   tutorial


API Reference
-------------

.. toctree::
   :maxdepth: 2

   api


Additional notes
----------------

Design notes and legal information are here for the interested.

.. toctree::
   :maxdepth: 2

   license
   development


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _SokobanYASC: http://sourceforge.net/projects/sokobanyasc/
.. _JSoko: http://www.sokoban-online.de/
.. _MazezaM: http://webpages.dcu.ie/~tyrrelma/MazezaM/
.. _Sokobano: http://sokobano.de/en/index.php
.. _Sokoban for Windows: http://www.sourcecode.se/sokoban/
