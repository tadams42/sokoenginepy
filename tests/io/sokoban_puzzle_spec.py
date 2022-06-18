import textwrap

import pytest

from sokoenginepy.game import Tessellation, index_1d
from sokoenginepy.io import Puzzle, SokobanPuzzle


class DescribeSokobanPuzzle:
    def it_creates_board_of_specified_size_and_tessellation(self):
        b = SokobanPuzzle(4, 2)
        assert b.width == 4
        assert b.height == 2
        assert b.tessellation == Tessellation.SOKOBAN

    def it_ignores_specified_size_if_board_string_is_given_and_parses_given_string_instead(
        self,
    ):
        puzzle = SokobanPuzzle(4, 2, board="#        #")
        assert puzzle.width == 10
        assert puzzle.height == 1
        assert puzzle.board == "#        #"
        assert puzzle.to_board_str(use_visible_floor=True) == "#--------#"

    def it_carries_some_metadata(self):
        puzzle = SokobanPuzzle()
        puzzle.title = "title"
        assert puzzle.title == "title"
        puzzle.author = "author"
        assert puzzle.author == "author"
        puzzle.boxorder = "boxorder"
        assert puzzle.boxorder == "boxorder"
        puzzle.goalorder = "goalorder"
        assert puzzle.goalorder == "goalorder"

    def it_can_access_individual_board_characters(self):
        puzzle = SokobanPuzzle(width=5, height=5)
        puzzle[index_1d(3, 3, puzzle.width)] = Puzzle.WALL
        assert puzzle[index_1d(3, 3, puzzle.width)] == Puzzle.WALL

    def it_validates_input_characters_when_setting_them(self):
        puzzle = SokobanPuzzle(width=5, height=5)
        with pytest.raises(ValueError):
            puzzle[index_1d(3, 3, puzzle.width)] = "Z"

    def it_provides_underlying_tessellation(self):
        puzzle = SokobanPuzzle()
        assert puzzle.tessellation == Tessellation.SOKOBAN

    def it_provides_board_dimensions(self):
        puzzle = SokobanPuzzle(4, 2)
        assert puzzle.width == 4
        assert puzzle.height == 2
        assert puzzle.size == 8

    def it_provides_agents_counts(self):
        puzzle = SokobanPuzzle(board="#@@...$$$$#")
        assert puzzle.pushers_count == 2
        assert puzzle.goals_count == 3
        assert puzzle.boxes_count == 4

    def it_provides_internal_and_original_board_strings(self):
        puzzle = SokobanPuzzle(4, 2)
        assert puzzle.internal_board == "--------"
        assert puzzle.board == ""
        assert puzzle.width == 4
        assert puzzle.height == 2

        puzzle = SokobanPuzzle(board="#       #")
        assert puzzle.internal_board == "#-------#"
        assert puzzle.board == "#       #"
        assert puzzle.width == 9
        assert puzzle.height == 1

    class describe_conversions_to_string:
        def test_board_returns_original_unparsed_data(self):
            puzzle = SokobanPuzzle(board="#   -   #")
            assert puzzle.board == "#   -   #"

        def test_str_prints_parsed_board_with_invisible_floors(self):
            puzzle = SokobanPuzzle(board="#   -   #")
            assert str(puzzle) == "#       #"

        def test_to_board_str_prints_parsed_board_with_configurable_output(self):
            puzzle = SokobanPuzzle(board="#   -   #")
            assert puzzle.to_board_str(use_visible_floor=False) == "#       #"
            assert puzzle.to_board_str(use_visible_floor=True) == "#-------#"

    class describe_parsing_from_string:
        def it_parses_board_from_string(self):
            data = """
                #####
                #   #
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
            data = textwrap.dedent(data)

            result = """
                ----#####----------
                ----#---#----------
                ----#$--#----------
                --###--$##---------
                --#--$-$-#---------
                ###-#-##-#---######
                #---#-##-#####--..#
                #-$--$----------..#
                #####-###-#@##--..#
                ----#-----#########
                ----#######--------
            """
            result = textwrap.dedent(result.lstrip("\n").rstrip())

            puzzle = SokobanPuzzle(board=data)
            assert puzzle.width == 19
            assert puzzle.height == 11
            assert puzzle.to_board_str(use_visible_floor=True) == result

        def it_raises_on_illegal_characters_in_board_string(self):
            with pytest.raises(ValueError):
                SokobanPuzzle(board="ZOMG!")

            with pytest.raises(ValueError):
                puzzle = SokobanPuzzle()
                puzzle.board = "ZOMG!"

        def it_correctly_parses_board_with_internal_blank_rows(self):
            # ::   The first and the last non-empty square in each row  ::
            # ::   must be a wall or a box on a goal. An empty interior ::
            # ::   row is written with at least one "-" or "_".         ::

            # Notice that our parser is correct even without that one "-" or "_"

            sources = [
                (
                    " ##########\n    \n"
                    " ## @ *   #\n"
                    "##  $ ####\n"
                    "# $.+ #\n"
                    "#######\n"
                ),
                (
                    " ##########\n  - \n"
                    " ## @ *   #\n"
                    "##  $ ####\n"
                    "# $.+ #\n"
                    "#######\n"
                ),
            ]

            result = """
                -##########
                -----------
                -##-@-*---#
                ##--$-####-
                #-$.+-#----
                #######----
            """
            result = textwrap.dedent(result.lstrip("\n").rstrip())

            for data in sources:
                puzzle = SokobanPuzzle(board=data)
                assert puzzle.width == 11
                assert puzzle.height == 6
                assert puzzle.to_board_str(use_visible_floor=True) == result

        def it_parses_RLE_encoded_board(self):
            # ::   The first and the last non-empty square in each row  ::
            # ::   must be a wall or a box on a goal. An empty interior ::
            # ::   row is written with at least one "-" or "_".         ::

            # Notice that our parser can go even without that on "-" or "_"

            sources = [
                (
                    " ##########   |"
                    " ## @ *   #|"
                    "##  $ ####|"
                    "# $.+ #|||"
                    "#######   |"
                ),
                (
                    " ##########   |"
                    " ## @ *   #|"
                    "##  $ ####|"
                    "# $.+ #|||"
                    "#######   |"
                ),
            ]

            result = """
                -##########---
                -##-@-*---#---
                ##--$-####----
                #-$.+-#-------
                --------------
                --------------
                #######-------
            """
            result = textwrap.dedent(result.lstrip("\n").rstrip())

            for src in sources:
                puzzle = SokobanPuzzle(board=src)
                assert puzzle.width == 14
                assert puzzle.height == 7
                assert puzzle.to_board_str(use_visible_floor=True) == result

        def it_carefully_preserves_original_newlines(self):
            src = (
                " ##########\n    \n\n"
                " ## @ *   #\n\n"
                "##  $ ####\n\n"
                "# $.+ #\n\n"
                "#######\n\n"
            )
            result = """
                -##########
                -----------
                -----------
                -##-@-*---#
                -----------
                ##--$-####-
                -----------
                #-$.+-#----
                -----------
                #######----
            """
            result = textwrap.dedent(result.lstrip("\n").rstrip())

            puzzle = SokobanPuzzle(board=src)
            assert puzzle.width == 11
            assert puzzle.height == 10
            assert puzzle.to_board_str(use_visible_floor=True) == result

    class describe_resize:
        def it_adds_right_columns_and_bottom_rows_when_enlarging(self):
            data = """
                #####
                #   #
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
            data = textwrap.dedent(data)

            result = """
                ----#####------------
                ----#---#------------
                ----#$--#------------
                --###--$##-----------
                --#--$-$-#-----------
                ###-#-##-#---######--
                #---#-##-#####--..#--
                #-$--$----------..#--
                #####-###-#@##--..#--
                ----#-----#########--
                ----#######----------
                ---------------------
                ---------------------
            """
            result = textwrap.dedent(result.lstrip("\n").rstrip())

            puzzle = SokobanPuzzle(board=data)
            puzzle.resize(puzzle.width + 2, puzzle.height + 2)
            assert puzzle.width == 21
            assert puzzle.height == 13
            assert puzzle.to_board_str(use_visible_floor=True) == result

        def it_removes_right_columns_and_bottom_rows_when_shrinking(self):
            data = """
                #####
                #   #
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
            data = textwrap.dedent(data)

            result = """
                ----#####--------
                ----#---#--------
                ----#$--#--------
                --###--$##-------
                --#--$-$-#-------
                ###-#-##-#---####
                #---#-##-#####--.
                #-$--$----------.
                #####-###-#@##--.
            """
            result = textwrap.dedent(result.lstrip("\n").rstrip())

            puzzle = SokobanPuzzle(board=data)
            puzzle.resize(puzzle.width - 2, puzzle.height - 2)
            assert puzzle.width == 17
            assert puzzle.height == 9
            assert puzzle.to_board_str(use_visible_floor=True) == result

    class describe_resize_and_center:
        def it_adds_columns_and_rows_when_enlarging(self):
            data = """
                #####
                #   #
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
            data = textwrap.dedent(data)

            result = """
                ------------------------
                ------------------------
                ------#####-------------
                ------#---#-------------
                ------#$--#-------------
                ----###--$##------------
                ----#--$-$-#------------
                --###-#-##-#---######---
                --#---#-##-#####--..#---
                --#-$--$----------..#---
                --#####-###-#@##--..#---
                ------#-----#########---
                ------#######-----------
                ------------------------
                ------------------------
                ------------------------
            """
            result = textwrap.dedent(result.lstrip("\n").rstrip())

            puzzle = SokobanPuzzle(board=data)
            puzzle.resize_and_center(puzzle.width + 5, puzzle.height + 5)
            assert puzzle.width == 24
            assert puzzle.height == 16
            assert puzzle.to_board_str(use_visible_floor=True) == result

        def it_doesnt_remove_columns_or_rows_when_compacting(self):
            data = """
                #####
                #   #
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
            data = textwrap.dedent(data)

            result = """
                ----#####----------
                ----#---#----------
                ----#$--#----------
                --###--$##---------
                --#--$-$-#---------
                ###-#-##-#---######
                #---#-##-#####--..#
                #-$--$----------..#
                #####-###-#@##--..#
                ----#-----#########
                ----#######--------
            """
            result = textwrap.dedent(result.lstrip("\n").rstrip())

            puzzle = SokobanPuzzle(board=data)
            puzzle.resize_and_center(puzzle.width - 2, puzzle.height - 2)
            assert puzzle.width == 19
            assert puzzle.height == 11
            assert puzzle.to_board_str(use_visible_floor=True) == result

    class describe_trim:
        def it_removes_empty_outer_rows_and_columns(self):
            data = """
                ------------------------
                ------------------------
                ------#####-------------
                ------#---#-------------
                ------#$--#-------------
                ----###--$##------------
                ----#--$-$-#------------
                --###-#-##-#---######---
                --#---#-##-#####--..#---
                --#-$--$----------..#---
                --#####-###-#@##--..#---
                ------#-----#########---
                ------#######-----------
                ------------------------
                ------------------------
                ------------------------
            """
            data = textwrap.dedent(data)

            result = """
                ----#####----------
                ----#---#----------
                ----#$--#----------
                --###--$##---------
                --#--$-$-#---------
                ###-#-##-#---######
                #---#-##-#####--..#
                #-$--$----------..#
                #####-###-#@##--..#
                ----#-----#########
                ----#######--------
            """
            result = textwrap.dedent(result.lstrip("\n").rstrip())

            puzzle = SokobanPuzzle(board=data)
            puzzle.trim()
            assert puzzle.width == 19
            assert puzzle.height == 11
            assert puzzle.to_board_str(use_visible_floor=True) == result

    class describe_reverse_rows:
        def it_mirrors_board_up_down(self):
            data = """
                #####
                #   #
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
            data = textwrap.dedent(data)

            result = """
                ----#######--------
                ----#-----#########
                #####-###-#@##--..#
                #-$--$----------..#
                #---#-##-#####--..#
                ###-#-##-#---######
                --#--$-$-#---------
                --###--$##---------
                ----#$--#----------
                ----#---#----------
                ----#####----------
            """
            result = textwrap.dedent(result.lstrip("\n").rstrip())

            puzzle = SokobanPuzzle(board=data)
            puzzle.reverse_rows()
            assert puzzle.width == 19
            assert puzzle.height == 11
            assert puzzle.to_board_str(use_visible_floor=True) == result

    class describe_reverse_columns:
        def it_mirrors_board_left_right(self):
            data = """
                #####
                #   #
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
            data = textwrap.dedent(data)

            result = """
            ----------#####----
            ----------#---#----
            ----------#--$#----
            ---------##$--###--
            ---------#-$-$--#--
            ######---#-##-#-###
            #..--#####-##-#---#
            #..----------$--$-#
            #..--##@#-###-#####
            #########-----#----
            --------#######----
            """
            result = textwrap.dedent(result).lstrip("\n").rstrip()

            puzzle = SokobanPuzzle(board=data)
            puzzle.reverse_columns()
            assert puzzle.width == 19
            assert puzzle.height == 11
            assert puzzle.to_board_str(use_visible_floor=True) == result
