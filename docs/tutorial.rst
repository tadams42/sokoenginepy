Tutorial
--------

Game board
^^^^^^^^^^

For each implemented game variant, there is a game board class. Game variants
differ by board tessellation, and supported tessellations are enumerated in
:class:`.Tessellation`. We provide following board classes: :class:`.SokobanBoard`,
:class:`.TriobanBoard`, :class:`.OctobanBoard` and :class:`.HexobanBoard`. All
implemented boards support having multiple pushers (``Multiban`` game variant).

Constructing an instance of board is as easy as:

.. code-block:: python

    >>> from sokoenginepy import SokobanBoard
    >>> board = SokobanBoard(board_str='\n'.join([
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

All boards implement rich API that allows editing individual board cells,
resizing and exploring neighboring positions. Positions are expressed as 1D
array indexes which can be retrieved fro 2D coordinates using :func:`.index_1d`

.. code-block:: python

    >>> from sokoenginepy import BoardCell, Direction
    >>> from sokoenginepy.utilities import index_1d
    >>> position = index_1d(11, 8, board.width)
    >>>
    >>> board[position]
    BoardCell('@')
    >>> print(board[position])
    @
    >>> board[position] = BoardCell.Characters.BOX
    >>> board[position]
    BoardCell('$')
    >>> board[position].has_pusher
    False
    >>> board[position].has_box
    True
    >>> board[position].put_pusher()
    BoardCell('@')
    >>> board.neighbor(position, Direction.RIGHT)
    164

Besides editing individual cells, all boards also support resizing, path
searching, etc...

Board state
^^^^^^^^^^^

To track changes of piece positions and allow efficient implementation of game
mechanics, we can attach instance of :class:`.HashedBoardState` to our board.

.. code-block:: python

    >>> from sokoenginepy import HashedBoardState
    >>> state = HashedBoardState(board)
    >>> state
    HashedBoardState(SokobanBoard(board_str='\n'.join([
        '    #####',
        '    #  @#',
        '    #$  #',
        '  ###  $##',
        '  #  $ $ #',
        '### # ## #   ######',
        '#   # ## #####  ..#',
        '# $  $          ..#',
        '##### ### #@##  ..#',
        '    #     #########',
        '    #######'
    ])))

This class memoizes positions of pushers and boxes and assigns numerical IDs to
them so they can be referred to in different contexts.

.. code-block:: python

    >>> from sokoenginepy import DEFAULT_PIECE_ID
    >>> state.pushers_ids
    [1, 2]
    >>> state.pushers_positions
    {1: 26, 2: 163}
    >>> state.has_pusher(42)
    False
    >>> state.has_pusher_on(163)
    True
    >>> state.pusher_position(DEFAULT_PIECE_ID)
    26
    >>> state.box_position(DEFAULT_PIECE_ID + 2)
    81

Now that we have a way to refer to individual pushers, boxes and goals, we can
also use Sokoban+ strings which changes end game conditions:

.. code-block:: python

    >>> state.boxorder = '1 3 2'
    >>> state.goalorder = '3 2 1'
    >>> state.enable_sokoban_plus()
    >>> state.is_sokoban_plus_enabled
    True
    >>> state.is_sokoban_plus_valid
    True

Above code block means that pieces get following Sokoban+ IDs:

+----------------------+-----------------+------------------+
| box/goal ID          | box Sokoban+ ID | goal Sokoban+ ID |
+----------------------+-----------------+------------------+
| DEFAULT_PIECE_ID     |        1        |         3        |
+----------------------+-----------------+------------------+
| DEFAULT_PIECE_ID + 1 |        3        |         2        |
+----------------------+-----------------+------------------+
| DEFAULT_PIECE_ID + 2 |        2        |         1        |
+----------------------+-----------------+------------------+

And board is solved only when matching Sokoban+ ids are paired.

The last thing that :class:`.HashedBoardState` does is Zobrist hashing of board.
This is mainly useful for implementing game solvers.

Movement
^^^^^^^^

Although it is necessary to understand how board elements are managed,
:class:`.HashedBoardState` is not suitable for end-game clients because it
doesn't actually implement any game rules. For this task, there is a
:class:`.Mover`. :class:`.Mover` is attached to board to implement all supported
game mechanics like this:

.. code-block:: python

    >>> from sokoenginepy import Mover, SolvingMode
    >>> from sokoenginepy.exceptions import IllegalMoveError
    >>>
    >>> # regular, forward solving mode
    >>> forward_mover = Mover(board)
    >>> # select pusher that will perform movement
    >>> forward_mover.select_pusher(DEFAULT_PIECE_ID + 1)
    >>> # perform movement
    >>> forward_mover.move(Direction.UP)
    >>> # try to perform illegal move raises CellAlreadyOccupiedError
    >>> try:
    ...     forward_mover.move(Direction.UP)
    ... except IllegalMoveError:
    ...     print("IllegalMoveError risen!")
    ...
    IllegalMoveError risen!

    >>> # reverse solving mode
    >>> board = SokobanBoard(board_str="""
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
    >>> print(reverse_mover.board)
        #####
        #  @#
        #.  #
      ###  .##
      #  . . #
    ### # ## #   ######
    #   # ## #####  $$#
    # .  .          $$#
    ##### ### #@##  $$#
        #     #########
        #######

    >>> # Sokoban+
    >>> reverse_mover.state.boxorder = '1 3 2'
    >>> reverse_mover.state.goalorder = '3 2 1'
    >>> reverse_mover.state.enable_sokoban_plus()
    >>>
    >>> # This check also considers if Sokoban+ is enabled...
    >>> reverse_mover.state.is_solved()
    False

:class:`.Mover` implements all ``Sokoban``, ``Sokoban+`` and other variants game
mechanics. It still lacks full game features like recording unlimited undo/redo
etc... This is by design: :class:`.Mover` is intended to be used by either full
game implementation or by solvers. It provides minimal memory footprint and
concentrates on being as fast as possible but sacrificing recording of game
history and maybe few other full game features.

Recording of game history and full game implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`.Snapshot` is used for recording full game history.

TODO: More info here when implementation is finished

Reading and writing Sokoban files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`.Puzzle` and :class:`.PuzzlesCollection` are collections of strings
representing boards, snapshots and meta data like author or title.
These classes are intermediate results of parsing Sokoban files.

This intermediary data is faster to manipulate and less memory hungry than full
game board and game snapshot. That way it is possible to efficiently and quickly
load, store and manipulate whole puzzle collections in memory. On the other
hand, :class:`.Puzzle` and :class:`.PuzzleSnapshot` can be easily converted to
:class:`.VariantBoard` and :class:`.Snapshot` when needed.

.. code-block:: python

    from sokoenginepy import PuzzlesCollection

    collection = PuzzlesCollection()
    collection.load("~/sokoban/collections/fabulous_sokoban_problems.sok")

    board = collection[0].to_game_board()
    # => SokobanBoard

    snapshot = collection[0].snapshots[0].to_game_snapshot()
    # => Snapshot

    # After board editing or game play...

    collection[0].snapshots[0].moves = str(some_recorded_snapshot)
    collection[0].board = str(some_edited_board)

To control output options (ie. line breaks, RLE encoding, etc...) use
:mod:`.settings`.
