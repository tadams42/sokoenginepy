import os

import pytest

from sokoenginepy import BoardConversionError, HexobanBoard, PuzzlesCollection

from ..test_helpers import TEST_RESOURCES_ROOT
from .autogenerated_board import HexobanBoardAutogeneratedSpecMixin


def load_parser_test_data():
    input_file = os.path.join(
        TEST_RESOURCES_ROOT, "test_data", "hexoban_parser_tests.sok"
    )
    collection = PuzzlesCollection()
    collection.load(input_file)

    retv = {}
    for puzzle in collection.puzzles:
        if (
            puzzle.title == "row_added_type1_top"
            or puzzle.title == "row_added_type2_top"
        ):
            puzzle.board = "-" + puzzle.board[1:]
        if (
            puzzle.title == "row_added_type1_bottom"
            or puzzle.title == "row_added_type2_bottom"
        ):
            puzzle.board = puzzle.board[:-2] + "-" + puzzle.board[-1]

        retv[puzzle.title] = puzzle.board.rstrip()

    return retv


TEST_BOARDS = load_parser_test_data()


class DescribeHexobanBoard(HexobanBoardAutogeneratedSpecMixin):
    def it_raises_on_illegal_scheme(self):
        input = TEST_BOARDS["illegal_scheme1"]
        with pytest.raises(BoardConversionError):
            HexobanBoard(board_str=input)

        input = TEST_BOARDS["illegal_scheme2"]
        with pytest.raises(BoardConversionError):
            HexobanBoard(board_str=input)

    class describe_parser_tests:
        def perform_parser_test(self, input, result, out_width, out_height):
            board = HexobanBoard(board_str=input)
            assert board.to_str(use_visible_floor=True) == result
            assert board == HexobanBoard(board_str=result)
            assert str(board) == str(HexobanBoard(board_str=result))
            assert board.width == out_width
            assert board.height == out_height

        def it_parses_scheme1_type1(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_scheme1_type1"],
                result=TEST_BOARDS["output_scheme1_type1"],
                out_width=10,
                out_height=7,
            )

        def it_parses_scheme2_type1(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_scheme2_type1"],
                result=TEST_BOARDS["output_scheme2_type1"],
                out_width=10,
                out_height=7,
            )

        def it_parses_scheme3_type1(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_scheme3_type1"],
                result=TEST_BOARDS["output_scheme3_type1"],
                out_width=10,
                out_height=7,
            )

        def it_parses_scheme4_type1(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_scheme4_type1"],
                result=TEST_BOARDS["output_scheme4_type1"],
                out_width=10,
                out_height=7,
            )

        def it_parses_scheme1_type2(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_scheme1_type2"],
                result=TEST_BOARDS["output_scheme1_type2"],
                out_width=10,
                out_height=7,
            )

        def it_parses_scheme2_type2(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_scheme2_type2"],
                result=TEST_BOARDS["output_scheme2_type2"],
                out_width=11,
                out_height=7,
            )

        def it_parses_scheme3_type2(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_scheme3_type2"],
                result=TEST_BOARDS["output_scheme3_type2"],
                out_width=10,
                out_height=7,
            )

        def it_parses_scheme4_type2(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_scheme4_type2"],
                result=TEST_BOARDS["output_scheme4_type2"],
                out_width=11,
                out_height=7,
            )

        def it_parses_hexocet_A(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_A"],
                result=TEST_BOARDS["output_hexocet_A"],
                out_width=9,
                out_height=10,
            )

        def it_parses_hexocet_Perfume(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_Perfume"],
                result=TEST_BOARDS["output_hexocet_Perfume"],
                out_width=8,
                out_height=8,
            )

        def it_parses_hexocet_Mud(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_Mud"],
                result=TEST_BOARDS["output_hexocet_Mud"],
                out_width=7,
                out_height=10,
            )

        def it_parses_hexocet_X(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_X"],
                result=TEST_BOARDS["output_hexocet_X"],
                out_width=7,
                out_height=8,
            )

        def it_parses_hexocet_Wildmil(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_Wildmil"],
                result=TEST_BOARDS["output_hexocet_Wildmil"],
                out_width=8,
                out_height=8,
            )

        def it_parses_hexocet_Four(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_Four"],
                result=TEST_BOARDS["output_hexocet_Four"],
                out_width=8,
                out_height=9,
            )

        def it_parses_hexocet_Bird(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_Bird"],
                result=TEST_BOARDS["output_hexocet_Bird"],
                out_width=7,
                out_height=9,
            )

        def it_parses_hexocet_V(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_V"],
                result=TEST_BOARDS["output_hexocet_V"],
                out_width=7,
                out_height=7,
            )

        def it_parses_hexocet_Bridge(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_Bridge"],
                result=TEST_BOARDS["output_hexocet_Bridge"],
                out_width=8,
                out_height=9,
            )

        def it_parses_hexocet_Gun(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_Gun"],
                result=TEST_BOARDS["output_hexocet_Gun"],
                out_width=8,
                out_height=8,
            )

        def it_parses_hexocet_Kite(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_Kite"],
                result=TEST_BOARDS["output_hexocet_Kite"],
                out_width=8,
                out_height=9,
            )

        def it_parses_hexocet_Fed(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_Fed"],
                result=TEST_BOARDS["output_hexocet_Fed"],
                out_width=8,
                out_height=10,
            )

        def it_parses_hexocet_Beetle(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_Beetle"],
                result=TEST_BOARDS["output_hexocet_Beetle"],
                out_width=8,
                out_height=9,
            )

        def it_parses_hexocet_LittleRabbit(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_LittleRabbit"],
                result=TEST_BOARDS["output_hexocet_LittleRabbit"],
                out_width=7,
                out_height=7,
            )

        def it_parses_hexocet_Losange(self):
            self.perform_parser_test(
                input=TEST_BOARDS["input_hexocet_Losange"],
                result=TEST_BOARDS["output_hexocet_Losange"],
                out_width=9,
                out_height=8,
            )

    class describe_row_and_column_reordering:
        def test_reverses_columns_for_boards_type1(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            result = TEST_BOARDS["type1_columns_reversed"]
            board = HexobanBoard(board_str=input)
            board.reverse_columns()
            assert board.to_str(use_visible_floor=True) == result
            assert board.width == 10
            assert board.height == 7

        def test_reverses_columns_for_boards_type2(self):
            input = TEST_BOARDS["input_scheme1_type2"]
            result = TEST_BOARDS["type2_columns_reversed"]
            board = HexobanBoard(board_str=input)
            board.reverse_columns()
            assert board.to_str(use_visible_floor=True) == result
            assert board.width == 11
            assert board.height == 7

        def test_reverses_rows_for_boards_type1(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            result = TEST_BOARDS["type1_rows_reversed"]
            board = HexobanBoard(board_str=input)
            board.reverse_rows()
            assert board.to_str(use_visible_floor=True) == result
            assert board.width == 10
            assert board.height == 7

        def test_reverses_rows_for_boards_type2(self):
            input = TEST_BOARDS["input_scheme1_type2"]
            result = TEST_BOARDS["type2_rows_reversed"]
            board = HexobanBoard(board_str=input)
            board.reverse_rows()
            assert board.to_str(use_visible_floor=True) == result
            assert board.width == 10
            assert board.height == 7

    class describe_board_resizing:
        def test_adds_row_top_type1(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            result = TEST_BOARDS["row_added_type1_top"]
            board = HexobanBoard(board_str=input)
            board.add_row_top()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 8
            assert board.width == 10

        def test_adds_row_top_type2(self):
            input = TEST_BOARDS["input_scheme1_type2"]
            result = TEST_BOARDS["row_added_type2_top"]
            board = HexobanBoard(board_str=input)
            board.add_row_top()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 8
            assert board.width == 11

        def test_adds_row_bottom_type1(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            result = TEST_BOARDS["row_added_type1_bottom"]
            board = HexobanBoard(board_str=input)
            board.add_row_bottom()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 8
            assert board.width == 10

        def test_adds_row_bottom_type2(self):
            input = TEST_BOARDS["input_scheme1_type2"]
            result = TEST_BOARDS["row_added_type2_bottom"]
            board = HexobanBoard(board_str=input)
            board.add_row_bottom()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 8
            assert board.width == 10

        def test_adds_column_left_type1(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            result = TEST_BOARDS["column_added_type1_left"]
            board = HexobanBoard(board_str=input)
            board.add_column_left()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 7
            assert board.width == 11

        def test_adds_column_left_type2(self):
            input = TEST_BOARDS["input_scheme1_type2"]
            result = TEST_BOARDS["column_added_type2_left"]
            board = HexobanBoard(board_str=input)
            board.add_column_left()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 7
            assert board.width == 11

        def test_adds_column_right_type1(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            result = TEST_BOARDS["column_added_type1_right"]
            board = HexobanBoard(board_str=input)
            board.add_column_right()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 7
            assert board.width == 11

        def test_adds_column_right_type2(self):
            input = TEST_BOARDS["input_scheme1_type2"]
            result = TEST_BOARDS["column_added_type2_right"]
            board = HexobanBoard(board_str=input)
            board.add_column_right()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 7
            assert board.width == 11

        def test_removes_row_top_type1(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            result = TEST_BOARDS["row_removed_type1_top"]
            board = HexobanBoard(board_str=input)
            board.remove_row_top()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 6
            assert board.width == 10

        def test_removes_row_top_type2(self):
            input = TEST_BOARDS["input_scheme1_type2"]
            result = TEST_BOARDS["row_removed_type2_top"]
            board = HexobanBoard(board_str=input)
            board.remove_row_top()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 6
            assert board.width == 11

        def test_removes_row_bottom_type1(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            result = TEST_BOARDS["row_removed_type1_bottom"]
            board = HexobanBoard(board_str=input)
            board.remove_row_bottom()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 6
            assert board.width == 10

        def test_removes_row_bottom_type2(self):
            input = TEST_BOARDS["input_scheme1_type2"]
            result = TEST_BOARDS["row_removed_type2_bottom"]
            board = HexobanBoard(board_str=input)
            board.remove_row_bottom()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 6
            assert board.width == 10

        def test_removes_column_left_type1(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            result = TEST_BOARDS["column_removed_type1_left"]
            board = HexobanBoard(board_str=input)
            board.remove_column_left()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 7
            assert board.width == 9

        def test_removes_column_left_type2(self):
            input = TEST_BOARDS["input_scheme1_type2"]
            result = TEST_BOARDS["column_removed_type2_left"]
            board = HexobanBoard(board_str=input)
            board.remove_column_left()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 7
            assert board.width == 9

        def test_removes_column_right_type1(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            result = TEST_BOARDS["column_removed_type1_right"]
            board = HexobanBoard(board_str=input)
            board.remove_column_right()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 7
            assert board.width == 9

        def test_removes_column_right_type2(self):
            input = TEST_BOARDS["input_scheme1_type2"]
            result = TEST_BOARDS["column_removed_type2_right"]
            board = HexobanBoard(board_str=input)
            board.remove_column_right()
            assert board.to_str(use_visible_floor=True) == result
            assert board.height == 7
            assert board.width == 9

        def test_resizes_board_to_bigger(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            board = HexobanBoard(board_str=input)
            old_width = board.width
            old_height = board.height
            board.resize(board.width + 5, board.height + 5)
            assert board.width == old_width + 5
            assert board.height == old_height + 5

        def test_resizes_board_to_smaller(self):
            input = TEST_BOARDS["input_scheme1_type1"]
            board = HexobanBoard(board_str=input)
            old_height = board.height
            board.resize(board.width - 3, board.height - 3)
            assert board.width == 7
            assert board.height == old_height - 3
