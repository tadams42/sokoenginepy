# libsokoengine

Sokoban and variants game engine

![Version](http://img.shields.io/badge/version-0.5.3-blue.svg)
[![Language](http://img.shields.io/badge/language-C++14-lightgrey.svg)](http://en.cppreference.com/w/)
[![License](http://img.shields.io/badge/license-GPLv3-brightgreen.svg)](http://opensource.org/licenses/GPL-3.0)

C++ implementation of classic Sokoban game inspired by [SokobanYASC], [JSoko] and [MazezaM] featuring:

- portable, using C++14 and [boost]
- supports Sokoban, Hexoban, Trioban and Octoban variants
  - Sokoban+ for all supported variants
  - multiple pushers (Multiban) for all variants
- fast game engine implementation with single step undo/redo
- Optional Python 3 bindings using [pybind11]
- TODO: self sufficient - clients are not required to link to any dependencies (not even Boost) because all compile time dependencies are either header-only or linked statically by default and also not exposed in own libsokoengine headers

Full C++ API docs are available at [http://tadams42.github.io/sokoenginepy/](http://tadams42.github.io/sokoenginepy/). Following sections describe key concepts of library.

- [libsokoengine](#libsokoengine)
    - [Install](#install)
    - [Usage & Documentation](#usage--documentation)
    - [Big picture view](#big-picture-view)
        - [Game variant](#game-variant)
        - [Game boards](#game-boards)
        - [Game logic and movement](#game-logic-and-movement)
        - [Piece tracking, position hashing and victory conditions](#piece-tracking-position-hashing-and-victory-conditions)
        - [Game snapshots and movement recording](#game-snapshots-and-movement-recording)
    - [Troubleshooting, issues and bugs](#troubleshooting-issues-and-bugs)

## Install

Detailed build and install instructions (including integration with your [CMake] projects, etc...) are in [INSTALL.md](INSTALL.md). Quick summary:

~~~sh
git clone --recursive https://github.com/tadams42/sokoenginepy.git
cd sokoenginepy && mkdir build && cd build
cmake ../
make && make install
~~~

## Usage & Documentation

Full docs can be generated from source using `make docs` target ([Doxygen] required) and are also available online at [http://tadams42.github.io/sokoenginepy/](http://tadams42.github.io/sokoenginepy/). Note that online docs are generated from `master` branch.

Minimal example `main.cpp` is:

~~~cpp
#include <sokoengine.hpp>

using namespace sokoengine;

int main() {
  HexobanBoard b;
  return 0;
}
~~~

## Big picture view

There are few key concepts implemented by library and explained by following sections.

### Game variant

We implement four game variants: Sokoban, Hexoban, Trioban and Octoban. These differ by plane tessellation on which game board is laid out:

- Sokoban boards consist of adjacent squares
- Hexoban boards consist of adjacent hexagons
- Trioban boards consist of adjacent triangles
- Octoban boards consist of interchanging, adjacent octagons and squares

Tessellation of game board determines available moves for game pieces. In general there are 8 supported movement directions: left, right, up, down, north west, north east, south west and south east. Of course, not all tessellations support all directions. Also, one set of directions may have different meaning in different tessellations.

To abstract all these differences, we implement `Tessellation` class, with subclass for each of supported variants. Instances of `Tessellation` are then used by other classes to parameterize game variant.

Note that `Tessellation` is low level implementation detail, and although it helps to be aware of its existence, client code doesn't usually need to interact with it directly.

### Game boards

Game board consists of 2D grid of cells. Each cell has a state describing its board element (ie. wall, pusher, box, goal...) and can have some additional flags added to that state. These flags are not displayed but are used internally by board editors, movement logic, etc.. Board elements (cells) are implemented by `BoardCell` class.

Game board is implemented using `VariantBoard` base class with concrete implementations for each variant (ie. `SokobanBoard`, `HexobanBoard`, etc...). For speed efficiency, board's 2D grid can be thought of as a 1D array of `BoardCell`. This means that most methods in `VariantBoard` and in other places in library, use 1D indexes to reference individual cells. Utility functions are provided that convert 2D coordinates to 1D indexes and vice versa (ie. `index1d`).

`VariantBoard` has following responsibilities:

- stores and provides reference to individual board cells
- manages board resizing (adding/removing rows and columns) for ie. editing sessions
- provides board-space searching capabilities like getting neighbor cell of given cell, detecting playable area of board, finding movement path between two points for either pusher or box, etc... (internally, appropriate graph structure for each tessellation and appropriate `Tessellation` are used)
- implements `std::string` (de)serialization. Traditional format for these strings is extended to support RLE compression of them, following specification of `SokobanYASC` `.sok` format.

Following is some example code for `VariantBoard` usage:

~~~cpp
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

### Game logic and movement

All game variants follow exactly same game rules. From [Wikipedia-Sokoban rules], classic rules of Sokoban are:

> The game is played on a board of squares, where each square is a floor or a wall. Some floor squares contain boxes, and some floor squares are marked as storage locations.
>
> The player is confined to the board, and may move horizontally or vertically onto empty squares (never through walls or boxes). The player can also move into a box, which pushes it into the square beyond. Boxes may not be pushed into other boxes or walls, and they cannot be pulled. The number of boxes is equal to the number of storage locations. The puzzle is solved when all boxes are at storage locations.

Beside classic rules of games, we implement two rule additions:

1. Multiban - we allow and implement more than one pusher per board. In this situation, classic rules of game apply to each of the pushers on board with additional rule that *pusher can't move through another pusher*
2. Reverse mode board solving. This is another way of playing game. When game is started, box and goal positions are switched and rules of game are slightly modified:

    - pusher can only pull boxes, not push them
    - before first box is pulled pusher is allowed to jump to any empty board cell
    - when boxes' and goals' positions are switched, pusher may end up standing "on top" of box in which case first move for that pusher must be jump
    - jumping after first pull can be optionally enabled if that helps searching for board solution

Class responsible for implementing all movement rules is `Mover`. `Mover` instance is attached to `VariantBoard` instance and it then performs movement on it.

Main responsibilities of `Mover` are:

- implement all game rules and modes of playing
- executes pusher and box movement on any `VariantBoard` instance
- provides single step undo/redo
- echoes performed moves (for movement display in rendering engines). This is especially interesting for future GUI implementations. To understand this feature better, consider following sequence of moves: `uuld` (up, up, left, down). When they are preformed, `Mover` echoes `uuld` which can be then rendered by ie. GUI. Now, let's say we want to undo them. We tell `Mover` to undo these moves and it echoes back `urdd` (up, right, down, down) which is straightforward to render in GUI. Without this feature, any rendering engine would have to actually know what undo of moves means and implement correct `undo` of performed movement making it (the rendering engine) both more complex and redundant.

`Mover` strives to be fast and efficient so it lacks full game features (like infinite undo/redo, tracking and exporting movement history, etc.). It is intended to be used by future full game implementations and solver implementations.

Examples of `Mover` use:

~~~cpp
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

`Mover` operates directly on referenced `VariantBoard` so that instance should not be edited outside of its `Mover`. For the same reason, it is not allowed to attach two movers to same game board.

### Piece tracking, position hashing and victory conditions

To allow fast pusher and box positions retrieval and tracking, we implement cache class - `BoardManager`. This class stores positions of board pieces, and allows fast update and retrieval of them.

On top of `BoardManager` we implement `HashedBoardManager`. Although `Mover` doesn't need board hashing in any way, future solver implementations will need it. `HashedBoardManager` implements Zobrist hashing of current positions of pushers and boxes. This can then be used by solvers to implement and speed up game-space searches by storing visited board hashes in cache tables while performing game-space search.

When `Mover` is attached to `VariantBoard` it also creates fresh instance of `HashedBoardManager` and keeps it up to date with current board position.

`BoardManager` also implements checking of victory conditions. There are two main groups of those:

1. Classic victory where any position in which each box is positioned on top of some goal
2. Sokoban+ victory condition where each box is positioned on top of goal with the same id as that box

Sokoban+ is optional feature that can be enabled by assigning `boxorder` and `goalorder` sequences to board. When these sequences are present, new victory conditions are activated. For example, having board with five boxes, we could assign these sequences: `1 1 2 2 3` and `2 1 3 1 2`. After that, board is considered solved only when boxes with ID 1 are a pushed onto goals with ID 1 etc...

### Game snapshots and movement recording

Each step of each pusher is recorded by instance of `AtomicMove`. Sequence of `AtomicMove` is implemented in `Snapshot`. Just like `VariantBoard`, `Snapshot` is serializable to `std::string`. Traditional snapshots string format is extended to support recording of jumps and selecting of different pushers in `Multiban` boards, again following `SokobanYASC` `.sok` format specification.

## Troubleshooting, issues and bugs

Pull requests and issue reports are welcome and greatly appreciated.

[SokobanYASC]:https://sourceforge.net/projects/sokobanyasc/
[JSoko]:https://www.sokoban-online.de/
[MazezaM]:http://webpages.dcu.ie/~tyrrelma/MazezaM/
[bandit]:http://banditcpp.org/
[boost]:http://www.boost.org/
[CMake]:http://www.cmake.org
[Doxygen]:http://www.stack.nl/~dimitri/doxygen/
[pybind11]: https://github.com/pybind/pybind11
[Wikipedia-Sokoban rules]: https://en.wikipedia.org/wiki/Sokoban#Rules
