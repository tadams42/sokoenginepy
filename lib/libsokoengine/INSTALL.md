# Install

## Runtime dependencies

~~~~~~sh
$ sudo apt install libboost-graph
~~~~~~

## Compile time dependencies

[git], [make], recent C++ compiler with C++11 support, [boost] and [CMake]

~~~~~~sh
$ sudo apt install git build-essential libboost-graph-dev cmake libdw-dev \
                   binutils-dev doxygen
~~~~~~

There are also few dependencies that [CMake] pulls automatically from GutHub
during build:

- [cppitertools]
- [backward-cpp]
- [pybind11]

## Compile and install

Clone repo:

~~~~~~sh
$ git clone https://github.com/tadams42/sokoenginepy.git
~~~~~~

Configure sources:

~~~~~~sh
$ cd lib/libsokoengine && mkdir build && cd build
$ cmake ../
~~~~~~

Build and install:

~~~~~~sh
$ make && make install
~~~~~~

## Customizing build

[CMake] accepts compile options in the form of:

~~~~~~sh
$ cmake -DOPTION_NAME=OPTION_VALUE
~~~~~~

For `libsokoengine`, these are probably most usable ones:

  - `CMAKE_INSTALL_PREFIX`
    + string, default: `/usr/local`
    + allowed values: platform dependent

  - `CMAKE_BUILD_TYPE`
    + string, default: `Release`
    + allowed values: [`RelWithDebInfo`, `Debug`, `Release`, `MinSizeRel`]

Example:

~~~sh
$ cmake -DCMAKE_INSTALL_PREFIX="/tmp" -DCMAKE_BUILD_TYPE="Debug"
~~~

## Integrating with other projects through [CMake]

`liboskoengine` installs everything needed to be used in [CMake] projects including [CMake Config-Package]. Minimal project for [CMake] would look like this:

```cmake
cmake_minimum_required (VERSION 2.8.12)
project(test_libsokoengine)

find_package(sokoengine 0.4 REQUIRED)
add_executable(tester main.cpp)
target_link_libraries( tester sokoengine )
```

## Python bindings

All `libsokoengine` classes are exposed to Python using [pybind11]. To compile
Python bindings:

~~~sh
$ make sokoenginepyext
~~~

Which will produce shred library importable in Python:

~~~python
import sokoenginepyext
~~~

## Tests

All tests are written in Python. This requires creation of Python
environment and [sokoenginepy] (which will also build `sokoenginepyext`)

After that, tests can be run with Python test runner.

For details see: http://sokoenginepy.readthedocs.io/en/latest/development.html

## Other [make] targets

- `benchmarks` - a suite of benchmarks for `Mover`

~~~sh
$ make benchmarks
$ ./bin/benchmarks/benchmarks
~~~

- `valgrind_profile_playground` - a profiling data generator

~~~sh
$ sudo apt install kcachegrind valgrind
$ make valgrind_profile_playground
$ kcachegrind playground_dump.pid
~~~

[C++ symbols wrapup]:http://www.eyrie.org/~eagle/journal/2012-02/001.html
[git]:http://git-scm.com/
[gcc]:http://gcc.gnu.org/
[clang]:http://clang.llvm.org/
[CMake]:http://www.cmake.org
[boost]:http://www.boost.org/
[make]:http://www.gnu.org/software/make/
[Doxygen]:http://www.doxygen.org/
[Graphviz]:http://www.graphviz.org
[CMake Config-Package]:https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html#using-packages
[pybind11]:http://pybind11.readthedocs.io/en/stable/index.html
[cppitertools]:https://github.com/ryanhaining/cppitertools
[backward-cpp]:https://github.com/bombela/backward-cpp
[sokoenginepy]:https://github.com/tadams42/sokoenginepy
