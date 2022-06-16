<!-- omit in toc -->
# Install

- [1. Python package](#1-python-package)
  - [1.1. Running tests and benchmarks](#11-running-tests-and-benchmarks)
  - [1.2. Python native extension](#12-python-native-extension)
- [2. libsokoengine C++ library](#2-libsokoengine-c-library)
  - [2.1. Build and install from source](#21-build-and-install-from-source)
  - [2.2. Integrating into other CMake projects](#22-integrating-into-other-cmake-projects)
  - [2.3. Other make targets](#23-other-make-targets)

## 1. Python package

```sh
pip install sokoenginepy
```

### 1.1. Running tests and benchmarks

```sh
py.test
```

or to get more verbose output

```sh
py.test --spec
```

We can also run some built-in, rudimentary benchmarks:

```sh
python -m sokoenginepy
```

### 1.2. Python native extension

When installing from source, `pip` will try to build native C++ extension. If build
fails for whatever reason, `pip` will fallback to installing pure Python implementation.

This native extension needs:

```sh
sudo apt install python3-dev libboost-graph-dev
```

Following environment variables control building of this native extension:

- `SOKOENGINEPYEXT_BUILD` (default: `true`)
  - should native extension be built?
- `SOKOENGINEPYEXT_DEBUG` (default: `false`)
  - should we build non-optimized native extension?

If built, native extension is used automatically - Python code calling stuff from
`sokoenginepy` doesn't need to change at all.

In short, to ensure that `pip` will always try to build native extension in development
environment:

```sh
export SOKOFILEPYEXT_BUILD=1
export SOKOENGINEPYEXT_BUILD=1
pip install -e ".[dev]"
```

## 2. libsokoengine C++ library

```sh
sudo apt install git build-essential libboost-graph-dev cmake doxygen
```

### 2.1. Build and install from source

```sh
git clone https://github.com/tadams42/sokoenginepy.git
cmake --preset "debug"
cd build/debug
make && make install
```

uninstall:

```sh
xargs rm < install_manifest.txt
```

### 2.2. Integrating into other CMake projects

When `libsokoengine` is installed, it can be found by `cmake`'s `find_package`:

```cmake
find_package(libsokoengine 0.5.0 REQUIRED)
add_executable(sokoban_app main.cpp)
target_link_libraries(sokoban_app PUBLIC libsokoengine::sokoengine)
```

It is also possible to use `libsokoengine` directly from built sources. In this case,
`find_package` needs `PATHS` argument. Assuming we'd built `libsokoengine` in
`/home/foo/development/sokoenginepy/build/debug`, we can use it (without installing it)
in other project like this:

```cmake
set(DEV_PATH_HINT1 "../sokoenginepy/build/debug")
set(DEV_PATH_HINT2 "../sokoenginepy/build/release")
cmake_path(ABSOLUTE_PATH DEV_PATH_HINT1 BASE_DIRECTORY ${CMAKE_SOURCE_DIR})
cmake_path(ABSOLUTE_PATH DEV_PATH_HINT2 BASE_DIRECTORY ${CMAKE_SOURCE_DIR})
find_package(
    libsokoengine 0.5.0 REQUIRED
    CONFIG
    PATHS ${DEV_PATH_HINT1}
          ${DEV_PATH_HINT2}
)
```

### 2.3. Other make targets

- `benchmarks` - a suite of benchmarks for `Mover`

  ```sh
  make benchmarks
  ./benchmarks
  ```

- `valgrind_profile_playground` - a profiling data generator

  ```sh
  sudo apt install kcachegrind valgrind
  make valgrind_profile_playground
  kcachegrind playground_dump.pid
  ```

- Python extension

  It is possible to re-build Python extension via cmake (usually faster than going
  through `pip install`). This can be useful for development environments.

  ```sh
  cd build/debug
  make sokoenginepyext
  cd ../../src
  ln -sf ../build/debug/src/sokoenginepyext/sokoenginepyext.cpython-39-x86_64-linux-gnu.so
  ```
