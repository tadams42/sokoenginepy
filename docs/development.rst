Development
===========

Preparing development environment
---------------------------------

Create new virtual environment

.. code-block:: sh

    cd path/to/cloned/repo/sokoenginepy
    pyvenv .venv
    source .venv/bin/activate
    pip install -u pip wheel

Installing in develop mode
--------------------------

.. code-block:: sh

    python setup.py develop

Later, to uninstall it

.. code-block:: sh

    python setup.py develop --uninstall

To install extra packages usefull in development

.. code-block:: sh

    pip install -e .[dev]

Running tests
-------------

.. code-block:: sh

    python setup.py test -a "tests"

or to get more verbose output

.. code-block:: sh

    python setup.py test -a "--spec tests"

or to generate tests coverage

.. code-block:: sh

    py.test --cov=sokoenginepy --cov-report=html tests/

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

Installing graph-tool_ to virtual environment on Ubuntu
-------------------------------------------------------

graph-tool_ is `Boost Graph Library`_ based graph package. Since it is not
instalable via pip, it is left as optional dependency: if sokoenginepy detects
it, it will use it instead of default NetworkX_. To install graph-tool_ do the
following:

.. code-block:: sh

    pyvenv .venvgt
    source .venvgt/bin/activate

    sudo apt-get install libcairomm-1.0-dev libgtk-3-dev libcairo2-dev \
        libjpeg-dev libgif-dev

    git clone git://git.cairographics.org/git/pycairo
    cd pycairo
    python setup.py install

    sudo apt-get install libsparsehash-dev libcgal-dev libboost-python-dev  \
        libboost-iostreams-dev libboost-coroutine-dev libboost-graph-dev \
        libexpat1-dev
    pip install scipy numpy matplotlib

    cd graph-tool-2.19
    export CXXFLAGS="-I${VIRTUAL_ENV}/include"
    export LIBDIR="-I${VIRTUAL_ENV}/lib"
    export CAIROMM_CFLAGS="-std=c++14 -I/usr/include/cairomm-1.0 -I/usr/lib/x86_64-linux-gnu/cairomm-1.0/include -I/usr/include/cairo -I/usr/include/glib-2.0 -I/usr/lib/x86_64-linux-gnu/glib-2.0/include -I/usr/include/pixman-1 -I/usr/include/freetype2 -I/usr/include/libpng12 -I/usr/include/sigc++-2.0 -I/usr/lib/x86_64-linux-gnu/sigc++-2.0/include"
    ./configure
    make
    sudo make install

Runing under PyPy3
------------------

.. code-block:: sh

    wget https://bitbucket.org/pypy/pypy/downloads/pypy3.3-v5.5.0-alpha-linux64.tar.bz2
    tar xvfj pypy3.3-v5.5.0-alpha-linux64.tar.bz2
    virtualenv -p /foo/bar/baz/pypy3-v5.5.0-linux64/bin/pypy3pypy3 .venvpypy
    source .venvpypy/bin/python

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
    repository = https://testpypi.python.org/pypi
    username = <username>
    password = <password>

    [pypi]
    repository = https://pypi.python.org/pypi
    username = <username>
    password = <password>

Create dist

.. code-block:: sh

    python setup.py sdist bdist_wheel

An upload it

.. code-block:: sh

    twine upload -r pypitest dist/*

.. _Boost Graph Library: http://www.boost.org/doc/libs/1_61_0/libs/graph/doc/index.html
.. _graph-tool: https://graph-tool.skewed.de/download
.. _PyPI: https://pypi.python.org/pypi
.. _tox: https://tox.readthedocs.io/en/latest/
.. _NetworkX: https://networkx.github.io/
