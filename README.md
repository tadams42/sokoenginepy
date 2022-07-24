# sokoenginepy - Sokoban and variants

[![badge - PyPi version]](https://pypi.org/project/sokoenginepy/)
[![badge - Python versions]](https://docs.python.org/3/)
[![badge - C++ version]](https://en.cppreference.com/w/cpp/17)
[![badge - CI - tests]](https://github.com/tadams42/sokoenginepy/actions/workflows/tests.yaml)
[![badge - ReadTheDocs build]](http://sokoenginepy.readthedocs.io/en/latest/)
[![badge - C++ docs]](http://tadams42.github.io/sokoenginepy/)
[![badge - Codecov]](https://codecov.io/gh/tadams42/sokoenginepy)
[![badge - license]](https://opensource.org/licenses/GPL-3.0)

This project implements various utilities for Sokoban:

- board representation for Sokoban, Hexoban, Trioban and Octoban variants with support
  for Sokoban+ and Multiban for all four variants
- game engine implementation
- [SokobanYASC] compatible level collections file reader / writer

It provides two implementations:

- `sokoenginepy` - pure Python implementation
- `libsokoengine` - C++ library

## Documentation

- Tutorial: [Read the Docs - Tutorial]
- Python docs: [Read the Docs]
- C++ docs: [Doxygen documentation]

## Example

In Python:

```python
import textwrap
from sokoenginepy import Config, Direction, Tessellation, Puzzle, BoardGraph, Mover

data = textwrap.dedent("""
        #####
        #  @#
        #$  #
      ###  $##
      #  $ $ #
    ### # ## #   ######
    #   # ## #####  ..#
    # $  $          ..#
    ##### ### #@##  ..#
        #     #########
        #######
""")
puzzle = Puzzle(Tessellation.SOKOBAN, board=data)
board = BoardGraph(puzzle)
mover = Mover(board)
mover.select_pusher(Config.DEFAULT_ID + 1)
mover.move(Direction.UP)
print(board)
```

or in C++:

```cpp
#include <sokoengine.hpp>

#include <iostream>

using sokoengine::BoardGraph;
using sokoengine::Config;
using sokoengine::Direction;
using sokoengine::Mover;
using sokoengine::Tessellation;
using sokoengine::Puzzle;
using std::string;

int main() {
  string data = R"""(
    #####
    #  @#
    #$  #
  ###  $##
  #  $ $ #
### # ## #   ######
#   # ## #####  ..#
# $  $          ..#
##### ### #@##  ..#
    #     #########
    #######
)""";

  Puzzle puzzle(Tessellation::SOKOBAN, data);
  BoardGraph board(puzzle);
  Mover mover(board);
  mover.select_pusher(Config::DEFAULT_ID + 1);
  mover.move(Direction::UP);

  std::cout << board.str() << std::endl;

  return 0;
}
```

## Install

`sokoenginepy` package from [PyPi]:

```sh
pip install sokoenginepy
```

or `libsokoengine` C++ library:

You will need [vcpkg] and then:

```sh
sudo apt install git build-essential cmake doxygen

git clone https://github.com/tadams42/sokoenginepy.git
cd sokoenginepy/

export CMAKE_TOOLCHAIN_FILE=[path to vcpkg]/scripts/buildsystems/vcpkg.cmake
cmake --preset "debug"

cd build/debug/
make && make install
```

For more elaborate details, see [INSTALL.md](./INSTALL.md)

## Why?

- experimenting with [Boost.X3], [Boost.Graph], [Boost.GIL] and [Boost.Geometry] in C++
- experimenting with [NetworkX] in Python
- experimenting with [pybind11]
- playing with [SokobanYASC] `.sok` file format and providing fully compatible
  implementation for it in both, Python and C++

[Boost.GIL]: https://www.boost.org/doc/libs/1_79_0/libs/gil/doc/html/index.html
[Boost.Graph]: https://www.boost.org/doc/libs/1_78_0/libs/graph/doc/index.html
[Boost.Geometry]: https://www.boost.org/doc/libs/1_79_0/libs/geometry/doc/html/index.html
[Boost.X3]: https://www.boost.org/doc/libs/1_79_0/libs/spirit/doc/x3/html/spirit_x3/preface.html
[NetworkX]: https://networkx.org/
[pybind11]: http://pybind11.readthedocs.io/en/stable/index.html
[PyPi]: https://pypi.org/
[cmake]: https://cmake.org/
[SokobanYASC]: https://sourceforge.net/projects/sokobanyasc/
[badge - PyPi version]: https://img.shields.io/pypi/v/sokoenginepy.svg
[badge - Python versions]: https://img.shields.io/pypi/pyversions/sokoenginepy.svg
[badge - C++ version]: https://img.shields.io/badge/C%2B%2B-17-blue
[badge - CI - tests]: https://github.com/tadams42/sokoenginepy/actions/workflows/tests.yaml/badge.svg?branch=development
[badge - ReadTheDocs build]: https://readthedocs.org/projects/sokoenginepy/badge/?style=flat
[badge - C++ docs]: https://img.shields.io/badge/C%2B%2B-docs-brightgreen
[badge - Codecov]: https://codecov.io/gh/tadams42/sokoenginepy/branch/development/graph/badge.svg?token=nnJAZHQyz9
[badge - license]: https://img.shields.io/github/license/tadams42/sokoenginepy
[Read the Docs - Tutorial]: https://sokoenginepy.readthedocs.io/en/latest/tutorial.html
[Doxygen documentation]: http://tadams42.github.io/sokoenginepy/
[Read the Docs]: https://sokoenginepy.readthedocs.io/en/latest/
[vcpkg]: https://vcpkg.io/
