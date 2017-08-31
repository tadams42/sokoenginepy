TODO
====

Misc
----

- Should these pass Sokoban+ validation (for board with 3 boxes)? ::

    goalorder = "1 2"
    boxorder = "1 2 3"

- ``Puzzle``
    - parsing should work properly with empty boards and should allow empty interior rows (SokobanYASC file format v0.17) - test this
- ``Hexoban``
    - board resizing implementation is smelly
    - re-check test patterns for these, draw new ones and adjust implementation
- Full ``Game`` implementation
- refactor I/O modules, maybe implement ``.sok`` stream instead of read/write

Solver / Utilities
------------------

- most solver concepts and techniques should be `Tessellation` independent but: deadlock detection is `Tessellation` dependent: it relies on patterns in  layout which are different for different tessellations
- implement reverse solution snapshot to forward solution snapshot conversion
- implement create board from solution snapshot
- genetic algorithm states search (as in YASS) would be fun to implement
- game board similarity tool ie. it detects that ie. all following boards are 100% similar ::

    """
    ######   ######   ######   ######
    #@ $.#   # @$.#   #  $.#   #  $.#
    #  $.#   #  $.#   #@ $.#   # @$.#
    ######   ######   ######   ######
    """
