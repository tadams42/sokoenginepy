# sokoenginepy - Sokoban and variants

[![version](https://img.shields.io/pypi/v/sokoenginepy.svg)](https://pypi.org/project/sokoenginepy/)
[![python_versions](https://img.shields.io/pypi/pyversions/sokoenginepy.svg)](https://pypi.org/project/sokoenginepy/)
![cpp](https://img.shields.io/badge/C%2B%2B-17-blue)
![GitHub CI](https://github.com/tadams42/sokoenginepy/actions/workflows/tests.yaml/badge.svg?branch=development)
[![docs](https://readthedocs.org/projects/sokoenginepy/badge/?style=flat)](http://sokoenginepy.readthedocs.io/en/latest/)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/3dd265ede6bd4c38a2cd1250738a1bfa)](https://app.codacy.com/gh/tadams42/sokoenginepy/dashboard)
[![codecov](https://codecov.io/gh/tadams42/sokoenginepy/branch/development/graph/badge.svg?token=nnJAZHQyz9)](https://codecov.io/gh/tadams42/sokoenginepy)
[![license](https://img.shields.io/github/license/tadams42/sokoenginepy)](https://opensource.org/licenses/GPL-3.0)

This project implements various utilities for Sokoban:

- board representation for Sokoban, Hexoban, Trioban and Octoban variants with support
  for Sokoban+ and Multiban for all four variants
- game engine implementation
- [SokobanYASC] compatible level collections file reader / writer

It provides two implementations:

- `sokoenginepy` - pure Python implementation
- `libsokoengine` - C++ library

## Documentation

- Tutorial: [Read the Docs - Tutorial](https://sokoenginepy.readthedocs.io/en/latest/tutorial.html)
- Python docs: [Read the Docs](https://sokoenginepy.readthedocs.io/en/latest/)
- C++ docs: [libsokoengine Doxygen documentation](http://tadams42.github.io/sokoenginepy/)

## Example

In Python:

```python
import textwrap
from sokoenginepy.io import SokobanPuzzle
from sokoenginepy.game import BoardGraph, Mover, Direction, Config

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
puzzle = SokobanPuzzle(board=data)
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

using sokoengine::game::BoardGraph;
using sokoengine::game::Direction;
using sokoengine::game::Mover;
using sokoengine::game::Config;
using sokoengine::io::SokobanPuzzle;
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

  SokobanPuzzle puzzle(data);
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

You will need [vcpkg](https://vcpkg.io/) and then:

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

- experimenting with [Boost.X3] in C++
- experimenting with [Boost.Graph] in C++
- experimenting with [NetworkX] in Python
- experimenting with [pybind11]
- playing with [SokobanYASC] `.sok` file format and providing fully compatible
  implementation for it in both, Python and C++

[Boost.Graph]: https://www.boost.org/doc/libs/1_78_0/libs/graph/doc/index.html
[Boost.X3]: https://www.boost.org/doc/libs/1_79_0/libs/spirit/doc/x3/html/spirit_x3/preface.html
[NetworkX]: https://networkx.org/
[pybind11]: http://pybind11.readthedocs.io/en/stable/index.html
[PyPi]: https://pypi.org/
[cmake]: https://cmake.org/
[SokobanYASC]: https://sourceforge.net/projects/sokobanyasc/
