import cProfile
from textwrap import dedent

from sokoenginepy import Direction, Mover, SokobanBoard

board = SokobanBoard(board_str=dedent("""
    ###########
    #       **#
    #       **#
    #  *@   **#
    #       **#
    ###########
"""[1:-1]))

mover = Mover(board)

moves_cycle =  3000 * [
    Direction.LEFT, Direction.DOWN, Direction.LEFT, Direction.LEFT,
    Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.RIGHT,
    Direction.RIGHT, Direction.UP
]

def main():
    for d in moves_cycle:
        mover.move(d)

# if __name__ == "__main__":
#     main()

cProfile.run('main()', 'mover_profiling.prof')

# python scripts/mover_profiling.py
# pyprof2calltree -i mover_profiling.prof
# kcachegrind mover_profiling.prof.log
