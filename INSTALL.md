# Install

## Python package - sokoenginepy

### Install from PyPi

```sh
pip install sokoenginepy
```

### Install from source

```sh
python3.9 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Running tests:

```sh
py.test
py.test --spec
```

Built-in, rudimentary benchmarks:

```sh
python -m sokoenginepy
```

Local copy of documentation:

```sh
cd docs/
make html
```

## C++ library - libsokoengine

### Build from source

1. Install C++ compiler, `cmake` and `doxygen` (YMMV may vary, depending on your OS):

   ```sh
   sudo apt install git build-essential cmake doxygen graphviz
   ```

2. Install [vcpkg](https://vcpkg.io/) and then:

   ```sh
   export CMAKE_TOOLCHAIN_FILE=[vcpkg root]/scripts/buildsystems/vcpkg.cmake
   ```

3. Get `libsokoengine` sources

   ```sh
   git clone https://github.com/tadams42/sokoenginepy.git
   ```

4. Configure C++ sources

   ```sh
   cd sokoenginepy/
   cmake --preset "debug"
   ```

5. Build the library

   ```sh
   cd build/debug
   make
   ```

### Install from source

```sh
cd build/debug
make install
```

To later uninstall:

```sh
xargs rm < install_manifest.txt
```

### Integrating into other CMake projects

`libsokoengine` is fully `cmake` enabled - it exports `cmake` targets that can be used
by other `cmake` projects:

```cmake
find_package(libsokoengine 1.0.0 REQUIRED)
add_executable(sokoban_app main.cpp)
target_link_libraries(sokoban_app PUBLIC libsokoengine::sokoengine)
```

It is also possible to integrate `libsokoengine` that was built (locally) but not
installed. Assuming we have following dir structure:

```sh
$ tree projects/
projects
├── myapp
│   └── CMakeLists.txt
└── sokoenginepy
    └── CMakeLists.txt
```

We first build `libsokoengine` in `projects/sokoenginepy/` as described in previous
sections. After that, we can use that built library directly from `projects/myapp`
(without running `make install` in `projects/sokoenginepy/`).

To do that add following in `myapp/CMakeLists.txt`:

```cmake
set(DEV_PATH_HINT1 "../sokoenginepy/build/debug")
set(DEV_PATH_HINT2 "../sokoenginepy/build/release")
cmake_path(ABSOLUTE_PATH DEV_PATH_HINT1 BASE_DIRECTORY ${CMAKE_SOURCE_DIR})
cmake_path(ABSOLUTE_PATH DEV_PATH_HINT2 BASE_DIRECTORY ${CMAKE_SOURCE_DIR})
find_package(
  libsokoengine 1.0.0 REQUIRED
  CONFIG
  PATHS ${DEV_PATH_HINT1}
        ${DEV_PATH_HINT2}
)
```

The `PATHS` argument to `find_package` serves as a list of hints on where to find
requested package.

### Other make targets

- `docs` - Doxygen documentation

  ```sh
  cd build/debug
  make docs
  ls docs/libsokoengine-v1.0.1/html/index.html
  ```

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

## Python C++ extension

### Build using pip

When installing `sokoenginepy` from source, `pip` will try to build native C++
extension. If build fails for whatever reason, `pip` will fallback to installing pure
Python implementation.

If C++ extension is installed, it is utilized automatically: Python code importing and
using `sokoenginepy` package doesn't need to change in any way.

It is possible to circumvent this automatic build via 2 environment variables:

- `SOKOENGINEPYEXT_SKIP`  - if set to true-ish value, C++ extension is not built
- `SOKOENGINEPYEXT_DEBUG` - if set to true-ish value, C++ extension compilation produces
  non optimized binary

Prerequisites for `pip` build of C++ extension:

- OS is Linux
- C++ library build via `cmake` must've succeed (meaning C++ compiler and `vcpkg` are
correctly set up)

When all requirements are met, you can build C++ extension:

```sh
sudo apt install python3-dev
python3.9 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

To verify, following file should've been created:

```sh
src/sokoenginepyext.cpython-XX-YYY_ZZZ-linux-gnu.so
```

### Build using cmake

When building through `pip`, most of the time whole source tree will be recompiled. This
is slow and inconvenient for development environments. We can use `cmake` instead. We
still need Python virtual environment though:

```sh
python3.9 -m venv .venv
source .venv/bin/activate
pip install pybind11
```

and then build C++ extension using cmake

```sh
cd build/debug
make sokoenginepyext
cd ../../src
ln -sf ../build/debug/src/sokoenginepyext/sokoenginepyext.cpython-39-x86_64-linux-gnu.so
cd ..
```

After this, we can re-build using just `cmake` giving us full control:

```sh
cd build/debug
make sokoenginepyext
```

Notice that we don't use `vcpkg` for `pybind11` and `Python3` headers. This is
intentional.

C++ extension should be build in requested Python virtual environment. If `python` was
managed via `vcpkg`, then Python version would've been pinned to whatever `vcpkg`
defines making it impossible to build ie. Python wheels for different Python versions
from the same source tree.

## Building on windows

1. Install:

   - Visual Studio Community edition for C++ or Microsoft C++ build toolchain
   - cmake
   - Python 3
   - git

2. open `x64 Native Tools Command Prompt`

3. setup `vcpkg`

   ```sh
   cd  C:\Users\vagrant\dev
   git clone https://github.com/Microsoft/vcpkg.git
   cd vcpkg
   bootstrap-vcpkg.bat
   vcpkg integrate install
   set CMAKE_TOOLCHAIN_FILE=C:/Users/vagrant/dev/vcpkg/scripts/buildsystems/vcpkg.cmake
   ```

4. get `sokoenginepy`

   ```sh
   cd  C:\Users\vagrant\dev
   git clone https://github.com/tadams42/sokoenginepy.git
   cd sokoenginepy
   ```

After that, choose one of following build scenarios:

1. PyPA build...

   ```sh
   set SOKOENGINEPYEXT_SKIP=0
   set SOKOENGINEPYEXT_DEBUG=1
   python -m venv .venv
   .venv\Scripts\activate.bat
   python -m pip install --upgrade pip
   pip install -U wheel build
   python -m build
   ```

2. ...or pip build editable

   ```sh
   set SOKOENGINEPYEXT_SKIP=0
   set SOKOENGINEPYEXT_DEBUG=1
   python -m venv .venv
   .venv\Scripts\activate.bat
   python -m pip install --upgrade pip
   pip install -U wheel

   # This is curious one - pip is unable to find globally installed cmake; reason unknown
   # We need to install cmake directly into Python environment
   pip install cmake

   # and finally
   pip install -e .[dev]
   ```

3. ...or build directly via cmake for VSCode / Visual Studio

   ```sh
   set CMAKE_TOOLCHAIN_FILE=C:/Users/vagrant/dev/vcpkg/scripts/buildsystems/vcpkg.cmake
   python -m venv .venv
   .venv\Scripts\activate.bat
   python -m pip install --upgrade pip
   pip install -U wheel

   cmake --preset visual_studio
   # or
   # cmake --preset vscode_win
   ```

   Open `build/visual_studio` or `build/vscode_win` in appropriate tool and enjoy.

   Build from command line:

   ```sh
   cmake --build build/visual_studio --config Debug --target sokoengine sokoenginepyext
   ```
