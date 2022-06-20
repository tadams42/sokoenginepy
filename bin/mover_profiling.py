import cProfile
from textwrap import dedent

from sokoenginepy.game import BoardGraph, Direction, Mover
from sokoenginepy.io import SokobanPuzzle

puzzle = SokobanPuzzle(
    board=dedent(
        """
    ###########
    #       **#
    #       **#
    #  *@   **#
    #       **#
    ###########
"""[
            1:-1
        ]
    )
)
board = BoardGraph(puzzle)

mover = Mover(board)

moves_cycle = 3000 * [
    Direction.LEFT,
    Direction.DOWN,
    Direction.LEFT,
    Direction.LEFT,
    Direction.UP,
    Direction.RIGHT,
    Direction.DOWN,
    Direction.RIGHT,
    Direction.RIGHT,
    Direction.UP,
]


def moves_profile():
    for d in moves_cycle:
        mover.move(d)


def single_move_profile():
    mover.move(Direction.LEFT)


def single_moves_cycle_profile():
    moves_cycle = [
        Direction.LEFT,
        Direction.DOWN,
        Direction.LEFT,
        Direction.LEFT,
        Direction.UP,
        Direction.RIGHT,
        Direction.DOWN,
        Direction.RIGHT,
        Direction.RIGHT,
        Direction.UP,
    ]
    for d in moves_cycle:
        mover.move(d)


# if __name__ == "__main__":
#     single_moves_cycle_profile()

cProfile.run("single_moves_cycle_profile()", "moves_profile.prof")
cProfile.run("mover.move(Direction.LEFT)", "single_move_profile.prof")

# pip install pyprof2calltree
# python bin/mover_profiling.py
# pyprof2calltree -i moves_profile.prof
# pyprof2calltree -i single_move_profile.prof
# kcachegrind moves_profile.prof.log
# kcachegrind single_move_profile.prof.log
