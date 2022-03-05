# Install

## Install from PyPi

```sh
pip install sokoenginepy
```

## Python dev environment

```sh
cd path/to/cloned/repo/sokoenginepy
python3.9 -m venv .venv
source .venv/bin/activate
pip install -U pip wheel
pip install -e .[dev]
```

## Build Python packages

```sh
source .venv/bin/activate
python -m build
```

## C++ native extension

There is optional C++ native extension that is built automatically with `pip install`
if all dependencies are met and OS is **Linux**.

Native extension needs [Boost.Graph] and [pybind11]. [Boost.Graph] needs to be installed
on system, everything else is pulled automatically:

```sh
sudo apt install python3-dev libboost-graph-dev
```

and then we can compile native extension in dev environment:

```sh
export SOKOENGINEPYEXT_BUILD=True
# optionally, to compile without optimizations
export SOKOENGINEPYEXT_DEBUG=True
pip install -e .[dev]
```

Notes:

- `python setup.py develop` performs similar install but without additional
  development packages
- `python setup.py develop` will fail when trying to build native extension with
  message that it is missing `pybind11` headers. This is most probably `setuptools`
  [bug](https://github.com/pybind/python_example/issues/16)
- `pip install -e .` will always work and is equivalent to calling `python setup.py
  development` but with some `pip` magic that makes `setuptools` problem go away

C++ extension is used automatically (for example, running tests will actually use native
code and effectively test native extension instead of Python code).

To control process of building native extension, use following environment variables:

- `SOKOENGINEPYEXT_BUILD`
  - Default: True
  - if `true`, `pip install` will try to build native C++ code
  - note that even if `true` and native code build fails, `pip install` will silently
    fallback to installing package without native extension
  - to see if compilation actually succeeded run `pip install -v` which will display
    all compile commands and their output

- `SOKOENGINEPYEXT_DEBUG`
  - Default: False
  - Enables debug build of native code

No client's source code needs to be changed in any case. Only difference is that when
we have native code built, stuff runs faster. A lot faster. (this can be checked by
running `mover_benchmarks.py` with and without native extension built).

To debug native code, use `gdb` like this:

```sh
sudo apt install python3-dbg
pip install gdbgui --upgrade
rm -r build/
SOKOENGINEPYEXT_DEBUG=True pip install -e .
gdbgui 'python crash.py'
gdbgui '.venv/bin/python .venv/bin/py.test tests/crash_test.py'
```

In cases where developing against native extension is undesirable, use this:

```sh
rm -r build/
SOKOENGINEPYEXT_BUILD=False pip install -e .
```

profiling native extension from Python:

```sh
rm -r build/
SOKOENGINEPYEXT_DEBUG=True pip install -e .
valgrind --dump-line=yes --dump-instr=yes --tool=callgrind --collect-jumps=yes \
    --callgrind-out-file=mover_profiling.log python bin/mover_profiling.py
kcachegrind mover_profiling.log
```

## Running tests

```sh
py.test
```

or to get more verbose output

```sh
py.test --spec
```

## Running under PyPy3

```sh
wget https://bitbucket.org/pypy/pypy/downloads/pypy3-v5.8.0-linux64.tar.bz2
tar -xvjf pypy3-v5.8.0-linux64.tar.bz2
virtualenv -p pypy3-v5.8.0-linux64/bin/pypy3 .venvpypy
source .venvpypy/bin/activate
pip install -U pip wheel
```

## Profiling

Use IPython shell to generate profiling data

```python
%prun -D program.prof [mover.move(d) for d in moves_cycle]
```

After that, it is viewable by either Snakeviz

```sh
snakeviz program.prof
```

or as call graph through KCacheGrind

```sh
pyprof2calltree -i program.prof
kcachegrind program.prof.log
```

There is also a suite of `Mover` benchmarks:

```sh
python bin/mover_benchmarks.py
```

And useful `Mover` profiling script:

```sh
pip install pyprof2calltree
python bin/mover_profiling.py
pyprof2calltree -i moves_profile.prof
pyprof2calltree -i single_move_profile.prof
kcachegrind moves_profile.prof.log
kcachegrind single_move_profile.prof.log
```

[pybind11]: http://pybind11.readthedocs.io/en/stable/index.html
[NetworkX]: https://networkx.github.io/
[Boost.Graph]: https://www.boost.org/doc/libs/1_61_0/libs/graph/doc/index.html
