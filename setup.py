"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import sys
# To use a consistent encoding
from codecs import open
from os import path

# Always prefer setuptools over distutils
from setuptools import find_packages, setup

HERE = path.abspath(path.dirname(__file__))
VERSION = {}
NEEDS_PYTEST = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
PYTEST_RUNNER = ['pytest-runner'] if NEEDS_PYTEST else []

# Get the long description from the README file
with open(path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

with open(path.join(HERE, 'sokoenginepy/version.py'), encoding='utf-8') as f:
    exec(f.read(), VERSION)

SETUP_REQUIREMENTS = [
    # ... (other setup requirements)
] + PYTEST_RUNNER

INSTALL_REQUIREMENTS = [
    'pytz >=2016.6.1',
    'pyparsing >=2.1.0',
    'networkx >=1.11',
    # Alternative that is A LOT faster but install through pip is not supported
    # 'graph-tool >=2.11'
    'cached-property >=1.2.0'
]

DEV_REQUIREMENTS = [
    'pycodestyle >= 2.0.0',  # (formerly called pep8)
    'mccabe >= 0.5.0',
    'pylint >= 1.6.0',
    'yapf >= 0.11.0',
    # 'flake8 >= 3.0.0',
    # 'pep257 >= 0.7.0',
    # 'pylama >= 7.1.0',
    # 'pylama-pylint >= 2.2.1',

    # IPython stuff
    'ipython >= 5.0.0',
    'jupyter >= 1.0.0',
    'ipdb >= 0.10.0',

    # Docs and viewers
    'Sphinx >= 1.4.0',
    'sphinx_rtd_theme >= 0.1.9',
    'restview >= 2.6.0',
    'grip >= 4.3.0',

    # Profiling
    'snakeviz >= 0.4.0',
    'pyprof2calltree >= 1.4.0',

    # py.test things usefull only when manually running tests
    'pytest-colordots >= 0.1.0',
    'colored-traceback >= 0.2.0',
]

TEST_REQUIREMENTS = [
    'pytest >= 3.0.0',
    'pytest-spec >= 1.0.0',
    'pytest-cov >= 2.3.0',
    'pytest-benchmark >= 3.0.0',
    'check-manifest >= 0.33.0',
    'factory-boy >= 2.8.0',
    'faker >= 0.6.0',
    'coverage >= 4.2.0',
]

setup(
    name="sokoenginepy",
    author="Tomislav Adamic",
    author_email="tomislav.adamic@gmail.com",
    url="https://github.com/tadamic/sokoenginepy",
    license="GPLv3",
    keywords="game sokoban hexoban octoban trioban",

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the VERSION across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=VERSION['__version__'],
    description="Sokoban and variants game engine",
    long_description=LONG_DESCRIPTION,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ],

    # You can just specify the packages manually HERE if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['docs', 'tests', 'scripts']),
    setup_requires=SETUP_REQUIREMENTS,

    # List run-time dependencies HERE.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=INSTALL_REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,

    # List additional groups of dependencies HERE (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': list(set(DEV_REQUIREMENTS).union(set(TEST_REQUIREMENTS))),
        'test': TEST_REQUIREMENTS
    },

    # If there are data files included in your packages that need to be
    # installed, specify them HERE.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={'sokoenginepy': ['res/*'],},
)
