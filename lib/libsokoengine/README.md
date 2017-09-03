# libsokoengine

Sokoban and variants game engine

![Version](http://img.shields.io/badge/version-0.5.2-blue.svg)
[![Language](http://img.shields.io/badge/language-C++11-lightgrey.svg)](http://en.cppreference.com/w/)
[![License](http://img.shields.io/badge/license-GPLv3-brightgreen.svg)](http://opensource.org/licenses/GPL-3.0)

C++ implementation of classic Sokoban game inspired by [SokobanYASC], [JSoko] and [MazezaM] featuring:

- portable, using C++11 and [boost]
- supports Sokoban, Hexoban, Trioban and Octoban variants
  - Sokoban+ for all supported variants
  - multiple pushers (Multiban) for all variants
- fast and game engine implementation with single step undo/redo
- TODO: self sufficient, clients are not required to link to any dependencies (not even Boost which is linked statically)

## Install

- [Install](INSTALL.md) - Detailed build and install instructions (including integration with your [CMake] projects, etc...)

Quick and dirty:

~~~bash
$ git clone --recursive https://github.com/tadams42/sokoenginepy.git
$ cd sokoenginepy && mkdir build && cd build
$ cmake ../
$ make && make install
~~~

## Usage & Documentation

Full docs can be generated from source using `make docs` target ([Doxygen]
required)

Minimal example `main.cpp`:

~~~C++
#include <sokoengine.hpp>

using namespace sokoengine;

int main() {
  HexobanBoard b;
  return 0;
}
~~~

## Big picture view

### Tessellation

Everything that is variant dependent is implemented by `Tessellation`.
`Tessellation` is then used to parametrize other base classes. Concrete
implementations usually don't need to interact with `Tessellation` objects
directly.

### Game boards

Boards consist of `BoardCell`. Individual `BoardCell` are accessed using 1D
indexes because of speed optimization. Where needed, there are helper methods
provided for coordinate conversion: `index_1d`, `X`, `Y`.

Concrete boards are implemented as subclasses of `VariantBoard` class which is
parametrized by `Tessellation` and does the following:

- manages individual board cells
- provides board-space searching capabilities (internally it uses appropriate
  graph structure for each tessellation)
- implements `std::string` (de)serialization.

~~~C++
// construction from string
HexobanBoard board(string() +
  "---#-#-#-#----------\n" +
  "--#-------#---------\n" +
  "-#-@-----#----------\n" +
  "--#-$---$-#-#-#-#-#-\n" +
  "-#---.---.-+---$---#\n" +
  "--#---*-----------#-\n" +
  "---#-#-#-#-#-#-#-#--\n"
);

// editing and cell referencing
board[42].has_pusher();
board[42] = BoardCell('@');
const BoardCell& cell = board[index_1d(42, 24, board.width())];

// board-space searches
position_t pusher_position = 42;
Positions reachable_by_pusher = board.positions_reachable_by_pusher(pusher_position);
board.mark_play_area();
position_t neighbor = board.neighbor(42, Direction::NORTH_WEST);
Positions jump_path = board.find_jump_path(42, 24);

// std::string serialization
string output = board.to_str();
~~~

### Movement

Class responsible for movement is `Mover`. It can be attached to `VariantBoard`
object to perform movement on it.

`Mover` is attached to `VariantBoard` instance and:

- implements all movement rules for any tessellation.
- provides single step undo/redo
- echoes performed moves (for movement display in rendering engines)
- implements forward and reverse mode of puzzle solving

`Mover` strives to be fast and efficient so it lacks full game features (like
infinite undo/redo, tracking and exporting movement history, etc.). It is
intended to be used by full game implementations and solver implementations.

~~~C++
// Forward solving mode is default
SokobanBoard board(42, 24);
Mover mover(board);

// Constructing reverse mover switches box and goal positions in supplied board
SokobanBoard board2(42, 24);
Mover mover2(board2, SolvingMode::REVERSE);

// selecting pusher that will perform next move
mover.select_pusher(DEFAULT_PIECE_ID);
mover.select_pusher(DEFAULT_PIECE_ID + 2);

// Forward mode: move selected pusher right and push box if it is there
// Reverse mode: move pusher right and pull box with it if box is there
mover.move(Direction::RIGHT);

// Box pulling in reverse mode can be enabled/disabled
mover.set_pulls_boxes(false);

// jump selected pusher to new position
// jumps are allowed only in reverse mode and only before first box pull
mover2.jump(42);

// echoing performed movement for rendering engines
const Mover::Moves& moves = mover.last_move();
mover.move(Direction::LEFT);
// moves[0].direction() == Direction::LEFT
mover.undo_last_move();
// moves[0].direction() == Direction::RIGHT;
~~~

`Mover` operates directly on referenced `VariantBoard` so that instance should
not be edited outside of its `Mover`. For the same reason, it is not allowed to
attach two movers to same game board.

#### Tracking movement state and victory conditions

`Mover` internally uses `HashedBoardState` which performs following:

- keeps track of piece IDs and manages Sokoban+
- allows fast access to game pieces by either ID or position
- keeps consistant Zobrist hash of attached `VariantBoard` and updates it with
  each move

`HashedBoardState` is what allows fast `Mover` implementation and these two
classes are intended to be used for future implementations of solvers.

## Troubleshooting, issues and bugs

Pull requests and issue reports are welcome and greatly appreciated.

[SokobanYASC]:http://sourceforge.net/projects/sokobanyasc/
[JSoko]:http://www.sokoban-online.de/
[MazezaM]:http://webpages.dcu.ie/~tyrrelma/MazezaM/
[bandit]:http://banditcpp.org/
[boost]:http://www.boost.org/
[CMake]:http://www.cmake.org
[Doxygen]:http://www.stack.nl/~dimitri/doxygen/
