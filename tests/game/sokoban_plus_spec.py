import pytest

from sokoenginepy.game import SokobanPlus, SokobanPlusDataError


@pytest.fixture
def sokoban_plus():
    return SokobanPlus(pieces_count=5, boxorder="42 24 4 2", goalorder="2 24 42 4")


class DescribeSokobanPlus:
    class Describe_init:
        def it_doesnt_validate_on_init(self):
            raised = False
            try:
                sokoban_plus = SokobanPlus(1, "foo bar", "4 2")

            except Exception:
                raised = True

            assert not raised
            assert not sokoban_plus.is_valid

        def it_always_creates_disabled_instance(self):
            sokoban_plus = SokobanPlus(42, "foo bar", "4 2")
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

        def test_they_return_parsed_order_string_if_sokoban_plus_is_valid_and_enabled(
            self,
        ):
            sokoban_plus = SokobanPlus(5, "1 2 0 3 0", "3 1 0 2 0 0 0")
            assert sokoban_plus.boxorder == "1 2 0 3 0"
            assert sokoban_plus.goalorder == "3 1 0 2 0 0 0"
            sokoban_plus.is_enabled = True
            assert sokoban_plus.boxorder == "1 2 0 3"
            assert sokoban_plus.goalorder == "3 1 0 2"

        def test_setters_disable_and_invalidate_instance(self):
            sokoban_plus = SokobanPlus(5, "1 2 0 3 0 ", "3 1 0 2 0 0 0")
            sokoban_plus.is_enabled = True
            assert sokoban_plus.is_valid is True
            assert sokoban_plus.is_enabled is True
            sokoban_plus.boxorder = "foo"
            assert sokoban_plus.boxorder == "foo"
            assert sokoban_plus.is_enabled is False
            assert sokoban_plus.is_valid is False

            sokoban_plus = SokobanPlus(5, "1 2 0 3 0 ", "3 1 0 2 0 0 0")
            sokoban_plus.is_enabled = True
            assert sokoban_plus.is_valid is True
            assert sokoban_plus.is_enabled is True
            sokoban_plus.goalorder = "foo"
            assert sokoban_plus.goalorder == "foo"
            assert sokoban_plus.is_enabled is False
            assert sokoban_plus.is_valid is False

        def test_setters_dont_disable_and_invalidate_if_setting_to_equal_value(self):
            sokoban_plus = SokobanPlus(5, "1 2 0 3 0", "3 1 0 2 0 0 0")
            sokoban_plus.is_enabled = True
            assert sokoban_plus.is_valid is True
            assert sokoban_plus.is_enabled is True

            sokoban_plus.boxorder = "1 2 0 3 0"
            assert sokoban_plus.boxorder == "1 2 0 3"
            assert sokoban_plus.is_valid is True
            assert sokoban_plus.is_enabled is True

            sokoban_plus.goalorder = "3 1 0 2 0 0 0"
            assert sokoban_plus.goalorder == "3 1 0 2"
            assert sokoban_plus.is_valid is True
            assert sokoban_plus.is_enabled is True

    class Describe_getter_for_box_plus_id:
        def it_returns_default_plus_id_for_disabled_sokoban_plus(self, sokoban_plus):
            assert sokoban_plus.box_plus_id(42) == SokobanPlus.DEFAULT_PLUS_ID

        def it_returns_box_plus_id_for_enabled_sokoban_plus(self, sokoban_plus):
            sokoban_plus.is_enabled = True
            assert sokoban_plus.box_plus_id(2) == int(sokoban_plus.boxorder.split()[1])

    class Describe_getter_for_goal_plus_id:
        def it_returns_default_plus_id_for_disabled_sokoban_plus(self, sokoban_plus):
            assert sokoban_plus.goal_plus_id(42) == SokobanPlus.DEFAULT_PLUS_ID

        def it_returns_goal_plus_id_for_enabled_sokoban_plus(self, sokoban_plus):
            sokoban_plus.is_enabled = True
            assert sokoban_plus.goal_plus_id(2) == int(
                sokoban_plus.goalorder.split()[1]
            )

    class When_it_is_set_to_enabled:
        def it_parses_init_data(self, sokoban_plus):
            assert not sokoban_plus.is_validated
            sokoban_plus.is_enabled = True
            assert sokoban_plus.is_validated

        def it_raises_on_invalid_data(self):
            sokoban_plus = SokobanPlus(5, "ZOMG!", "YOLO")
            with pytest.raises(SokobanPlusDataError):
                sokoban_plus.is_enabled = True

        def it_enables_sokoban_plus(self, sokoban_plus):
            assert not sokoban_plus.is_enabled
            sokoban_plus.is_enabled = True
            assert sokoban_plus.is_enabled

    class Describe_legacy_plus_id_handling:
        def it_converts_legacy_plus_ids_silently_if_piece_count_is_smaller_than_legacy_plus_id(
            self,
        ):
            sokoban_plus = SokobanPlus(
                pieces_count=10,
                boxorder=f"1 5 42 {SokobanPlus.LEGACY_DEFAULT_PLUS_ID} 23",
                goalorder=f"1 5 42 {SokobanPlus.LEGACY_DEFAULT_PLUS_ID} 23",
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
            sokoban_plus = SokobanPlus(
                pieces_count=SokobanPlus.LEGACY_DEFAULT_PLUS_ID,
                boxorder=f"1 5 42 {SokobanPlus.LEGACY_DEFAULT_PLUS_ID} 23",
                goalorder=f"1 5 42 {SokobanPlus.LEGACY_DEFAULT_PLUS_ID} 23",
            )
            sokoban_plus.is_enabled = True
            assert sokoban_plus.boxorder == "1 5 42 {0} 23".format(
                SokobanPlus.LEGACY_DEFAULT_PLUS_ID
            )
            assert sokoban_plus.goalorder == "1 5 42 {0} 23".format(
                SokobanPlus.LEGACY_DEFAULT_PLUS_ID
            )

    class Describe_is_valid:
        def it_validates_all_plus_ids(self):
            sokoban_plus = SokobanPlus(3, "1 2 3", "3 2 1")
            assert sokoban_plus.is_valid
            assert len(sokoban_plus.errors) == 0

            sokoban_plus = SokobanPlus(3, "-1 -2 -3", "3 2 1")
            assert not sokoban_plus.is_valid
            assert len(sokoban_plus.errors) > 0

        def it_validates_piece_count_is_greater_or_equal_than_zero(
            self, is_using_native
        ):
            sokoban_plus = SokobanPlus(42, "1 2 3", "3 2 1")
            assert sokoban_plus.is_valid

            if is_using_native:
                with pytest.raises(TypeError):
                    sokoban_plus = SokobanPlus(-42, "1 2 3", "3 2 1")
            else:
                sokoban_plus = SokobanPlus(-42, "1 2 3", "3 2 1")
                assert not sokoban_plus.is_valid

        def it_validates_ids_lengths_are_equal_to_piece_count(self):
            sokoban_plus = SokobanPlus(4, "1 2 3", "3 2 1")
            assert sokoban_plus.is_valid

            sokoban_plus = SokobanPlus(2, "1 2 3", "3 2 1")
            assert not sokoban_plus.is_valid

        def it_validates_there_are_not_to_many_ids(self):
            sokoban_plus = SokobanPlus(
                goalorder="1 2 3 4 5 6", boxorder="6 5 4 3 2 1", pieces_count=5
            )
            assert not sokoban_plus.is_valid

        def it_validates_same_id_set_is_defined_for_both_piece_types(self):
            sokoban_plus = SokobanPlus(
                goalorder="1 2 3 4 5 6", boxorder="5 4 3 2 1", pieces_count=6
            )
            assert not sokoban_plus.is_valid

        def it_allows_that_there_are_duplicate_plus_ids_for_same_piece_type(self):
            sokoban_plus = SokobanPlus(
                goalorder="1 1 2 2 3 3", boxorder="2 2 3 3 1 1", pieces_count=10
            )
            assert sokoban_plus.is_valid
