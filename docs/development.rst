Development
===========

Preparing development environment
---------------------------------

Create new virtual environment

.. code-block:: sh

    cd path/to/cloned/repo/sokoenginepy
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -u pip wheel

Installing in develop mode
--------------------------

.. code-block:: sh

    python setup.py develop

Later, to uninstall it

.. code-block:: sh

    python setup.py develop --uninstall

To install extra packages useful in development

.. code-block:: sh

    pip install -e .[dev]

Running tests
-------------

.. code-block:: sh

    py.test

or to get more verbose output

.. code-block:: sh

    py.test -p no:sugar --spec

or to generate tests coverage

.. code-block:: sh

    py.test --cov=sokoenginepy --cov-report=html

and finally, tests can be run with tox_

.. code-block:: sh

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox

Running under PyPy3
-------------------

.. code-block:: sh

    wget https://bitbucket.org/pypy/pypy/downloads/pypy3-v5.8.0-linux64.tar.bz2
    tar -xvjf pypy3-v5.8.0-linux64.tar.bz2
    virtualenv -p pypy3-v5.8.0-linux64/bin/pypy3 .venvpypy
    source .venvpypy/bin/activate
    pip install -U pip wheel

Profiling
---------

Use IPython shell to generate profiling data

.. code-block:: python

    %prun -D program.prof [mover.move(d) for d in moves_cycle]

After that, it is viewable by either Snakeviz

.. code-block:: sh

    snakeviz program.prof

or as call graph through KCacheGrind

.. code-block:: sh

    pyprof2calltree -i program.prof
    kcachegrind program.prof.log

Uploading to PyPI
-----------------

.. code-block:: sh

    pip install -U twine

Prepare ``~/.pypirc``

.. code-block:: ini

    [distutils]
    index-servers=
        pypi
        pypitest

    [pypitest]
    repository = https://test.pypi.org/legacy/
    username = <username>
    password = <password>

    [pypi]
    username = <username>
    password = <password>

Create dist

.. code-block:: sh

    python setup.py sdist bdist_wheel

An upload it

.. code-block:: sh

    twine upload -r pypitest dist/*

Native extenstion
-----------------

There is optional C++ native extension that is built with ``python setup.py`` automatically if all dependencies are in place.

Configuring dependencies needs more work, currently it is guaranteed to work on only on Ubuntu and only on Python 3.5.

Native extnsion relies on Boost.Python and Boost.Graph:

.. code-block:: sh

    sudo apt install python3-dev python3-dbg libboost-python-dev libboost-graph-dev

.. _Boost Graph Library: http://www.boost.org/doc/libs/1_61_0/libs/graph/doc/index.html
.. _graph-tool: https://graph-tool.skewed.de/download
.. _PyPI: https://pypi.python.org/pypi
.. _tox: https://tox.readthedocs.io/en/latest/
.. _NetworkX: https://networkx.github.io/
