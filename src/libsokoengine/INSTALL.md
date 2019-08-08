# Install

## Runtime dependencies

~~~sh
sudo apt install libboost-graph
~~~

## Compile time dependencies

[git], [make], recent C++ compiler with C++14 support, [boost] and [CMake]

~~~sh
sudo apt install git build-essential libboost-graph-dev cmake libdw-dev \
                 binutils-dev doxygen
~~~

There are also few dependencies that [CMake] pulls automatically from GutHub during build:

- [cppitertools]
- [backward-cpp]
- [pybind11]

## Compile and install

Clone the repo:

~~~sh
git clone https://github.com/tadams42/sokoenginepy.git
~~~

Configure sources:

~~~sh
cd lib/libsokoengine && mkdir build && cd build
cmake ../
~~~

Build and install:

~~~sh
make && make install
~~~

To later uninstall you can:

~~~sh
xargs rm < install_manifest.txt
~~~

## Customizing build

[CMake] accepts compile options in the form of:

~~~sh
cmake -DOPTION_NAME=OPTION_VALUE
~~~

For `libsokoengine`, these are probably most usable ones:

- `CMAKE_INSTALL_PREFIX`
  - string, default: `/usr/local`
  - allowed values: platform dependent

- `CMAKE_BUILD_TYPE`
  - string, default: `Release`
  - allowed values: [`RelWithDebInfo`, `Debug`, `Release`, `MinSizeRel`]

- `BUILD_SHARED_LIBS`
  - boolean
  - should we build shared library?

Example:

~~~sh
cmake -DCMAKE_INSTALL_PREFIX="/tmp" \
      -DCMAKE_BUILD_TYPE="RelWithDebInfo" \
      -DCMAKE_CXX_COMPILER="clang++" \
      -G Ninja \
      -S ../../src/libsokoengine/ \
      -B ./
~~~

## Integrating with other projects through [CMake]

`libsokoengine` installs everything needed to be used in [CMake] projects including [CMake Config-Package]. Minimal project for [CMake] would look like this:

~~~cmake
cmake_minimum_required (VERSION 3.15.1)

project(test_installed_sokoengine VERSION 0.5.3 LANGUAGES CXX)

find_package(libsokoengine 0.5.0 REQUIRED)

add_executable(playground playground.cpp)
target_link_libraries(playground PUBLIC libsokoengine::sokoengine)
~~~

## Python bindings

All `libsokoengine` classes are exposed to Python using [pybind11]. To compile
Python bindings:

~~~sh
make sokoenginepyext
~~~

Which will produce shred library importable in Python:

~~~python
import sokoenginepyext
~~~

## Tests

All tests are written in Python.

To run tests, install [sokoenginepy] (which will also build `sokoenginepyext`)
and run Python test suite.

For details see [sokoenginepy docs].

## Other [make] targets

- `benchmarks` - a suite of benchmarks for `Mover`

~~~sh
make benchmarks
./src/utilities/benchmarks
~~~

- `valgrind_profile_playground` - a profiling data generator

~~~sh
sudo apt install kcachegrind valgrind
make valgrind_profile_playground
kcachegrind playground_dump.pid
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
[sokoenginepy docs]:http://sokoenginepy.readthedocs.io/en/latest/
