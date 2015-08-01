Developing sokenginepy
======================


Prepare development environment
-------------------------------

sokoenginepy requires Python 3.3 or newer. It is encouraged to use vrtualenv.
To set it up, lets first create new virtual environment::

    cd path/to/cloned/repo/sokoenginepy
    pyvenv .venv
    source .venv/bin/activate

Then ensure we have newest pip and setuptools::

    pip install -U pip
    wget https://bootstrap.pypa.io/ez_setup.py -O - | python

To be able to package project into wheels, we need::

    pip install wheel

And to distribute it on PyPI::

    pip install twine


Install it in develop mode
--------------------------

::

    python setup.py develop

Later, to uninstall it::

    python setup.py develop --uninstall


Running tests
-------------

::

    python setup.py test -a "tests"

or to get more verbose output::

    python setup.py test -a "--spec tests"

or to generate tests coverage::

    py.test --cov=sokoengine --cov-report=html tests/

and finally, tests can be run with tox::

    tox
