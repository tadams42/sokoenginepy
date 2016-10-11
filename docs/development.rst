Developing sokenginepy
======================


Prepare development environment
-------------------------------

sokoenginepy requires Python 3.3 or newer. It is encouraged to use vrtualenv.
To set it up, lets first create new virtual environment

.. code-block:: sh

    cd path/to/cloned/repo/sokoenginepy
    pyvenv .venv
    source .venv/bin/activate

Then ensure we have newest pip and setuptools

.. code-block:: sh

    pip install -U pip
    wget https://bootstrap.pypa.io/ez_setup.py -O - | python

To be able to package project into wheels, we need

.. code-block:: sh

    pip install wheel

And to distribute it on PyPI

.. code-block:: sh

    pip install twine


Install it in develop mode
--------------------------

.. code-block:: sh

    python setup.py develop

Later, to uninstall it

.. code-block:: sh

    python setup.py develop --uninstall

To install extra packages usefull in development

.. code-block:: sh

    pip install -e .[dev, test]


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

and finally, tests can be run with tox

.. code-block:: sh

    tox

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

    python setup.py sdist

An upload it

.. code-block:: sh

    twine upload -r pypitest dist/*
