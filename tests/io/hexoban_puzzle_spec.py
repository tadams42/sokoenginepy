import json
import os

import pytest

from sokoenginepy.io import HexobanPuzzle


@pytest.fixture(scope="session")
def tests_data(resources_root):
    path = os.path.join(resources_root, "test_data", "hexoban_parser_tests.json")

    with open(path) as f:
        data = json.load(f)

    return data


class DescribeHexobanPuzzle:
    def it_raises_on_illegal_scheme(self, tests_data):
        board = "\n".join(tests_data["illegal_scheme1"])
        puzzle = HexobanPuzzle(board=board)
        with pytest.raises(ValueError):
            # Trigger parsing
            puzzle.width

        board = "\n".join(tests_data["illegal_scheme2"])
        puzzle = HexobanPuzzle(board=board)
        with pytest.raises(ValueError):
            # Trigger parsing
            puzzle.width

    class describe_parser_tests:
        def it_correctly_parses_hexocet_collection(self, tests_data):
            for level_title, test_case in tests_data[_PARSING_HEXOCET_KEY].items():
                src = "\n".join(test_case["src"])
                parsed = "\n".join(test_case["parsed"])
                parsed_width = test_case["parsed_width"]
                parsed_height = test_case["parsed_height"]
                fail_msg = f"Failed Hexocet parsing test: {level_title}"

                raised = False
                try:
                    in_puzzle = HexobanPuzzle(board=src)
                    in_puzzle.width
                    out_puzzle = HexobanPuzzle(board=parsed)
                    out_puzzle.width
                except ValueError:
                    raised = True

                assert not raised, fail_msg
                assert in_puzzle.board == src, fail_msg
                assert out_puzzle.board == parsed, fail_msg
                assert str(in_puzzle) == parsed, fail_msg
                assert str(in_puzzle) == str(out_puzzle), fail_msg
                assert in_puzzle.width == parsed_width, fail_msg
                assert in_puzzle.height == parsed_height, fail_msg

        def it_correctly_parses_various_hexoban_text_layout_schemes(self, tests_data):
            for level_title, test_case in tests_data[_PARSING_SCHEMES_KEY].items():
                src = "\n".join(test_case["src"])
                parsed = "\n".join(test_case["parsed"])
                parsed_width = test_case["parsed_width"]
                parsed_height = test_case["parsed_height"]
                fail_msg = f"Failed schemes parsing test: {level_title}"

                raised = False
                try:
                    in_puzzle = HexobanPuzzle(board=src)
                    in_puzzle.width
                    out_puzzle = HexobanPuzzle(board=parsed)
                    out_puzzle.width
                except ValueError:
                    raised = True

                assert not raised, fail_msg
                assert in_puzzle.board == src, fail_msg
                assert out_puzzle.board == parsed, fail_msg
                assert str(in_puzzle) == parsed, fail_msg
                assert str(in_puzzle) == str(out_puzzle), fail_msg
                assert in_puzzle.width == parsed_width, fail_msg
                assert in_puzzle.height == parsed_height, fail_msg

    class describe_row_and_column_reordering:
        def it_correctly_reorders_rows_and_columns(self, tests_data):
            for test_title, test_case in tests_data[_REVERSING_KEY].items():
                src_key = test_case["src"]
                board = "\n".join(tests_data[_PARSING_SCHEMES_KEY][src_key]["src"])
                result = "\n".join(test_case["result"])
                method_name = test_case["method"]
                fail_msg = f'Failed mirroring test "{test_title}"!'

                raised = False
                try:
                    puzzle = HexobanPuzzle(board=board)
                    getattr(puzzle, method_name)()
                except ValueError:
                    raised = True

                assert not raised, fail_msg
                assert str(puzzle) == result, fail_msg
                assert puzzle.width == test_case["result_width"], fail_msg
                assert puzzle.height == test_case["result_height"], fail_msg

    class describe_board_resizing:
        def it_can_resize_board_independently_of_encoding_scheme(self, tests_data):
            for test_title, test_case in tests_data[_RESIZING_KEY].items():
                src_key = test_case["src"]
                board = "\n".join(tests_data[_PARSING_SCHEMES_KEY][src_key]["src"])
                result = "\n".join(test_case["result"])
                method_name = test_case["method"]
                fail_msg = f'Failed resizing test "{test_title}"!'

                raised = False
                try:
                    puzzle = HexobanPuzzle(board=board)
                    puzzle.width
                    getattr(puzzle, method_name)()
                except ValueError:
                    raised = True

                assert not raised, fail_msg
                assert str(puzzle) == result, fail_msg
                assert puzzle.width == test_case["result_width"], fail_msg
                assert puzzle.height == test_case["result_height"], fail_msg

        def test_resizes_board_to_bigger(self, tests_data):
            board = "\n".join(tests_data[_PARSING_SCHEMES_KEY]["scheme1_type1"]["src"])
            puzzle = HexobanPuzzle(board=board)
            old_width = puzzle.width
            old_height = puzzle.height
            puzzle.resize(puzzle.width + 5, puzzle.height + 5)
            assert puzzle.width == old_width + 5
            assert puzzle.height == old_height + 5

        def test_resizes_board_to_smaller(self, tests_data):
            board = "\n".join(tests_data[_PARSING_SCHEMES_KEY]["scheme1_type1"]["src"])
            puzzle = HexobanPuzzle(board=board)
            old_height = puzzle.height
            puzzle.resize(puzzle.width - 3, puzzle.height - 3)
            assert puzzle.width == 7
            assert puzzle.height == old_height - 3


_PARSING_HEXOCET_KEY = "parsing - Hexocet"
_PARSING_SCHEMES_KEY = "parsing - schemes"
_RESIZING_KEY = "resizing"
_REVERSING_KEY = "reversing"
