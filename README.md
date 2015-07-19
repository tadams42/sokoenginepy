## Installing in development mode

Prepare (run only once):

~~~sh
# Create virtual environment
pyvenv ~/.virtualenvs3/bosp
# Activate it
source ~/.virtualenvs3/bosp/bin/activate
# Make sure we have newest pip
pip install -U pip
# Install setuptools
wget https://bootstrap.pypa.io/ez_setup.py -O - | python
# You’ll need this to package your project into wheels
# pip install wheel
# You’ll need this to upload your project distributions to PyPI
# pip install twine
# Install bosp in develop mode
python setup.py develop
~~~

~~~
python setup.py develop
python setup.py develop --uninstall
~~~

## Running tests

~~~sh
python setup.py test -a "tests"
# or
python setup.py test -a "--spec tests"
~~~
