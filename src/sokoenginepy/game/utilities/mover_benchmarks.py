from __future__ import annotations

import enum
import operator
import textwrap
import time
from enum import IntEnum
from functools import reduce

from sokoenginepy.game import BoardGraph, Direction, Mover, SolvingMode
from sokoenginepy.io import SokobanPuzzle


class BoardType(IntEnum):
    SMALL = 1
    LARGE = 2

    @property
    def puzzle(self) -> SokobanPuzzle:
        if self == self.SMALL:
            data = """
                ##########
                #      **#
                #      **#
                # *@   **#
                #      **#
                ##########
            """
            data = textwrap.dedent(data.lstrip("\n").rstrip())
            return SokobanPuzzle(board=data)
        else:
            data = """
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
            """
            return SokobanPuzzle(board=data)


class BenchmarkType(enum.Enum):
    FORWARD_MOVER = Direction.LEFT
    REVERSE_MOVER = Direction.RIGHT

    @property
    def is_reverse(self) -> bool:
        return self == self.REVERSE_MOVER

    @property
    def title(self) -> str:
        return self.name.replace("_", " ").lower().title()


class MovementBenchmark:
    def __init__(
        self, board_type: BoardType, benchmark_type: BenchmarkType, moves_count: int
    ):
        self.milliseconds_used = 0
        self.board_type = board_type
        self.benchmark_type = benchmark_type
        self.moves_count = moves_count
        self.puzzle = self.board_type.puzzle
        self.graph = BoardGraph(self.puzzle)

        self.mover = Mover(
            self.graph,
            (
                SolvingMode.REVERSE
                if self.benchmark_type.is_reverse
                else SolvingMode.FORWARD
            ),
        )
        self.mover.pulls_boxes = True

    @property
    def moves_per_second(self) -> float:
        return self.moves_count / (self.milliseconds_used / 1000)

    def run(self):
        total_time = 0
        undo_move = False
        for i in range(0, int(self.moves_count)):
            if undo_move:
                start_time = time.perf_counter()
                self.mover.undo_last_move()
                end_time = time.perf_counter()
                total_time += end_time - start_time
                undo_move = False
            else:
                start_time = time.perf_counter()
                self.mover.move(self.benchmark_type.value)
                end_time = time.perf_counter()
                total_time += end_time - start_time
                undo_move = True

        self.milliseconds_used = total_time * 1000


class MovementBenchmarkPrinter:
    def __init__(self, runs_count: int, moves_per_run_count: int):
        self.runs_count = runs_count
        self.moves_per_run_count = moves_per_run_count

    def board_header(self, board_type):
        benchmarker = MovementBenchmark(board_type, BenchmarkType.FORWARD_MOVER, 1)

        return (
            "{:<10} W:{:<5} H:{:<5} P:{:<5} B:{:<5}".format(
                "Board: ",
                benchmarker.puzzle.width,
                benchmarker.puzzle.height,
                benchmarker.mover.board_manager.pushers_count,
                benchmarker.mover.board_manager.boxes_count,
            )
            + "\n"
            + str(benchmarker.mover.board)
            + "\nMoves count: {0}".format(self.moves_per_run_count)
        )

    def run_and_print_experiment(
        self, board_type: BoardType, benchmark_type: BenchmarkType, pivot_speed=None
    ):
        speeds = []
        times = []

        print("{:<20}: ".format(benchmark_type.title), end="", flush=True)

        for i in range(0, self.runs_count):
            benchmarker = MovementBenchmark(
                board_type, benchmark_type, self.moves_per_run_count
            )
            benchmarker.run()
            speeds.append(benchmarker.moves_per_second)
            times.append(benchmarker.milliseconds_used)
            print(".", end="", flush=True)

        mean_speed = reduce(operator.add, speeds, 0.0) / len(speeds)
        mean_time = reduce(operator.add, times, 0.0) / len(times)
        print(
            " {:.2f} [ms] {:.2e} [moves/s]".format(mean_time, mean_speed),
            end="",
            flush=True,
        )

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

        native_extension_available = True
        try:
            import sokoenginepyext
        except ImportError:
            native_extension_available = False

        if native_extension_available:
            runs = 10
            moves_per_run = 3e5
        else:
            runs = 10
            moves_per_run = 3e4

        printer = MovementBenchmarkPrinter(runs, int(moves_per_run))
        print(printer.board_header(BoardType.SMALL))

        # Speed of early, not thoroughly tested, C++ only implementation
        pivot_speed = 3e6

        printer.run_and_print_experiment(
            BoardType.SMALL, BenchmarkType.FORWARD_MOVER, pivot_speed
        )
        printer.run_and_print_experiment(
            BoardType.SMALL, BenchmarkType.REVERSE_MOVER, pivot_speed
        )


def run_benchmarks():
    return MovementBenchmarkPrinter.run_all()
