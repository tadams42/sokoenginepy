from unittest.mock import Mock, call

import pytest
from factories import SokobanPlusFactory
from sokoenginepy.board import SokobanPlus, SokobanPlusDataError


class DescribeSokobanPlus:

    class Describe_init:

        def it_doesnt_validate_on_init(self):
            sokoban_plus = SokobanPlus(42, "foo bar", [4, 2])
            assert not sokoban_plus._is_validated

        def it_always_creates_disabled_instance(self):
            sokoban_plus = SokobanPlus(42, "foo bar", [4, 2])
            assert not sokoban_plus.is_enabled

    class Describe_boxorder_and_goalorder:

        def test_they_return_order_object_from_init_if_sokoban_plus_is_not_valid(
            self, sokoban_plus
        ):
            sokoban_plus = SokobanPlus(5, "1 2 3 4 5 6", "6 5 4 3 2 1")
            assert sokoban_plus.boxorder == "1 2 3 4 5 6"
            assert sokoban_plus.goalorder == "6 5 4 3 2 1"
            sokoban_plus = SokobanPlus(5, "foo", "bar")
            assert sokoban_plus.boxorder == "foo"
            assert sokoban_plus.goalorder == "bar"

        def test_they_return_parsed_order_string_if_sokoban_plus_is_valid(self):
            sokoban_plus = SokobanPlus(5, "1 2 0 3 0 ", "3 1 0 2 0 0 0")
            assert sokoban_plus.boxorder == "1 2 0 3"
            assert sokoban_plus.goalorder == "3 1 0 2"

        def test_setters_disable_and_invalidate_instance(self):
            sokoban_plus = SokobanPlus(5, "1 2 0 3 0 ", "3 1 0 2 0 0 0")
            sokoban_plus.is_enabled = True
            assert sokoban_plus.is_valid == True
            assert sokoban_plus.is_enabled == True
            sokoban_plus.boxorder = 'foo'
            assert sokoban_plus.boxorder == 'foo'
            assert sokoban_plus.is_enabled == False
            assert sokoban_plus.is_valid == False

            sokoban_plus = SokobanPlus(5, "1 2 0 3 0 ", "3 1 0 2 0 0 0")
            sokoban_plus.is_enabled = True
            assert sokoban_plus.is_valid == True
            assert sokoban_plus.is_enabled == True
            sokoban_plus.goalorder = 'foo'
            assert sokoban_plus.goalorder == 'foo'
            assert sokoban_plus.is_enabled == False
            assert sokoban_plus.is_valid == False

        def test_setters_dont_disable_and_invalidate_if_setting_to_equal_value(self):
            sokoban_plus = SokobanPlus(5, "1 2 0 3 0", "3 1 0 2 0 0 0")
            sokoban_plus.is_enabled = True
            assert sokoban_plus.is_valid == True
            assert sokoban_plus.is_enabled == True

            sokoban_plus.boxorder = '1 2 0 3 0'
            assert sokoban_plus.boxorder == '1 2 0 3'
            assert sokoban_plus.is_valid == True
            assert sokoban_plus.is_enabled == True

            sokoban_plus.goalorder = '3 1 0 2 0 0 0'
            assert sokoban_plus.goalorder == '3 1 0 2'
            assert sokoban_plus.is_valid == True
            assert sokoban_plus.is_enabled == True

    class Describe_getter_for_box_plus_id:

        def it_returns_default_plus_id_for_disabled_sokoban_plus(
            self, sokoban_plus
        ):
            assert sokoban_plus.box_plus_id(42) == SokobanPlus.DEFAULT_PLUS_ID

        def it_returns_box_plus_id_for_enabled_sokoban_plus(self, sokoban_plus):
            sokoban_plus.is_enabled = True
            assert sokoban_plus.box_plus_id(2) == sokoban_plus._box_plus_ids[2]

    class Describe_getter_for_goal_plus_id:

        def it_returns_default_plus_id_for_disabled_sokoban_plus(
            self, sokoban_plus
        ):
            assert sokoban_plus.goal_plus_id(42) == SokobanPlus.DEFAULT_PLUS_ID

        def it_returns_goal_plus_id_for_enabled_sokoban_plus(
            self, sokoban_plus
        ):
            sokoban_plus.is_enabled = True
            assert sokoban_plus.goal_plus_id(2) == sokoban_plus._goal_plus_ids[2]

    class When_it_is_set_to_enabled:

        def it_parses_init_data(self, sokoban_plus):
            assert not sokoban_plus._is_validated
            sokoban_plus.is_enabled = True
            assert sokoban_plus._is_validated

        def it_raises_on_invalid_data(self):
            sokoban_plus = SokobanPlus(5, "ZOMG!", "YOLO")
            with pytest.raises(SokobanPlusDataError):
                sokoban_plus.is_enabled = True

        def it_enables_sokoban_plus(self, sokoban_plus):
            assert not sokoban_plus._is_enabled
            sokoban_plus.is_enabled = True
            assert sokoban_plus._is_enabled

    class Describe_legacy_plus_id_handling:

        def it_converts_legacy_plus_ids_silently_if_piece_count_is_smaller_than_legacy_plus_id(
            self
        ):
            sokoban_plus = SokobanPlusFactory(
                pieces_count=10,
                boxorder="1 5 42 {0} 23".
                format(SokobanPlus._LEGACY_DEFAULT_PLUS_ID),
                goalorder="1 5 42 {0} 23".
                format(SokobanPlus._LEGACY_DEFAULT_PLUS_ID)
            )
            sokoban_plus.is_enabled = True
            assert sokoban_plus.boxorder == "1 5 42 {0} 23".format(
                SokobanPlus.DEFAULT_PLUS_ID
            )
            assert sokoban_plus.goalorder == "1 5 42 {0} 23".format(
                SokobanPlus.DEFAULT_PLUS_ID
            )

        def it_doesnt_convert_legacy_plus_ids_if_piece_count_is_greater_than_legacy_plus_id(
            self, sokoban_plus
        ):
            sokoban_plus = SokobanPlusFactory(
                pieces_count=SokobanPlus._LEGACY_DEFAULT_PLUS_ID,
                boxorder="1 5 42 {0} 23".
                format(SokobanPlus._LEGACY_DEFAULT_PLUS_ID),
                goalorder="1 5 42 {0} 23".
                format(SokobanPlus._LEGACY_DEFAULT_PLUS_ID)
            )
            sokoban_plus.is_enabled = True
            assert sokoban_plus.boxorder == "1 5 42 {0} 23".format(
                SokobanPlus._LEGACY_DEFAULT_PLUS_ID
            )
            assert sokoban_plus.goalorder == "1 5 42 {0} 23".format(
                SokobanPlus._LEGACY_DEFAULT_PLUS_ID
            )

    class Describe_is_valid:

        def it_is_valid_calls_all_validators(self, sokoban_plus):
            sokoban_plus._validate_plus_ids = Mock()
            sokoban_plus._validate_piece_count = Mock()
            sokoban_plus._validate_ids_counts = Mock()
            sokoban_plus._validate_id_sets_equality = Mock()
            sokoban_plus.is_valid

            assert sokoban_plus._validate_plus_ids.call_count == 2
            assert sokoban_plus._validate_plus_ids.call_args_list == [
                call(sokoban_plus._box_plus_ids),
                call(sokoban_plus._goal_plus_ids)
            ]
            assert sokoban_plus._validate_piece_count.called
            assert sokoban_plus._validate_ids_counts.called
            assert sokoban_plus._validate_id_sets_equality.called

        def it_validates_all_plus_ids(self, sokoban_plus):
            sokoban_plus.is_enabled = True
            sokoban_plus.is_valid_plus_id = Mock()
            sokoban_plus.is_valid_plus_id.return_value = True
            sokoban_plus._validate_plus_ids(sokoban_plus._box_plus_ids)

            assert sokoban_plus.is_valid_plus_id.call_args_list == [
                call(id) for id in sokoban_plus._box_plus_ids
            ]
            assert len(sokoban_plus.errors) == 0

            sokoban_plus.is_valid_plus_id.return_value = False
            sokoban_plus._validate_plus_ids(sokoban_plus._box_plus_ids)
            assert len(sokoban_plus.errors) > 0

        def it_validates_piece_count_is_greater_or_equal_than_zero(
            self, sokoban_plus
        ):
            sokoban_plus._validate_piece_count()
            assert len(sokoban_plus.errors) == 0
            sokoban_plus._pieces_count = -42
            sokoban_plus._validate_piece_count()
            assert len(sokoban_plus.errors) > 0

        def it_validates_ids_lengths_are_equal_to_piece_count(
            self, sokoban_plus
        ):
            sokoban_plus.is_enabled = True
            sokoban_plus._validate_ids_counts()
            assert len(sokoban_plus.errors) == 0
            sokoban_plus._pieces_count = -42
            sokoban_plus._validate_ids_counts()
            assert len(sokoban_plus.errors) > 0

        def it_validates_there_are_not_to_many_ids(self):
            sokoban_plus = SokobanPlusFactory(
                goalorder="1 2 3 4 5 6", boxorder="5 4 3 2 1", pieces_count=5
            )
            sokoban_plus._parse()
            assert not sokoban_plus.is_valid

        def it_validates_same_id_set_is_defined_for_both_piece_types(
            self, sokoban_plus
        ):
            sokoban_plus.is_enabled = True
            sokoban_plus._validate_id_sets_equality()
            assert len(sokoban_plus.errors) == 0

            sokoban_plus._box_plus_ids = \
                sokoban_plus._goal_plus_ids.copy()
            sokoban_plus._box_plus_ids[42000] = 24000

            sokoban_plus._validate_id_sets_equality()
            assert len(sokoban_plus.errors) > 0

        def it_allows_that_there_are_duplicate_plus_ids_for_same_piece_type(
            self
        ):
            sokoban_plus = SokobanPlusFactory(
                goalorder="1 1 2 2 3 3",
                boxorder="2 2 3 3 1 1",
                pieces_count=10
            )
            sokoban_plus._parse()
            assert sokoban_plus.is_valid
