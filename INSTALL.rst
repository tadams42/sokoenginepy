Install
=======

Installing sokoenginepy should be as simple as

.. code-block:: sh

    pip install sokoenginepy

There is optional C++ native extension that is built automatically with ``pip
install`` if all dependencies are met. It relies on `Boost.Graph`_ and `pybind11`_. `Boost.Graph`_ needs to be installed on system, everything else is pulled automatically:

.. code-block:: sh

    sudo apt install python3-dev libboost-graph-dev

Following are all the glory details of individual build and install steps, running tests, debugging, profiling, etc...

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

There is also a suite of ``Mover`` benchmarks:

.. code-block:: sh

    python bin/mover_benchmarks.py

And useful ``Mover`` profiling script:

.. code-block:: sh

    python bin/mover_benchmarks.py
    pip install pyprof2calltree
    python bin/mover_profiling.py
    pyprof2calltree -i moves_profile.prof
    pyprof2calltree -i single_move_profile.prof
    kcachegrind moves_profile.prof.log
    kcachegrind single_move_profile.prof.log

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

Native extension
----------------

If all dependencies are met, ``python setup.py develop`` and ``pip install sokoenginepy`` will produce native C++ extension that is then used automatically (for example, running tests will actually use native code and effectively test native extension instead of Python code)

.. code-block:: sh

    $ sudo apt install git build-essential libboost-graph-dev cmake libdw-dev
    binutils-dev doxygen

To debug native code, use ``gdb`` like this:

.. code-block:: sh

    sudo apt install python3-dbg
    pip install gdbgui --upgrade
    rm -r build/
    SOKOENGINEPYEXT_DEBUG=True python setup.py develop
    gdbgui 'python crash.py'
    gdbgui '.venv/bin/python .venv/bin/py.test tests/crash_test.py'

In cases where developing against native extension is undesirable, use this:

.. code-block:: sh

    rm -r build/
    SOKOENGINEPYEXT_BUILD=False python setup.py develop

profiling native extension from Python:

.. code-block:: sh

    rm -r build/
    SOKOENGINEPYEXT_DEBUG=True python setup.py develop
    valgrind --dump-line=yes --dump-instr=yes --tool=callgrind --collect-jumps=yes --callgrind-out-file=mover_profiling.log python bin/mover_profiling.py
    kcachegrind mover_profiling.log

Since native extension is itself a C++ library (``libsokoengine``), it can be used as a part of separate, independent C++ projects. The only downside of this is that there are no native tests for the library - whole test suite is written in Python only. Beside that, everything works and is nicely integrated using `CMake`_. For details see `libsokoengine docs`_.

.. _PyPI: https://pypi.python.org/pypi
.. _tox: https://tox.readthedocs.io/en/latest/
.. _pybind11: http://pybind11.readthedocs.io/en/stable/index.html
.. _NetworkX: https://networkx.github.io/
.. _Boost.Graph: http://www.boost.org/doc/libs/1_61_0/libs/graph/doc/index.html
.. _cppitertools: https://github.com/ryanhaining/cppitertools
.. _backward-cpp: https://github.com/bombela/backward-cpp
.. _sokoenginepy: https://github.com/tadams42/sokoenginepy
.. _libsokoengine docs: http://tadams42.github.io/sokoenginepy/
.. _CMake: https://cmake.org/
