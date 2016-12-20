import operator
import time
from copy import deepcopy
from enum import IntEnum
from functools import reduce
from textwrap import dedent

from cached_property import cached_property

from sokoenginepy import (Direction, HashedBoardState, Mover, SokobanBoard,
                          SolvingMode, settings)

settings.OUTPUT_BOARDS_WITH_VISIBLE_FLOORS = False


class BoardType(IntEnum):
    SMALL = 1
    LARGE = 2

    @property
    def board(self):
        if self == self.SMALL:
            return SokobanBoard(board_str=dedent("""
                ##########
                #      **#
                #      **#
                # *@   **#
                #      **#
                ##########
            """[1:-1]))
        else:
            return SokobanBoard(board_str=dedent("""
                ######################################
                #************************************#
                #************************************#
                #************************************#
                #************************************#
                #************************************#
                #************************************#
                #************************************#
                #************************************#
                #************************************#
                #*************          *************#
                #*************          *************#
                #*************          *************#
                #*************    *@    *************#
                #*************          *************#
                #*************          *************#
                #*************          *************#
                #************************************#
                #************************************#
                #************************************#
                #************************************#
                #************************************#
                #************************************#
                #************************************#
                ######################################
            """[1:-1]))


class BenchmarkType(IntEnum):
    FORWARD_MOVE = 0
    REVERSE_MOVE = 1

    @property
    def is_reverse(self):
        return self == self.REVERSE_MOVE

    @property
    def title(self):
        return self.name.replace('_', ' ').lower().title()

    @property
    def direction(self):
        if self == self.FORWARD_MOVE:
            return Direction.LEFT
        else:
            return Direction.RIGHT


class MovementBenchmark:
    def __init__(self, board_type, benchmark_type, moves_count):
        self.milliseconds_used = 0
        self.board_type = board_type
        self.benchmark_type = benchmark_type
        self.moves_count = moves_count
        self.mover = Mover(
            self.board_type.board,
            (
                SolvingMode.REVERSE
                if self.benchmark_type.is_reverse
                else SolvingMode.FORWARD
            )
        )
        self.mover.pulls_boxes = True
        self.start_time = None
        self.end_time = None

    @property
    def speed(self):
        return self.moves_count / (self.milliseconds_used * 1000)

    def run(self):
        self.start_time = time.perf_counter()
        undo_move = False
        for i in range(0, int(self.moves_count)):
            if undo_move:
                self.mover.undo()
                undo_move = False
            else:
                self.mover.move(self.benchmark_type.direction)
                undo_move = True
        self.end_time = time.perf_counter()
        self.milliseconds_used = (self.end_time - self.start_time) * 1000


class MovementBenchmarkPrinter:
    def __init__(self, runs_count, moves_per_run_count):
        self.runs_count = runs_count
        self.moves_per_run_count = moves_per_run_count
        self.benchmarker = None

    def board_header(self, board_type):
        benchmarker = MovementBenchmark(
            board_type, BenchmarkType.FORWARD_MOVE, 1
        )

        return '{:<10} W:{:<5} H:{:<5} P:{:<5} B:{:<5}'.format(
            "Board: ",
            benchmarker.mover.board.width,
            benchmarker.mover.board.height,
            benchmarker.mover.state.pushers_count,
            benchmarker.mover.state.boxes_count
        ) + "\n" + str(benchmarker.mover.board) + "Moves count: {0}".format(
            self.moves_per_run_count
        )

    def run_and_print_experiment(
        self, board_type, benchmark_type, pivot_speed=None
    ):
        speeds = []
        moves = []

        print("{:<20}: ".format(benchmark_type.title), end='', flush=True)

        for i in range(0, self.runs_count):
            self.benchmarker = MovementBenchmark(
                board_type, benchmark_type, self.moves_per_run_count
            )
            self.benchmarker.run()
            speeds.append(self.benchmarker.speed)
            moves.append(self.benchmarker.moves_count)
            print('.', end='', flush=True)

        mean_speed = reduce(operator.add, speeds, 0.0) / len(speeds)
        print(" {:.2E} [moves/s]".format(mean_speed), end='', flush=True)

        if pivot_speed:
            print("  {0:.2f}%".format(mean_speed / pivot_speed * 100))
        else:
            print("  100.00%")

        return mean_speed

    @classmethod
    def run_all(cls):
        print("--------------------------------------------------")
        print("--              MOVER BENCHMARKS                --")
        print("--------------------------------------------------")

        runs = 10
        moves_per_run = 3e3

        printer = MovementBenchmarkPrinter(runs, moves_per_run)
        print(printer.board_header(BoardType.SMALL))

        pivot_speed = printer.run_and_print_experiment(
            BoardType.SMALL, BenchmarkType.FORWARD_MOVE
        )
        printer.run_and_print_experiment(
            BoardType.SMALL, BenchmarkType.REVERSE_MOVE, pivot_speed
        )


if __name__ == "__main__":
    MovementBenchmarkPrinter.run_all()
