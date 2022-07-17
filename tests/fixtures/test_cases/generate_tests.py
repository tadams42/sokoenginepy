#!/usr/bin/env python

import os
import textwrap
from collections import OrderedDict
from pathlib import Path

from pyexcel_ods3 import get_data

_SELF_DIR = Path(__file__).parent.absolute().resolve()
SOURCE_ROOT = (_SELF_DIR / ".." / ".." / "..").resolve()
TESTS_DIR = SOURCE_ROOT / "tests"
RES_DIR = TESTS_DIR / "fixtures"
TEST_CASES_DIR = RES_DIR / "test_cases"
BOARD_TESTS_DIR = TESTS_DIR / "io"
TESSELLATION_TESTS_DIR = TESTS_DIR / "game"


class SpecGenerator:
    TESSELLATIONS = ["sokoban", "trioban", "hexoban", "octoban"]
    DIRECTION_NAMES = ["l", "r", "u", "d", "nw", "sw", "ne", "se"]
    DIRECTIONS = dict(
        zip(
            DIRECTION_NAMES,
            [
                "Direction.LEFT",
                "Direction.RIGHT",
                "Direction.UP",
                "Direction.DOWN",
                "Direction.NORTH_WEST",
                "Direction.SOUTH_WEST",
                "Direction.NORTH_EAST",
                "Direction.SOUTH_EAST",
            ],
        )
    )
    RESULTS = dict(
        zip(DIRECTION_NAMES, ["result_{0}".format(d) for d in DIRECTION_NAMES])
    )

    def generate(self):
        for tessellation in self.TESSELLATIONS:
            print(f"Generating test cases for {tessellation}...")

            self.write_header(tessellation)

            test_cases = self.get_test_cases(tessellation)

            self.output = []
            self.generate_test_class(tessellation)
            for test_case in test_cases:
                self.generate_test_case_output(test_case)

            with open(str(self.output_file_path(tessellation)), "a") as f:
                for line in self.output:
                    f.write(line)
                f.write("\n")

    def write_header(self, tessellation: str):
        s = """
        from sokoenginepy import (
            BoardGraph,
            CellOrientation,
            Config,
            Direction,
            Puzzle,
            Tessellation,
            index_1d,
            is_on_board_1d,
        )
        """

        trio = """
        def triangle_points_down(board_graph, position):
            return (
                board_graph.cell_orientation(position) == CellOrientation.TRIANGLE_DOWN
            )
        """

        octo = """
        def is_octagon(board_graph, position):
            return board_graph.cell_orientation(position) == CellOrientation.OCTAGON
        """

        if tessellation == "trioban":
            s += trio
        elif tessellation == "octoban":
            s += octo

        with open(str(self.output_file_path(tessellation)), "w") as f:
            f.write(textwrap.dedent(s).strip() + "\n\n\n")

    def get_test_cases(self, tessellation):
        data = get_data(str(self.input_file_path(tessellation)))
        sheet1 = data[list(data.keys())[0]]
        rows = [row[:12] for row in sheet1 if len(row) > 0 and len(row[0]) > 0]
        header = rows[0]
        raw_cases = [OrderedDict(zip(header, row)) for row in rows[1:]]

        cases = []
        for case in raw_cases:
            case["tessellation"] = tessellation
            case["width"] = int(case["board_dimensions"].split(",")[0].strip())
            case["height"] = int(case["board_dimensions"].split(",")[1].strip())
            case["row"] = int(case["test_position"].split(",")[1].strip())
            case["column"] = int(case["test_position"].split(",")[0].strip())
            cases.append(case)

        return cases

    def generate_test_class(self, tessellation: str):
        s = f"""
        class Describe{tessellation.capitalize()}BoardGraph:
            class describe_neighbor_position:
        """
        self.output.append(textwrap.dedent(s).strip() + "\n")

    def generate_test_case_output(self, test_case):
        s = f"""
        def test_generated_{test_case['test_name']}(self):
            width = {test_case['width']}
            height = {test_case['height']}
            row = {test_case['row']}
            column = {test_case['column']}
            puzzle = Puzzle(Tessellation.{test_case['tessellation'].upper()}, width, height)
            g = BoardGraph(puzzle)
            index = index_1d(column, row, width)
        """
        self.output.append(
            textwrap.indent(textwrap.dedent(s).strip() + "\n", prefix="        ")
        )

        if test_case["test_position_requirement"] != "nil":
            self.output.append("\n")
            self.output.append(
                "            assert {0}".format(
                    test_case["test_position_requirement"]
                    .replace("&&", "and")
                    .replace("||", "or")
                    .replace("!", "not ")
                )
            )
            self.output.append("\n\n")
        else:
            self.output.append("\n")

        for direction in self.DIRECTION_NAMES:
            if self.is_result_illegal_position(test_case, direction):
                s = f"assert not is_on_board_1d(g.neighbor(index, {self.DIRECTIONS[direction]}), width, height)"
            elif self.is_result_illegal_direction(test_case, direction):
                s = f"assert g.neighbor(index, {self.DIRECTIONS[direction]}) == Config.NO_POS"
            else:
                s = (
                    f"assert g.neighbor(index, {self.DIRECTIONS[direction]}) == "
                    f"index_1d({test_case[self.RESULTS[direction]]}, width)"
                )

            self.output.append(
                textwrap.indent(
                    textwrap.dedent(s).strip() + "\n", prefix="            "
                )
            )

        self.output.append("\n")

    def input_file_path(self, tessellation):
        return os.path.join(TEST_CASES_DIR, f"{tessellation}_test_cases.ods")

    def output_file_path(self, tessellation: str):
        return os.path.join(
            TESSELLATION_TESTS_DIR, f"generated_{tessellation}_graph_spec.py"
        )

    def is_result_illegal_direction(self, test_case, direction):
        return test_case[self.RESULTS[direction]] == "IllegalDirection"

    def is_result_illegal_position(self, test_case, direction):
        return test_case[self.RESULTS[direction]] == "OfBoardPosition"


def main():
    generator = SpecGenerator()
    generator.generate()


if __name__ == "__main__":
    main()
