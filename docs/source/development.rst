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

    py.test --cov=sokoenginepy --cov-report=html tests/

and finally, tests can be run with tox::

    tox

Uploading to PyPI
-----------------

::
    pip install -U twine

Prepare ``~/.pypirc``::

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

Create dist::

    python setup.py sdist

An upload it::

    twine upload -r pypitest dist/*
