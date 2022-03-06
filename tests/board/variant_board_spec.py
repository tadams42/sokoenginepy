from unittest.mock import patch

import pytest

from sokoenginepy import (
    BoardConversionError,
    BoardGraph,
    Direction,
    GraphType,
    SokobanBoard,
    Tessellation,
    TriobanBoard,
    VariantBoard,
)
from sokoenginepy.utilities import index_1d


class DescribeVariantBoard:
    class describe_is_board_string:
        input = "0123456789\n\t bB$*p_pmM@+#_-|"

        def it_recognizes_board_string(self):
            assert VariantBoard.is_board_string(self.input)

        def it_fails_on_illegal_characters(self):
            assert not VariantBoard.is_board_string(self.input + "z")

        def it_fails_on_numeric_string(self):
            assert not VariantBoard.is_board_string("42")

        def it_fails_on_blank_string(self):
            assert not VariantBoard.is_board_string("")
            assert not VariantBoard.is_board_string("    ")
            assert not VariantBoard.is_board_string("   \r\n ")

    class describe_parse_board_string:
        def it_parses_regular_board(self):
            src = (
                " ##########\n    \n"
                + " ## @ *   #\n"
                + "##  $ ####\n"
                + "# $.+ #\n"
                + "#######\n"
            )
            result = [
                " ##########",
                "           ",
                " ## @ *   #",
                "##  $ #### ",
                "# $.+ #    ",
                "#######    ",
                "           ",
            ]
            parsed = VariantBoard.parse_board_string(src)
            assert parsed == result

        def it_parses_RLE_board(self):
            src = (
                " ##########   |"
                + " ## @ *   #|"
                + "##  $ ####|"
                + "# $.+ #|||"
                + "#######   |"
            )
            result = [
                " ##########   ",
                " ## @ *   #   ",
                "##  $ ####    ",
                "# $.+ #       ",
                "              ",
                "              ",
                "#######       ",
                "              ",
            ]
            parsed = VariantBoard.parse_board_string(src)
            assert parsed == result

        def it_raises_on_illegal_characters(self):
            src = (
                " ##########\n\n"
                + " ##       #\n"
                + "##   z####\n"
                + "#   a #\n"
                + "#######\n"
            )
            with pytest.raises(BoardConversionError):
                VariantBoard.parse_board_string(src)

        def it_discards_empty_but_not_blank_lines(self):
            src = (
                " ##########\n    \n\n"
                + " ## @ *   #\n\n"
                + "##  $ ####\n\n"
                + "# $.+ #\n\n"
                + "#######\n\n"
            )
            result = [
                " ##########",
                "           ",
                "           ",
                " ## @ *   #",
                "           ",
                "##  $ #### ",
                "           ",
                "# $.+ #    ",
                "           ",
                "#######    ",
                "           ",
                "           ",
            ]
            parsed = VariantBoard.parse_board_string(src)
            assert parsed == result

    def it_discards_blank_boards(self):
        src = "              "
        parsed = VariantBoard.parse_board_string(src)
        assert parsed == []

    class describe_init:
        def it_creates_board_of_specified_size_and_tessellation(self):
            b = TriobanBoard(4, 2)
            assert b.width == 4
            assert b.height == 2
            assert b.tessellation == Tessellation.TRIOBAN.value

        def it_ignores_specified_size_if_string_given_and_parses_string_instead(
            self, board_str, board_width, board_height
        ):
            b = SokobanBoard(4, 2, board_str=board_str)
            assert b.width == board_width
            assert b.height == board_height

            assert b.to_str(use_visible_floor=False) == board_str

        def it_raises_on_illegal_board_string(self):
            with pytest.raises(BoardConversionError):
                SokobanBoard(board_str="ZOOMG!")

        def it_reconfigures_all_edges_in_board(self):
            board = SokobanBoard(2, 2)

            assert board.graph.edges_count == 8
            assert board.graph.has_edge(0, 1, Direction.RIGHT)
            assert board.graph.has_edge(1, 0, Direction.LEFT)
            assert board.graph.has_edge(0, 2, Direction.DOWN)
            assert board.graph.has_edge(2, 0, Direction.UP)
            assert board.graph.has_edge(2, 3, Direction.RIGHT)
            assert board.graph.has_edge(3, 2, Direction.LEFT)
            assert board.graph.has_edge(1, 3, Direction.DOWN)
            assert board.graph.has_edge(3, 1, Direction.UP)

        def it_doesnt_create_duplicate_direction_edges_in_multidigraph(self):
            board = TriobanBoard(2, 2)
            assert board.graph.out_edges_count(0, 1) == 2
            assert board.graph.out_edges_count(1, 0) == 2

    if hasattr(VariantBoard, "_reinit"):

        class describe__reinit:
            def it_reinitializes_graph_vertices(self, variant_board):
                variant_board._reinit(width=2, height=3)
                assert variant_board.graph.vertices_count == 2 * 3

                for position in range(0, variant_board.size):
                    assert variant_board[position].is_empty_floor

            def it_reinitializes_width_and_height(self, variant_board):
                variant_board._reinit(width=4, height=5)
                assert variant_board.width == 4
                assert variant_board.height == 5

            def it_optionally_recreates_all_adges(self, variant_board):
                variant_board._reinit(width=4, height=5, reconfigure_edges=False)
                assert variant_board.graph.edges_count == 0
                variant_board._reinit(width=4, height=5)
                assert variant_board.graph.edges_count > 0

    class describe_clear:
        def it_clears_board_cells_in_all_nodes(self, variant_board):
            variant_board.clear()
            for pos in range(0, variant_board.size):
                assert variant_board[pos].is_empty_floor

        def it_doesnt_change_board_dimensions(self, variant_board):
            old_width = variant_board.width
            old_height = variant_board.height
            variant_board.clear()
            assert variant_board.width == old_width
            assert variant_board.height == old_height

    class describe_resize:
        def test_adds_right_columns_and_bottom_rows_when_enlarging(self, variant_board):
            output = "\n".join(
                [
                    "----#####------------",
                    "----#--@#------------",
                    "----#$--#------------",
                    "--###--$##-----------",
                    "--#--$-$-#-----------",
                    "###-#-##-#---######--",
                    "#---#-##-#####--..#--",
                    "#-$--$----------..#--",
                    "#####-###-#@##--..#--",
                    "----#-----#########--",
                    "----#######----------",
                    "---------------------",
                    "---------------------",
                ]
            )
            old_width = variant_board.width
            old_height = variant_board.height
            variant_board.resize(old_width + 2, old_height + 2)
            assert variant_board.width == old_width + 2
            assert variant_board.height == old_height + 2
            assert variant_board.to_str(use_visible_floor=True) == output

        def test_removes_right_columns_and_bottom_rows_when_compacting(
            self, variant_board
        ):
            output = "\n".join(
                [
                    "----#####--------",
                    "----#--@#--------",
                    "----#$--#--------",
                    "--###--$##-------",
                    "--#--$-$-#-------",
                    "###-#-##-#---####",
                    "#---#-##-#####--.",
                    "#-$--$----------.",
                    "#####-###-#@##--.",
                ]
            )
            old_width = variant_board.width
            old_height = variant_board.height
            variant_board.resize(old_width - 2, old_height - 2)
            assert variant_board.width == old_width - 2
            assert variant_board.height == old_height - 2
            assert variant_board.to_str(use_visible_floor=True) == output

        def test_reconfigures_graph_edges_only_once(self, variant_board, mocker):
            if VariantBoard.__module__.startswith("sokoenginepy."):
                with mocker.patch(
                    "sokoenginepy.BoardGraph.reconfigure_edges", return_value=None
                ):
                    variant_board.resize(2, 2)
                    assert variant_board.graph.reconfigure_edges.call_count == 1

    class describe_resize_and_center:
        def test_adds_columns_and_rows_when_enlarging(self, variant_board):
            output = "\n".join(
                [
                    "------------------------",
                    "------------------------",
                    "------#####-------------",
                    "------#--@#-------------",
                    "------#$--#-------------",
                    "----###--$##------------",
                    "----#--$-$-#------------",
                    "--###-#-##-#---######---",
                    "--#---#-##-#####--..#---",
                    "--#-$--$----------..#---",
                    "--#####-###-#@##--..#---",
                    "------#-----#########---",
                    "------#######-----------",
                    "------------------------",
                    "------------------------",
                    "------------------------",
                ]
            )
            old_width = variant_board.width
            old_height = variant_board.height
            variant_board.resize_and_center(old_width + 5, old_height + 5)
            assert variant_board.width == old_width + 5
            assert variant_board.height == old_height + 5
            assert variant_board.to_str(use_visible_floor=True) == output

        def test_removes_right_columns_and_bottom_rows_when_compacting(
            self, variant_board
        ):
            output = "\n".join(
                [
                    "----#####--------",
                    "----#--@#--------",
                    "----#$--#--------",
                    "--###--$##-------",
                    "--#--$-$-#-------",
                    "###-#-##-#---####",
                    "#---#-##-#####--.",
                    "#-$--$----------.",
                    "#####-###-#@##--.",
                ]
            )
            old_width = variant_board.width
            old_height = variant_board.height
            variant_board.resize(old_width - 2, old_height - 2)
            assert variant_board.width == old_width - 2
            assert variant_board.height == old_height - 2
            assert variant_board.to_str(use_visible_floor=True) == output

        def test_reconfigures_graph_edges_only_once(self, variant_board, mocker):
            if VariantBoard.__module__.startswith("sokoenginepy."):
                with mocker.patch(
                    "sokoenginepy.BoardGraph.reconfigure_edges", return_value=None
                ):
                    variant_board.resize_and_center(42, 42)
                    assert variant_board.graph.reconfigure_edges.call_count == 1

    class describe_trim:
        def test_removes_empty_outer_rows_and_columns(self, variant_board):
            output = str(variant_board)
            old_width = variant_board.width
            old_height = variant_board.height

            variant_board.resize_and_center(old_width + 5, old_height + 5)
            variant_board.trim()

            assert variant_board.width == old_width
            assert variant_board.height == old_height
            assert str(variant_board) == output

        def test_reconfigures_graph_edges_only_once(self, variant_board, mocker):
            if VariantBoard.__module__.startswith("sokoenginepy."):
                with mocker.patch(
                    "sokoenginepy.BoardGraph.reconfigure_edges", return_value=None
                ):
                    variant_board.resize(2, 2)
                    assert variant_board.graph.reconfigure_edges.call_count == 1

    class describe_reverse_rows:
        def test_mirrors_board_up_down(self, variant_board):
            output = "\n".join(
                [
                    "----#######--------",
                    "----#-----#########",
                    "#####-###-#@##--..#",
                    "#-$--$----------..#",
                    "#---#-##-#####--..#",
                    "###-#-##-#---######",
                    "--#--$-$-#---------",
                    "--###--$##---------",
                    "----#$--#----------",
                    "----#--@#----------",
                    "----#####----------",
                ]
            )
            variant_board.reverse_rows()
            assert variant_board.to_str(use_visible_floor=True) == output

    class describe_reverse_columns:
        def test_mirrors_board_left_rightt(self, variant_board):
            output = "\n".join(
                [
                    "----------#####----",
                    "----------#@--#----",
                    "----------#--$#----",
                    "---------##$--###--",
                    "---------#-$-$--#--",
                    "######---#-##-#-###",
                    "#..--#####-##-#---#",
                    "#..----------$--$-#",
                    "#..--##@#-###-#####",
                    "#########-----#----",
                    "--------#######----",
                ]
            )
            variant_board.reverse_columns()
            assert variant_board.to_str(use_visible_floor=True) == output
