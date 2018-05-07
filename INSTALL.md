# Install

Installing sokoenginepy should be as simple as

~~~sh
pip install sokoenginepy
~~~

There is optional C++ native extension that is built automatically with `pip install` if all dependencies are met and OS is Linux. It relies on [Boost.Graph] and [pybind11]. [Boost.Graph] needs to be installed on system, everything else is pulled automatically:

~~~sh
sudo apt install python3-dev libboost-graph-dev
~~~

Following are all the glory details of individual build and install steps, running tests, debugging, profiling, etc...

## Preparing development environment

Create new virtual environment

~~~sh
cd path/to/cloned/repo/sokoenginepy
python3 -m venv .venv
source .venv/bin/activate
pip install -u pip wheel
~~~

## Installing in develop mode

~~~sh
pip install -e .[dev]
~~~

Notes:

- `python setup.py develop` performs similar install but without additional development packages
- `python setup.py develop` will fail when trying to build native extension with message that it is missing `pybind11` headers. This is most probably `setuptools` bug (see also https://github.com/pybind/python_example/issues/16)
- `pip install -e .` will always work and is equivalent to calling `python setup.py development` but with some `pip` magic that makes `setuptools` problem go away

## Running tests

~~~sh
py.test
~~~

or to get more verbose output

~~~sh
py.test -p no:sugar --spec
~~~

or to generate tests coverage

~~~sh
py.test --cov=sokoenginepy --cov-report=html
~~~

and finally, tests can be run with `tox`

~~~sh
tox
~~~

## Running under PyPy3

~~~sh
wget https://bitbucket.org/pypy/pypy/downloads/pypy3-v5.8.0-linux64.tar.bz2
tar -xvjf pypy3-v5.8.0-linux64.tar.bz2
virtualenv -p pypy3-v5.8.0-linux64/bin/pypy3 .venvpypy
source .venvpypy/bin/activate
pip install -U pip wheel
~~~

## Profiling

Use IPython shell to generate profiling data

~~~python
%prun -D program.prof [mover.move(d) for d in moves_cycle]
~~~

After that, it is viewable by either Snakeviz

~~~sh
snakeviz program.prof
~~~

or as call graph through KCacheGrind

~~~sh
pyprof2calltree -i program.prof
kcachegrind program.prof.log
~~~

There is also a suite of `Mover` benchmarks:

~~~sh
python bin/mover_benchmarks.py
~~~

And useful `Mover` profiling script:

~~~sh
python bin/mover_benchmarks.py
pip install pyprof2calltree
python bin/mover_profiling.py
pyprof2calltree -i moves_profile.prof
pyprof2calltree -i single_move_profile.prof
kcachegrind moves_profile.prof.log
kcachegrind single_move_profile.prof.log
~~~

## Uploading to PyPI

~~~sh
pip install -U twine
~~~

Prepare `~/.pypirc`

~~~ini
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
~~~

Create dist

~~~sh
python setup.py sdist bdist_wheel
~~~

An upload it

~~~sh
twine upload -r pypitest dist/*
~~~

## Native extension

If all dependencies are met and we are on Linux, `pip install sokoenginepy` will produce native C++ extension that is then used automatically (for example, running tests will actually use native code and effectively test native extension instead of Python code).

In cases where native extension can't be built, `pip install` will fall back to installing only Python code. Currently this means that on both, MacOS and Windows no native code will be built.

No client's source code needs to be changed in any case. Only difference is that when we have native code built, stuff runs faster. A lot faster. (this can be checked by running `mover_benchmarks.py` with and without native extension built).

~~~sh
$ sudo apt install git build-essential libboost-graph-dev cmake libdw-dev
binutils-dev doxygen
~~~

To debug native code, use `gdb` like this:

~~~sh
sudo apt install python3-dbg
pip install gdbgui --upgrade
rm -r build/
SOKOENGINEPYEXT_DEBUG=True pip install -e .
gdbgui 'python crash.py'
gdbgui '.venv/bin/python .venv/bin/py.test tests/crash_test.py'
~~~

In cases where developing against native extension is undesirable, use this:

~~~sh
rm -r build/
SOKOENGINEPYEXT_BUILD=False pip install -e .
~~~

profiling native extension from Python:

~~~sh
rm -r build/
SOKOENGINEPYEXT_DEBUG=True pip install -e .
valgrind --dump-line=yes --dump-instr=yes --tool=callgrind --collect-jumps=yes --callgrind-out-file=mover_profiling.log python bin/mover_profiling.py
kcachegrind mover_profiling.log
~~~

Since native extension is itself a C++ library (`libsokoengine`), it can be used as a part of separate, independent C++ projects. The only downside of this is that there are no native tests for the library - whole test suite is written in Python only. Beside that, everything works and is nicely integrated using [CMake]. For details see [libsokoengine docs].

[PyPI]: https://pypi.python.org/pypi
[tox]: https://tox.readthedocs.io/en/latest/
[pybind11]: http://pybind11.readthedocs.io/en/stable/index.html
[NetworkX]: https://networkx.github.io/
[Boost.Graph]: https://www.boost.org/doc/libs/1_61_0/libs/graph/doc/index.html
[cppitertools]: https://github.com/ryanhaining/cppitertools
[backward-cpp]: https://github.com/bombela/backward-cpp
[sokoenginepy]: https://github.com/tadams42/sokoenginepy
[libsokoengine docs]: http://tadams42.github.io/sokoenginepy/
[CMake]: https://cmake.org/
