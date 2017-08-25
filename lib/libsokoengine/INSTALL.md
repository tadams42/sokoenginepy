# Install

## Prerequisites

Required: [git], [make], recent C++ compiler with C++11 support ([gcc] v4.7, [clang] v3.0), [boost], [CMake]

~~~~~~sh
$ sudo apt-get install git build-essential libboost-graph-dev cmake
~~~~~~

Useful for development:

~~~~~~sh
$ sudo apt-get install lcov libdw-dev binutils-dev doxygen valgrind \
kcachegrind gcov lcov genhtml ninja-build cmake-qt-gui
~~~~~~

## Compile and install

Clone repo:

~~~~~~sh
$ git clone https://github.com/tadams42/sokoenginepy.git
~~~~~~

Configure sources:

~~~~~~sh
$ cd libsokoengine && mkdir build && cd build
$ cmake ../
~~~~~~

Build and install:

~~~~~~sh
$ make && make install
~~~~~~

## Customizing source

[CMake] accepts compile options in the form of:

~~~~~~sh
$ cmake -DOPTION_NAME=OPTION_VALUE
~~~~~~

For sokoengine, these are probably most usable options:

  - `CMAKE_INSTALL_PREFIX`
    + string, default: `/usr/local`
    + allowed values: platform dependent

  - `CMAKE_BUILD_TYPE`
    + string, default: `Release`
    + allowed values: [`RelWithDebInfo`, `Debug`, `Release`, `MinSizeRel`]

Example:

~~~
cmake -DCMAKE_INSTALL_PREFIX="/tmp" -DCMAKE_BUILD_TYPE="Debug"
~~~

### Integrating with [CMake]

`liboskoengine` installs everything needed to be used in [CMake] projects including [CMake Config-Package](http://www.cmake.org/cmake/help/git-master/manual/cmake-packages.7.html#using-packages). Minimal project for [CMake] would look like this:

```cmake
cmake_minimum_required (VERSION 2.8.12)
project(test_libsokoengine)

find_package(sokoengine 0.4 REQUIRED)
add_executable(tester main.cpp)
target_link_libraries( tester sokoengine )
```

[C++ symbols wrapup]:http://www.eyrie.org/~eagle/journal/2012-02/001.html
[git]:http://git-scm.com/
[gcc]:http://gcc.gnu.org/
[clang]:http://clang.llvm.org/
[CMake]:http://www.cmake.org
[boost]:http://www.boost.org/
[make]:http://www.gnu.org/software/make/
[Doxygen]:http://www.doxygen.org/
[Graphviz]:http://www.graphviz.org
