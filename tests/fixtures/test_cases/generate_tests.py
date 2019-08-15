#!/usr/bin/env python

# Requires: 'pyexcel-ods3 >= 0.2.0',

import os
import textwrap
from collections import OrderedDict
from inspect import getsourcefile
from string import Template

from pyexcel_ods3 import get_data

# Directory where this file is found
basedir = os.path.abspath(os.path.join(getsourcefile(lambda: 0), ".."))
SOURCE_ROOT = os.path.abspath(os.path.join(basedir, "..", "..", ".."))
TESTS_DIR = os.path.abspath(os.path.join(SOURCE_ROOT, "tests"))
RES_DIR = os.path.abspath(os.path.join(TESTS_DIR, "fixtures"))
TEST_CASES_DIR = os.path.abspath(os.path.join(RES_DIR, "test_cases"))
BOARD_TESTS_DIR = os.path.abspath(os.path.join(TESTS_DIR, "board"))
TESSELLATION_TESTS_DIR = os.path.abspath(os.path.join(TESTS_DIR, "tessellation"))


class SpecGenerator:
    VARIANTS = ["sokoban", "trioban", "hexoban", "octoban"]
    TEST_TYPES = ["board", "tessellation"]

    DIRECTIONS = ["l", "r", "u", "d", "nw", "sw", "ne", "se"]
    DIRECTIONS_HASH = dict(
        zip(
            DIRECTIONS,
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
    RESULTS_HASH = dict(zip(DIRECTIONS, ["result_{0}".format(d) for d in DIRECTIONS]))

    def generate(self):
        self.write_header()

        for variant in type(self).VARIANTS:
            print("Generating test cases for {0}...".format(variant))
            test_cases = self.get_test_cases(variant)

            for test_type in self.TEST_TYPES:
                self.output = []
                self.generate_test_class(variant, test_type)
                for test_case in test_cases:
                    test_case["test_type"] = test_type
                    self.generate_test_case_output(test_case)

                if test_type == "board":
                    with open(str(self.board_output_file_path), "a") as f:
                        for line in self.output:
                            f.write(line)
                        f.write("\n")
                else:
                    with open(str(self.tessellation_output_file_path), "a") as f:
                        for line in self.output:
                            f.write(line)
                        f.write("\n")

    def write_header(self):
        s = """
            # Generated by generate_tests.py using data from fixtures/test_cases
            import pytest

            from sokoenginepy import (CellOrientation, Direction, HexobanBoard,
                                      OctobanBoard, SokobanBoard, Tessellation,
                                      TriobanBoard)
            from sokoenginepy.utilities import index_1d, is_on_board_1d


            def triangle_points_down(position, board_width, board_height):
                return Tessellation.TRIOBAN.value.cell_orientation(
                    position, board_width, board_height
                ) == CellOrientation.TRIANGLE_DOWN


            def is_octagon(position, board_width, board_height):
                return Tessellation.OCTOBAN.value.cell_orientation(
                    position, board_width, board_height
                ) == CellOrientation.OCTAGON
        """

        with open(str(self.board_output_file_path), "w") as f:
            f.write(textwrap.dedent(s).strip() + "\n\n\n")

        with open(str(self.tessellation_output_file_path), "w") as f:
            f.write(textwrap.dedent(s).strip() + "\n\n\n")

    def get_test_cases(self, variant):
        data = get_data(str(self.input_file_path(variant)))
        sheet1 = data[list(data.keys())[0]]
        rows = [row[:12] for row in sheet1 if len(row) > 0 and len(row[0]) > 0]
        header = rows[0]
        raw_cases = [OrderedDict(zip(header, row)) for row in rows[1:]]

        cases = []
        for case in raw_cases:
            case["variant"] = variant
            case["width"] = int(case["board_dimensions"].split(",")[0].strip())
            case["height"] = int(case["board_dimensions"].split(",")[1].strip())
            case["row"] = int(case["test_position"].split(",")[1].strip())
            case["column"] = int(case["test_position"].split(",")[0].strip())
            cases.append(case)

        return cases

    def generate_test_class(self, variant, test_type):
        s = """
            class {0}{1}AutogeneratedSpecMixin:
                class Describe_neighbor_position:
        """.format(
            variant.capitalize(), test_type.capitalize()
        )
        self.output.append(textwrap.dedent(s).strip() + "\n")

    def generate_test_case_output(self, test_case):
        s = Template(
            """
            def test_autogenerated_$test_name(self):
                width = $width
                height = $height
                row = $row
                column = $column
                index = index_1d(column, row, width)
        """
        ).substitute(
            test_name=test_case["test_name"],
            width=test_case["width"],
            height=test_case["height"],
            row=test_case["row"],
            column=test_case["column"],
        )
        self.output.append(
            textwrap.indent(textwrap.dedent(s).strip() + "\n", prefix="        ")
        )

        if test_case["test_type"] == "tessellation":
            self.output.append(
                '            t = Tessellation.instance_from("{0}").value'.format(
                    test_case["variant"]
                )
            )
        else:
            self.output.append(
                "            b = {0}Board(width, height)".format(
                    test_case["variant"].capitalize()
                )
            )
        self.output.append("\n")

        if test_case["test_position_requrement"] != "nil":
            self.output.append("\n")
            self.output.append(
                "            assert {0}".format(
                    test_case["test_position_requrement"]
                    .replace("&&", "and")
                    .replace("||", "or")
                    .replace("!", "not ")
                )
            )
            self.output.append("\n\n")
        else:
            self.output.append("\n")

        for direction in self.DIRECTIONS:
            if test_case["test_type"] == "tessellation":
                if self.is_result_illegal_position(test_case, direction):
                    s = """
                        assert not is_on_board_1d(t.neighbor_position(index, {0}, width, height), width, height)
                    """.format(
                        self.DIRECTIONS_HASH[direction]
                    )

                elif self.is_result_illegal_direction(test_case, direction):
                    s = """
                        with pytest.raises(ValueError):
                            t.neighbor_position(index, {0}, width, height)
                    """.format(
                        self.DIRECTIONS_HASH[direction]
                    )
                else:
                    s = """
                        assert t.neighbor_position(index, {0}, width, height) == index_1d({1}, width)
                    """.format(
                        self.DIRECTIONS_HASH[direction],
                        test_case[self.RESULTS_HASH[direction]],
                    )
            else:
                if self.is_result_illegal_position(
                    test_case, direction
                ) or self.is_result_illegal_direction(test_case, direction):
                    s = """
                        assert not is_on_board_1d(b.neighbor(index, {0}), width, height)
                    """.format(
                        self.DIRECTIONS_HASH[direction]
                    )
                else:
                    s = """
                        assert b.neighbor(index, {0}) == index_1d({1}, width)
                    """.format(
                        self.DIRECTIONS_HASH[direction],
                        test_case[self.RESULTS_HASH[direction]],
                    )

            self.output.append(
                textwrap.indent(
                    textwrap.dedent(s).strip() + "\n", prefix="            "
                )
            )

        self.output.append("\n")

    def input_file_path(self, variant):
        return os.path.join(
            TEST_CASES_DIR, "{0}_test_cases.ods".format(variant.strip().lower())
        )

    @property
    def board_output_file_path(self):
        return os.path.join(BOARD_TESTS_DIR, "autogenerated_board.py")

    @property
    def tessellation_output_file_path(self):
        return os.path.join(TESSELLATION_TESTS_DIR, "autogenerated_tessellation.py")

    def is_result_illegal_direction(self, test_case, direction):
        return test_case[self.RESULTS_HASH[direction]] == "IllegalDirection"

    def is_result_illegal_position(self, test_case, direction):
        return test_case[self.RESULTS_HASH[direction]] == "OfBoardPosition"


def main():
    generator = SpecGenerator()
    generator.generate()


if __name__ == "__main__":
    main()
