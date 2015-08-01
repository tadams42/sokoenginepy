import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))
version = {}


with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'sokoenginepy/version.py'), encoding='utf-8') as f:
    exec(f.read(), version)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


# Always installed
requirements = [
    'Unipath >=1.1',
    'pytz >=2015.4',
    'pyparsing >=2.0.3',
    # Alternative that is A LOT faster but ard fails install on Python 3.4
    # graph-tool
    'networkx >=1.9.1',
]

# $ pip install -e .[dev,test]
requirements_dev = [
    # IPython stuff
    'ipython >=3.2.0, <4',
    'pyzmq >=14.7.0',
    'Jinja2 >=2.7.3',
    'tornado >=4.2.1',
    'jsonschema >=2.5.1',
    'terminado >=0.5',
    'ipdb >=0.8.1',

    # Petty stacktrace
    'colored-traceback >=0.2.1',

    # Animation and graph debugging
    'scipy >=0.15.1',
    'moviepy >=0.2.2.11',
    'matplotlib >=1.4.3',

    # Docs and viewers
    'Sphinx >=1.3.1',
    'restview >=2.4.0',
    'grip >=3.3.0',

    # Profiler
    'snakeviz >=0.4.0',
]

# $ pip install -e .[dev,test]
# Also, automatically installed by setup.py test
requirements_test = [
    'pytest >=2.7.2',
    'pytest-spec >=0.2.24',
    'pytest-cov >=2.0.0',
    'factory-boy >=2.5.2',
    'fake-factory >=0.5.2',
    'PyHamcrest >=1.8.3',
    'pyexcel-ods3 >=0.0.8',
    'lxml >=3.4.4',
    'tox >=2.1.1',
]

# with open(path.join(here, 'requirements.txt'), encoding='utf-8', mode='w') as f:
#     for requirement in (requirements + requirements_dev + requirements_test):
#         f.write(requirement + "\n")

setup(

    name             = "sokoenginepy",
    description      = "Sokoban and variants game engine",
    version          = version['__version__'],
    author           = "Tomislav Adamic",
    author_email     = "tomislav.adamic@gmail.com",
    url              = "https://github.com/tadamic/sokoenginepy",
    license          = "GPLv3",
    keywords         = "game sokoban hexoban octoban trioban",
    # packagemds         = ['sokoenginepy'],
    packages         = find_packages(),
    install_requires = requirements,
    long_description = long_description,

    cmdclass         = {'test': PyTest},

    extras_require = {
        'dev': requirements_dev,
        'test': requirements_test,
    },
    tests_require = requirements_test,

    package_data = {
        'sokoenginepy': ['res/*'],
    },

    classifiers = [
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',

        "Development Status :: 2 - Pre-Alpha",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",

        "Operating System :: OS Independent",

        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ],
)
