# Tutorial

There are few key concepts implemented by library and explained by following sections.

## Game variant

We implement four game variants: Sokoban, Hexoban, Trioban and Octoban. These differ by
plane tessellation on which game board is laid out:

- Sokoban boards consist of adjacent squares
- Hexoban boards consist of adjacent hexagons
- Trioban boards consist of adjacent triangles
- Octoban boards consist of interchanging, adjacent octagons and squares

`Tessellation` of game board determines available moves for game pieces. In general
there are 8 supported movement directions: left, right, up, down, north west, north
east, south west and south east. Of course, not all tessellations support all
directions. Also, one set of directions may have different meaning in different
tessellations.

To abstract all these differences, we implement `Tessellation` class, with subclass for
each of supported variants. Instances of `Tessellation` are then used by other classes
to parameterize game variant.

## Game boards

Game board consists of 2D grid of cells. Each cell has a state describing its board
element (ie. wall, pusher, box, goal...) and can have some additional flags added to
that state. These flags are not displayed but are used internally by board editors,
movement logic, etc.. Board elements (cells) are implemented by `BoardCell` class.

Game board is implemented using `VariantBoard` base class with concrete implementations
for each variant (ie. `SokobanPuzzle`, `HexobanBoard`, etc...). For speed efficiency,
board's 2D grid can be thought of as a 1D array of `BoardCell`. This means that most
methods in `VariantBoard` and in other places in library, use 1D indexes to reference
individual cells. Utility functions are provided that convert 2D coordinates to 1D
indexes and vice versa (ie. `index_1d`).

`VariantBoard` has following responsibilities:

- stores and provides reference to individual board cells
- manages board resizing (adding/removing rows and columns) for ie. editing sessions
- provides board-space searching capabilities like getting neighbor cell of given cell,
  detecting playable area of board, finding movement path between two points for either
  pusher or box, etc... (internally, appropriate graph structure for each tessellation
  and appropriate `Tessellation` are used)
- implements string (de)serialization. Traditional format for these strings is
  extended to support RLE compression of them, following specification of [SokobanYASC]
  .sok file format.

Constructing an instance of board is as easy as:

```python
>>> from sokoenginepy.io import SokobanPuzzle
>>> board = SokobanPuzzle(board='\n'.join([
...     '    #####',
...     '    #  @#',
...     '    #$  #',
...     '  ###  $##',
...     '  #  $ $ #',
...     '### # ## #   ######',
...     '#   # ## #####  ..#',
...     '# $  $          ..#',
...     '##### ### #@##  ..#',
...     '    #     #########',
...     '    #######'
... ]))
>>> print(board)
----#####----------
----#--@#----------
----#$--#----------
--###--$##---------
--#--$-$-#---------
###-#-##-#---######
#---#-##-#####--..#
#-$--$----------..#
#####-###-#@##--..#
----#-----#########
----#######--------

```

All boards implement rich API that allows editing individual board cells, resizing
and exploring neighboring positions. Positions are expressed as 1D array indexes
which can be retrieved from 2D coordinates using `index_1d`.

```python
>>> from sokoenginepy.io import Puzzle
>>> from sokoenginepy.game import BoardCell, Direction, index_1d
>>> position = index_1d(11, 8, board.width)
>>>
>>> board[position]
'@'
>>> print(board[position])
@
>>> board[position] = Puzzle.BOX
>>> board[position]
'$'
>>> board[position].has_pusher
False
>>> board[position].has_box
True
>>> board[position].put_pusher()
>>> board.neighbor(position, Direction.RIGHT)
164

```

Besides editing individual cells, all boards also support resizing, path searching,
etc...

## Game logic and movement

All game variants follow exactly same game rules. From [Wikipedia-Sokoban rules],
classic rules of Sokoban are:

> The game is played on a board of squares, where each square is a floor or a wall.
> Some floor squares contain boxes, and some floor squares are marked as storage
> locations.
>
> The player is confined to the board, and may move horizontally or vertically onto
> empty squares (never through walls or boxes). The player can also move into a box,
> which pushes it into the square beyond. Boxes may not be pushed into other boxes or
> walls, and they cannot be pulled. The number of boxes is equal to the number of
> storage locations. The puzzle is solved when all boxes are at storage locations.

Beside classic rules of games, we implement two rule additions:

1. Multiban - we allow and implement more than one pusher per board. In this situation,
   classic rules of game apply to each of the pushers on board with additional rule that
   *pusher can't move through another pusher*
2. Reverse mode board solving. This is another way of playing game. When game is
   started, box and goal positions are switched and rules of game are slightly modified:
   - pusher can only pull boxes, not push them
   - before first box is pulled pusher is allowed to jump to any empty board cell
   - when boxes' and goals' positions are switched, pusher may end up standing "on
     top" of box in which case first move for that pusher must be jump
   - jumping after first pull can be optionally enabled if that helps searching for
     board solution

Class responsible for implementing all movement rules is `Mover`. `Mover` instance is
attached to `VariantBoard` instance and it then performs movement on it.

Main responsibilities of `Mover` are:

- implement all game rules and modes of playing
- executes pusher and box movement on any `VariantBoard` instance
- provides single step undo/redo
- echoes performed moves (for movement display in rendering engines). This is especially
  interesting for future GUI implementations. To understand this feature better,
  consider following sequence of moves: `uuld` (up, up, left, down). When they are
  preformed, `Mover` echoes ``uuld`` which can be then rendered by ie. GUI. Now, let's
  say we want to undo them. We tell `Mover` to undo these moves and it echoes back
  `urdd` (up, right, down, down) which is straightforward to render in GUI. Without this
  feature, any rendering engine would have to actually know what undo of moves means and
  implement correct `undo` of performed movement making it (the rendering engine) both
  more complex and redundant.

`Mover` strives to be fast and efficient so it lacks full game features (like infinite
undo/redo, tracking and exporting movement history, etc.). It is intended to be used by
future full game implementations and solver implementations. Example usage of `Mover`:

```python
>>> from sokoenginepy.game import Mover, SolvingMode, IllegalMoveError, DEFAULT_PIECE_ID
>>>
>>> # regular, forward solving mode
>>> forward_mover = Mover(board)
>>> # select pusher that will perform movement
>>> forward_mover.select_pusher(DEFAULT_PIECE_ID + 1)
>>> # perform movement
>>> forward_mover.move(Direction.UP)
>>> # try to perform illegal move raises IllegalMoveError
>>> try:
...     forward_mover.move(Direction.UP)
... except IllegalMoveError as e:
...     print("IllegalMoveError risen!")
...     print(e)
...
IllegalMoveError risen!
Pusher ID: 2 can't be placed in position 125 occupied by '#'

>>> # reverse solving mode
>>> board = SokobanPuzzle(board="""
...     #####
...     #  @#
...     #$  #
...   ###  $##
...   #  $ $ #
... ### # ## #   ######
... #   # ## #####  ..#
... # $  $          ..#
... ##### ### #@##  ..#
...     #     #########
...     #######
... """[1:-1])
>>> reverse_mover = Mover(board, SolvingMode.REVERSE)
>>> print(reverse_mover.board.to_str(use_visible_floor=True))
----#####----------
----#--@#----------
----#.--#----------
--###--.##---------
--#--.-.-#---------
###-#-##-#---######
#---#-##-#####--$$#
#-.--.----------$$#
#####-###-#@##--$$#
----#-----#########
----#######--------

>>> # Sokoban+
>>> reverse_mover.board_manager.boxorder = '1 3 2'
>>> reverse_mover.board_manager.goalorder = '3 2 1'
>>> reverse_mover.board_manager.enable_sokoban_plus()
>>>
>>> # This check also considers if Sokoban+ is enabled...
>>> reverse_mover.board_manager.is_solved
False

```

`Mover` operates directly on referenced `VariantBoard` so that instance should not be
edited outside of its `Mover`. For the same reason, it is not allowed to attach two
movers to same game board.

## Piece tracking, position hashing and victory conditions

To allow fast pusher and box positions retrieval and tracking, we implement cache
class - `BoardManager`. This class stores positions of board pieces, and allows fast
update and retrieval of them.

On top of `BoardManager` we implement `HashedBoardManager`. Although `Mover` doesn't
need board hashing in any way, future solver implementations will need it.
`HashedBoardManager` implements Zobrist hashing of current positions of pushers and
boxes. This can then be used by solvers to implement and speed up game-space searches by
storing visited board hashes in cache tables while performing game-space search.

When `Mover` is attached to `VariantBoard` it also creates fresh instance of
`HashedBoardManager` and keeps it up to date with current board position.

`BoardManager` also implements checking of victory conditions. There are two main groups
of those:

1. Classic victory where any position in which each box is positioned on top of some
   goal
2. Sokoban+ victory condition where each box is positioned on top of goal with the
   same id as that box

Sokoban+ is optional feature that can be enabled by assigning `boxorder` and `goalorder`
sequences to board. When these sequences are present, new victory conditions are
activated. For example, having board with five boxes, we could assign these sequences:
`1 1 2 2 3` and `2 1 3 1 2`. After that, board is considered solved only when boxes with
ID 1 are a pushed onto goals with ID 1 etc... Example of `HashedBoardManager` usage:

```python
>>> from sokoenginepy.game import HashedBoardManager
>>> board = SokobanPuzzle(board="""
...     #####
...     #  @#
...     #$  #
...   ###  $##
...   #  $ $ #
... ### # ## #   ######
... #   # ## #####  ..#
... # $  $          ..#
... ##### ### #@##  ..#
...     #     #########
...     #######
... """[1:-1])
>>> manager = HashedBoardManager(board)
>>> manager
HashedBoardManager(variant_board=SokobanPuzzle(board='\n'.join([
    '    #####          ',
    '    #  @#          ',
    '    #$  #          ',
    '  ###  $##         ',
    '  #  $ $ #         ',
    '### # ## #   ######',
    '#   # ## #####  ..#',
    '# $  $          ..#',
    '##### ### #@##  ..#',
    '    #     #########',
    '    #######        '
])), boxorder='', goalorder='')

```

This class memoizes positions of pushers and boxes and assigns numerical IDs to them so
they can be referred to in different contexts.

```python
>>> from sokoenginepy.game import DEFAULT_PIECE_ID
>>> manager.pushers_ids
[1, 2]
>>> manager.pushers_positions
{1: 26, 2: 163}
>>> manager.has_pusher(42)
False
>>> manager.has_pusher_on(163)
True
>>> manager.pusher_position(DEFAULT_PIECE_ID)
26
>>> manager.box_position(DEFAULT_PIECE_ID + 2)
81

```

Now that we have a way to refer to individual pushers, boxes and goals, we can also use
Sokoban+ strings which changes end game conditions:

```python
>>> manager.boxorder = '1 3 2'
>>> manager.goalorder = '3 2 1'
>>> manager.enable_sokoban_plus()
>>> manager.is_sokoban_plus_enabled
True
>>> manager.is_sokoban_plus_valid
True

```

Above code block means that pieces get following Sokoban+ IDs:

| box/goal ID          | box Sokoban+ ID | goal Sokoban+ ID |
| -------------------- | --------------- | ---------------- |
| DEFAULT_PIECE_ID     | 1               | 3                |
| DEFAULT_PIECE_ID + 1 | 3               | 2                |
| DEFAULT_PIECE_ID + 2 | 2               | 1                |

And board is solved only when matching Sokoban+ ids are paired.

The last thing that `HashedBoardManager` does is Zobrist hashing of board. This is
mainly useful for implementing game solvers.

When initialized, `HashedBoardManager` hashes board using positions and IDs of boxes and
produces 64b integer hash. After that, whenever position changes, this hash is updated.
The ``Zobrist`` part means hashing is deterministic which then means that undoing box
move will return hash value to previous one. All this allows for creation of position
tables that contain many board layouts and can be quickly compared (since we are not
comparing positions but only hashes of these positions). Being able to quickly compare
and find current board layout in some big table, speeds up searching through game space
which is needed for effective solver implementations.

```python
>>> from sokoenginepy.game import Mover, Direction
>>> mover = Mover(board)
>>> initial_hash = mover.board_manager.state_hash
>>> mover.move(Direction.DOWN)
>>> moved_hash = mover.board_manager.state_hash
>>> mover.undo_last_move()
>>> mover.board_manager.state_hash == initial_hash
True
>>> mover.move(Direction.DOWN)
>>> mover.board_manager.state_hash == moved_hash
True

```

## Game snapshots and movement recording

Each step of each pusher is recorded by instance of `PusherStep`. Sequence of
`PusherStep` is implemented in `Snapshot`. Just like `VariantBoard`, `Snapshot`
is serializable to string. Traditional snapshots string format is extended to support
recording of jumps and selecting of different pushers in Multiban boards, again
following [SokobanYASC] .sok file format specification.

## Reading and writing Sokoban files

`Puzzle` and `PuzzlesCollection` are collections of strings representing boards,
snapshots and meta data like author or title. These classes are intermediate results of
parsing Sokoban files.

This intermediary data is faster to manipulate and less memory hungry than full game
board and game snapshot. That way it is possible to efficiently and quickly load, store
and manipulate whole puzzle collections in memory. On the other hand, `Puzzle` and
`Snapshot` can be easily converted to `VariantBoard` and `Snapshot` when needed.

```python
from sokoenginepy.io import Collection

collection = Collection()
collection.load("~/sokoban/collections/fabulous_sokoban_problems.sok")

board = collection[0].to_game_board()
# => SokobanPuzzle

snapshot = collection[0].snapshots[0].to_game_snapshot()
# => Snapshot

# After board editing or game play...

collection[0].snapshots[0].moves = str(some_recorded_snapshot)
collection[0].board = str(some_edited_board)
```

[SokobanYASC]: (https://sourceforge.net/projects/sokobanyasc/)
[Wikipedia-Sokoban rules]: (https://en.wikipedia.org/wiki/Sokoban#Rules)
