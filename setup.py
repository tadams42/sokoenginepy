import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


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


setup(
    name = "bosp",
    description = "Bunch Of Sokoban Programs",
    version = "0.0.1",
    author = "Tomislav Adamic",
    author_email = "tomislav.adamic@gmail.com",
    url = "https://github.com/tadamic/bosp",
    license = "GPLv3",
    keywords = "game sokoban hexoban octoban trioban",

    packages = ['bosp'],
    # packages = find_packages(),

    install_requires = [
        'Unipath ==1.1',
        'pytz',
        'pyparsing ==2.0.3',
    ],

    tests_require = [
        'pytest >=2.7.2',
        'pytest-spec >=0.2.24',
        'factory-boy >=2.5.2',
        'fake-factory >=0.5.2',
        'PyHamcrest >=1.8.3',
        'colored-traceback >=0.2.1',
        'ipython >=3.2.0',
        'ipdb >=0.8.1',
    ],

    cmdclass = {'test': PyTest},

    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",

        "Development Status :: 2 - Pre-Alpha",

        "Environment :: X11 Applications :: KDE",

        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",

        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",

        "Operating System :: OS Independent",

        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ],

    long_description = """\

    Not so long for now...

"""
)
