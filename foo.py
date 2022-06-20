import textwrap

from sokoenginepy.game import BoardGraph, BoardManager, Config, Direction, Mover
from sokoenginepy.io import SokobanPuzzle

data = textwrap.dedent(
    """
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
"""
)
puzzle = SokobanPuzzle(board=data)
board = BoardGraph(puzzle)
manager = BoardManager(board)

breakpoint()
