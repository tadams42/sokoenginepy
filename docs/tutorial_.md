# Tutorial

## Game tessellation

`sokoenginepy` implements four game variants: Sokoban, Hexoban, Trioban and Octoban.
These differ by plane tessellation on which game board is laid out:

- Sokoban boards consist of adjacent squares
- Hexoban boards consist of adjacent hexagons
- Trioban boards consist of adjacent triangles
- Octoban boards consist of interchanging octagons and squares

For each game tessellation there is :

- a class that implements tessellation speciffics (ie. `SokobanTessellation`,
  `HexobanTesselation`, etc...)
- a class that implements puzzle (ie. `SokobanPuzzle`, `HexobanPuzzle`, etc...)
- a class that implements snapshot (ie. `SokobanSnapshot`, `HexobanSnapshot`, etc...)

Tessellation class determines available moves for game pieces in . In general there are
8 supported movement directions: left, right, up, down, north west, north east, south
west and south east. Not all tessellations support all directions and some directions
have different meaning in different tessellations.

All this is abstracted by before mentioned `Puzzle` and `Snapshot` classes.

## Game puzzle

Game puzzle can be instantiated like this:

```python
>>> import textwrap
>>> from sokoenginepy.io import SokobanPuzzle
>>> data = """
...         #####
...         #  @#
...         #$  #
...       ###  $##
...       #  $ $ #
...     ### # ## #   ######
...     #   # ## #####  ..#
...     # $  $          ..#
...     ##### ### #@##  ..#
...         #     #########
...         #######
... """
>>> data = textwrap.dedent(data.lstrip("\n").rstrip())
>>> puzzle = SokobanPuzzle(board=data)
>>> print(repr(puzzle))
SokobanPuzzle(board='\n'.join([
    '----#####----------',
    '----#--@#----------',
    '----#$--#----------',
    '--###--$##---------',
    '--#--$-$-#---------',
    '###-#-##-#---######',
    '#---#-##-#####--..#',
    '#-$--$----------..#',
    '#####-###-#@##--..#',
    '----#-----#########',
    '----#######--------'
]))

```

or for `Hexoban`:

```python
>>> import textwrap
>>> from sokoenginepy.io import HexobanPuzzle
>>>
>>> data = """
...     ---#-#-#-#----------
...     --#-------#---------
...     -#-@-----#----------
...     --#-$---$-#-#-#-#-#-
...     -#---.---.-+---$---#
...     --#---*-----------#-
...     ---#-#-#-#-#-#-#-#--
... """
>>> data = textwrap.dedent(data.lstrip("\n").rstrip())
>>> hexoban_puzzle = HexobanPuzzle(board=data)
>>> print(repr(hexoban_puzzle))
HexobanPuzzle(board='\n'.join([
    '---#-#-#-#----------',
    '--#-------#---------',
    '-#-@-----#----------',
    '--#-$---$-#-#-#-#-#-',
    '-#---.---.-+---$---#',
    '--#---*-----------#-',
    '---#-#-#-#-#-#-#-#--'
]))

```

Puzzles implement rich API that allows editing individual board cells and resizing game
board. One important note about this is that all board positions in API are specified
as 1D coordinates. To convert from 2D to 1D coordinates, use `index_1d()` function.

```python
>>> from sokoenginepy.game import index_1d
>>> position = index_1d(11, 8, puzzle.width)
>>> puzzle[position]
'@'

```

## Playing a game

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

Beside classic rules of games, we implement few (optional) rule additions:

1. `Multiban`
   More than one pusher is present on game board. In this situation, classic rules of
   game apply to each of the pushers on board with additional rule that
   *pusher can't move through another pusher*
2. `Reverse mode` game solving
   When game is started, box and goal positions are switched and rules of game are
   slightly modified:
   - pusher can only pull boxes, not push them
   - before first box is pulled pusher is allowed to jump to any empty board cell
   - when boxes' and goals' positions are switched, pusher may end up standing "on
     top" of box in which case first move for that pusher must be jump
   - jumping after first pull can be optionally enabled if that helps searching for
     board solution
3. `Sokoban+`
   - restricts pairing between boxes and goals such that not any box can go to any goal
     like in ordinary Sokoban rules

Class responsible for implementing all movement rules is `Mover`. Class responsible for
representing game puzzle when playing it is `BoardGraph`.

This is how to play game in regular, forward solving mode:

```python
>>> from sokoenginepy.game import Mover, SolvingMode, IllegalMoveError, Direction
>>> from sokoenginepy.game import Config, BoardGraph
>>>
>>> board = BoardGraph(puzzle)
>>>
>>> forward_mover = Mover(board)
>>> # select pusher that will perform movement
>>> # notice that our starting board, already has two pushers
>>> # so we need to tell Mover which one we want to move
>>> forward_mover.select_pusher(Config.DEFAULT_PIECE_ID + 1)
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

```

And to play in reverse mode:

```python
>>> # reverse solving mode
>>> puzzle2 = SokobanPuzzle(board="""
...         #####
...         #  @#
...         #$  #
...       ###  $##
...       #  $ $ #
...     ### # ## #   ######
...     #   # ## #####  ..#
...     # $  $          ..#
...     ##### ### #@##  ..#
...         #     #########
...         #######
... """[1:-1])
>>> board2 = BoardGraph(puzzle2)
>>> reverse_mover = Mover(board2, SolvingMode.REVERSE)
>>> print(reverse_mover.board)
--------#####----------
--------#--@#----------
--------#.--#----------
------###--.##---------
------#--.-.-#---------
----###-#-##-#---######
----#---#-##-#####--$$#
----#-.--.----------$$#
----#####-###-#@##--$$#
--------#-----#########
--------#######--------

```

## Piece tracking

When `Mover` is attached to `BoardGraph` it internally creates board manager and keeps
it up to date with action happening on board. Board manager assigns unique IDs to all
board pieces (pushers, boxes and goals) and tracks their positions:

```python
>>> forward_mover.board_manager.pushers_ids
[1, 2]
>>> forward_mover.board_manager.pushers_positions
{1: 26, 2: 144}
>>> forward_mover.board_manager.has_pusher(42)
False
>>> forward_mover.board_manager.has_pusher_on(144)
True
>>> forward_mover.board_manager.pusher_position(Config.DEFAULT_PIECE_ID)
26
>>> forward_mover.board_manager.box_position(Config.DEFAULT_PIECE_ID + 2)
81

```

How are piece IDs assigned?

We start scanning game board from top left corner to the right, row by row. First
encountered box will get `box.id = Config.DEFAULT_PIECE_ID`, second one `box.id =
Config.DEFAULT_PIECE_ID + 1`, etc... Same goes for pushers and goals.

## Position hashing

`mover.board_manager` also implements [Zobrist hashing] of board state:

```python
>>> from sokoenginepy.game import Mover, Direction, BoardGraph
>>> board = BoardGraph(puzzle)
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

Zobrist hashing is deterministic which means that undoing box move will return hash
value to previous one. `Mover` doesn't or use board hashing internally in any way, but
any kind of solver implementations will need it to speed up game-space searches and
position caching.

## Victory conditions and Sokoban+

Board manager is also used fof checking of victory conditions. There are two types of
game victory conditions:

1. `Classic` victory is any board position in which each box is positioned on top of
   each goal
2. `Sokoban+` victory is board position where each box is positioned on top of each goal
   with the same Sokoban+ ID as that box

`Sokoban+` can be enabled by assigning `boxorder` and `goalorder` sequences to board
manager (for any kind of `Mover`, forward or reverse).

For example, having a board with five boxes, we could assign `boxorder = "1 1 2 2 3"`
and `goalorder = "2 1 3 1 2"` and activate `Sokoban+`

After activating it, board is considered solved only when boxes with `box.plus_id == 1`
are a pushed onto goals with `goal.plus_id == 1`, boxes with `box.plus_id == 2` are a
pushed onto goals with `goal.plus_id == 2`, etc...

```python
>>> mover.board_manager.boxorder = '1 3 2'
>>> mover.board_manager.goalorder = '3 2 1'
>>> mover.board_manager.enable_sokoban_plus()

```

How are `Sokoban+` strings interpreted?

Position of each ID in Sokoban+ string, determines ID of the piece that will get that
`plus_id`. Or, by example:

| box/goal ID          | box Sokoban+ ID | goal Sokoban+ ID |
| -------------------- | --------------- | ---------------- |
| DEFAULT_PIECE_ID     | 1               | 3                |
| DEFAULT_PIECE_ID + 1 | 3               | 2                |
| DEFAULT_PIECE_ID + 2 | 2               | 1                |

When `boxorder` and `goalorder` are present, valid and enabled, then new victory
conditions are activated for given `Mover`. This affects result of call to
`mover.is_solved`:

```python
>>> mover.board_manager.is_sokoban_plus_enabled
True
>>> # Following check will now also takes Sokoban+ into account
>>> mover.board_manager.is_solved
False

```

## Reading and writing Sokoban files

`sokoenginepy` fully support [SokobanYASC] `.sok` file format. It can load and save
puzzle collections and game solutions for all implemented game variants and
tessellations.

```python
from sokoenginepy.io import Collection

collection = Collection()
collection.load("~/sokoban/collections/fabulous_sokoban_problems.sok")

puzzle = collection.puzzles[0]
# => SokobanPuzzle

snapshot = collection.puzzles[0].snapshots[0]
# => SokobanSnapshot

# Edit game board, add more boards to collection.puzzles and more solutions to
# puzzle.snapshots...

collection.save("~/sokoban/collections/some_other_file.sok")
```

[SokobanYASC]: (https://sourceforge.net/projects/sokobanyasc/)
[Wikipedia-Sokoban rules]: (https://en.wikipedia.org/wiki/Sokoban#Rules)
[Zobrist hashing]: (https://en.wikipedia.org/wiki/Zobrist_hashing)
