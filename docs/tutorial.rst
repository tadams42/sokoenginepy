Tutorial
--------

Game board
^^^^^^^^^^

For each implemented board tessellation, there is a game board class. Variants
are enumarated by :class:`.Variant` and board classes are :class:`.SokobanBoard`,
:class:`.TriobanBoard`, :class:`.OctobanBoard` and :class:`.HexobanBoard`. All
implemented boards support having multiple pushers (``Multiban`` game variant).

Contructing an instance of board is as easy as:

.. code-block:: python

    from sokoenginepy import SokobanBoard

    board = SokobanBoard(board_str="""
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
    """[1:-1])

All boards implement rich API that allows editing individual board cells,
resizing and exploring neigbouring positions. Positions are expressed as 1D
array indexes which can be retreived fro 2D coordinates using :func:`.index_1d`

.. code-block:: python

    from sokoenginepy import BoardCell, index_1d, BoardCharacters, Direction

    position = index_1d(11, 8, board.width)

    board[position]
    # => BoardCell(BoardCharacters.PUSHER)
    print(board[position])
    # => @

    board[position] = BoardCharacters.BOX
    print(board[position])
    # => $

    board[position].has_pusher
    # => False
    board[position].has_box
    # => True

    board[position].put_pusher()
    print(board[position])
    # => @

    board.neighbor(position, Direction.RIGHT)
    # => 164

Except editing individual cells, all boards also support resizing, path
searching, etc... For details see :class:`.VariantBoard` or any of subclasses.

Board state
^^^^^^^^^^^

To track changes of piece positions and allow efficient implementation of game
mechanics, we can attach instance of :class:`.HashedBoardState` to our board.

.. code-block:: python

    from sokoenginepy import HashedBoardState

    state = HashedBoardState(board)

Now we have efficient means to inspect positions of pushers, boxes and goals.
To understand how this works, we need to have a way  if identifying individual
pushers, boxes and goals. :class:`.HashedBoardState` does that by assigning
ID to individual pieces. This ID can then be used to refer to individual piece.

IDs are assigned by simply counting from top left corner of board, starting with
:data:`.DEFAULT_PIECE_ID`

.. image:: /images/assigning_ids.png
    :alt: Assigning board elements' IDs

Having IDs of elements, we can refer them through :class:`.HashedBoardState`

.. code-block:: python

    from sokoenginepy import DEFAULT_PIECE_ID

    state.pusher_position(DEFAULT_PIECE_ID)
    # => 26

    state.box_position(DEFAULT_PIECE_ID + 2)
    # => 81

Once we have tracking of piece positions, it is also possible to move them:

.. code-block:: python

    state.move_pusher(DEFAULT_PIECE_ID, Direction.RIGHT)

Movement preserves IDs of pieces. This is best ilustrated by following:

+----------------------------------------------+----------------------------------------------+----------------------------------------------+
| 1) Initial board                             | 2) Edited board                              | 3) Box moved                                 |
+----------------------------------------------+----------------------------------------------+----------------------------------------------+
| .. image:: /images/movement_vs_transfer1.png | .. image:: /images/movement_vs_transfer2.png | .. image:: /images/movement_vs_transfer3.png |
+----------------------------------------------+----------------------------------------------+----------------------------------------------+

Using :class:`.HashedBoardState`, we can also manage Sokoban+.

.. code-block:: python

    state.boxorder = '1 3 2'
    state.goalorder = '3 2 1'
    state.is_sokoban_plus_enabled = True

The last thing that :class:`.HashedBoardState` does is Zobrist hashing of board.
This is mainly usefull for implementing game solvers.

Movement
^^^^^^^^

Although it is necessary to understand how board elements are managed,
:class:`.HashedBoardState` is not suitable for end-game clients because it
doesn't actually implement any game rules. For this task, there is a
:class:`.Mover`. :class:`.Mover` is attached to board to implement all supported
game mechanics like this:

.. code-block:: python

    from sokoenginepy import Mover, GameSolvingMode

    # regular, forward solving mode
    forward_mover = Mover(board)
    # select pusher that will perform movement
    forward_mover.selected_pusher = DEFAULT_PIECE_ID + 1
    # perform movement
    forward_mover.move(Direction.UP)
    # try to perform illegal move
    forward_mover.move(Direction.UP)
    # rises IllegalMoveError

    # reverse solving mode
    board = SokobanBoard(board_str="""
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
    """[1:-1])
    reverse_mover = Mover(board, GameSolvingMode.REVERSE)

    print(reverse_mover.board)
    #     #####
    #     #  @#
    #     #.  #
    #   ###  .##
    #   #  . . #
    # ### # ## #   ######
    # #   # ## #####  $$#
    # # .  .          $$#
    # ##### ### #@##  $$#
    #     #     #########
    #     #######

    # Sokoban+
    reverse_mover.state.boxorder = '1 3 2'
    reverse_mover.state.goalorder = '3 2 1'
    reverse_mover.state.is_sokoban_plus_enabled = True

    # This check also considers if Sokoban+ is enabled...
    reverse_mover.state.is_solved
    # => False

:class:`.Mover` implements all ``Sokoban``, ``Sokoban+`` and other variants game
mechanics. It still lacks full game features like recording unlimited undo/redo
etc... This is by design: :class:`.Mover` is intended to be used by either full
game implementation or by solvers. It provides minimal memory footprint and
concentrates on being as fast as possible but sacrifficing reocrding of game
history.

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
game board an game snapshot. That way it is possible to efficiently and quickly
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

To controll output options (ie. line breaks, RLE encoding, etc...) use
:data:`.OUTPUT_SETTINGS`.
