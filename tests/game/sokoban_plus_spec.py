import pytest
from hamcrest import assert_that, equal_to, is_, empty, is_not
from unittest.mock import Mock, call
from sokoenginepy import SokobanPlus, Piece, SokobanPlusDataError
from sokoenginepy.game import SokobanPlusValidator
from factories import SokobanPlusFactory


class DescribeSokobanPlus(object):

    class Describe_init(object):
        def test_it_doesnt_validate_on_init(self):
            sokoban_plus = SokobanPlus(42, "foo bar", [4, 2])
            assert_that(sokoban_plus._is_validated, equal_to(False))

        def test_it_always_creates_not_enabled_instance(self):
            sokoban_plus = SokobanPlus(42, "foo bar", [4, 2])
            assert_that(sokoban_plus.is_enabled, equal_to(False))

    class Describe_boxorder_and_goalorder(object):
        def test_they_return_order_object_from_init_if_sokoban_plus_is_not_validated(
            self, sokoban_plus
        ):
            assert_that(sokoban_plus._is_validated, equal_to(False))
            assert_that(sokoban_plus.boxorder, equal_to(sokoban_plus._boxorder))
            assert_that(sokoban_plus.goalorder, equal_to(sokoban_plus._goalorder))

        def test_they_return_parsed_order_string_if_sokoban_plus_is_validated(self):
            sokoban_plus = SokobanPlus(5, "1 2 0 3 0 ", "3 1 0 2 0 0 0")
            sokoban_plus._validate()
            assert_that(sokoban_plus.boxorder, equal_to("1 2 0 3"))
            assert_that(sokoban_plus.goalorder, equal_to("3 1 0 2"))

    class Describe_getter_for_box_plus_id(object):
        def test_it_returns_default_plus_id_for_disabled_sokoban_plus(
            self, sokoban_plus
        ):
            assert_that(
                sokoban_plus.box_plus_id(42), equal_to(Piece.DEFAULT_PLUS_ID)
            )

        def test_it_returns_box_plus_id_for_enabled_sokoban_plus(self, sokoban_plus):
            sokoban_plus.is_enabled = True
            assert_that(
                sokoban_plus.box_plus_id(2),
                equal_to(sokoban_plus._box_plus_ids[2 - Piece.DEFAULT_PLUS_ID])
            )

    class Describe_getter_for_goal_plus_id(object):
        def test_it_returns_default_plus_id_for_disabled_sokoban_plus(
            self, sokoban_plus
        ):
            assert_that(
                sokoban_plus.goal_plus_id(42), equal_to(Piece.DEFAULT_PLUS_ID)
            )

        def test_it_returns_goal_plus_id_for_enabled_sokoban_plus(self, sokoban_plus):
            sokoban_plus.is_enabled = True
            assert_that(
                sokoban_plus.goal_plus_id(2),
                equal_to(sokoban_plus._goal_plus_ids[2 - Piece.DEFAULT_PLUS_ID])
            )

    class When_it_is_set_to_enabled(object):
        def test_parses_init_data(self, sokoban_plus):
            assert_that(sokoban_plus._is_validated, equal_to(False))
            sokoban_plus.is_enabled = True
            assert_that(sokoban_plus._is_validated, equal_to(True))

        def test_raises_on_invalid_data(self):
            sokoban_plus = SokobanPlus(5, "ZOMG!", "YOLO")
            with pytest.raises(SokobanPlusDataError):
                sokoban_plus.is_enabled = True

        def test_enables_sokoban_plus(self, sokoban_plus):
            assert_that(sokoban_plus._is_enabled, equal_to(False))
            sokoban_plus.is_enabled = True
            assert_that(sokoban_plus._is_enabled, equal_to(True))

    class Describe_legacy_plus_id_handling(object):
        def test_it_converts_legacy_plus_ids_silently_if_piece_count_is_smaller_than_legacy_plus_id(self):
            sokoban_plus = SokobanPlusFactory(
                pieces_count=10,
                boxorder="1 5 42 {0} 23".format(SokobanPlus._LEGACY_DEFAULT_PLUS_ID),
                goalorder="1 5 42 {0} 23".format(SokobanPlus._LEGACY_DEFAULT_PLUS_ID)
            )
            sokoban_plus.is_enabled = True
            assert_that(
                sokoban_plus.boxorder,
                equal_to("1 5 42 {0} 23".format(Piece.DEFAULT_PLUS_ID))
            )
            assert_that(
                sokoban_plus.goalorder,
                equal_to("1 5 42 {0} 23".format(Piece.DEFAULT_PLUS_ID))
            )

        def test_it_doesnt_convert_legacy_plus_ids_if_piece_count_is_greater_than_legacy_plus_id(
            self, sokoban_plus
        ):
            sokoban_plus = SokobanPlusFactory(
                pieces_count=SokobanPlus._LEGACY_DEFAULT_PLUS_ID,
                boxorder="1 5 42 {0} 23".format(SokobanPlus._LEGACY_DEFAULT_PLUS_ID),
                goalorder="1 5 42 {0} 23".format(SokobanPlus._LEGACY_DEFAULT_PLUS_ID)
            )
            sokoban_plus.is_enabled = True
            assert_that(
                sokoban_plus.boxorder,
                equal_to("1 5 42 {0} 23".format(SokobanPlus._LEGACY_DEFAULT_PLUS_ID))
            )
            assert_that(
                sokoban_plus.goalorder,
                equal_to("1 5 42 {0} 23".format(SokobanPlus._LEGACY_DEFAULT_PLUS_ID))
            )


class DescribeSokobanPlusValidator(object):
    def test_is_valid_calls_all_validators(self, sokoban_plus_validator):
        sokoban_plus_validator._validate_plus_ids_by_piece = Mock()
        sokoban_plus_validator._validate_piece_count = Mock()
        sokoban_plus_validator._validate_ids_counts = Mock()
        sokoban_plus_validator._validate_id_sets_equality = Mock()
        sokoban_plus_validator.is_valid

        assert_that(
            sokoban_plus_validator._validate_plus_ids_by_piece.call_count,
            equal_to(2)
        )
        assert_that(
            sokoban_plus_validator._validate_plus_ids_by_piece.call_args_list,
            equal_to([
                call(sokoban_plus_validator.sokoban_plus._box_plus_ids),
                call(sokoban_plus_validator.sokoban_plus._goal_plus_ids),
            ])
        )
        assert_that(
            sokoban_plus_validator._validate_piece_count.called, equal_to(True)
        )
        assert_that(
            sokoban_plus_validator._validate_ids_counts.called, equal_to(True)
        )
        assert_that(
            sokoban_plus_validator._validate_id_sets_equality.called,
            equal_to(True)
        )

    def test_validates_all_plus_ids_using_piece(self, sokoban_plus_validator):
        method_backup = Piece.is_valid_plus_id

        Piece.is_valid_plus_id = Mock(return_value=True)
        sokoban_plus_validator._validate_plus_ids_by_piece(
            sokoban_plus_validator.sokoban_plus._box_plus_ids
        )
        assert_that(
            Piece.is_valid_plus_id.call_args_list,
            equal_to([
                call(id)
                for id in sokoban_plus_validator.sokoban_plus._box_plus_ids
            ])
        )
        assert_that(sokoban_plus_validator.errors, is_(empty()))

        Piece.is_valid_plus_id = Mock(return_value=False)
        sokoban_plus_validator._validate_plus_ids_by_piece(
            sokoban_plus_validator.sokoban_plus._box_plus_ids
        )
        assert_that(sokoban_plus_validator.errors, is_not(empty()))

        Piece.is_valid_plus_id = method_backup

    def test_validates_piece_count_is_greater_than_zero(
        self, sokoban_plus_validator
    ):
        sokoban_plus_validator._validate_piece_count()
        assert_that(sokoban_plus_validator.errors, is_(empty()))
        sokoban_plus_validator.sokoban_plus._pieces_count = -42
        sokoban_plus_validator._validate_piece_count()
        assert_that(sokoban_plus_validator.errors, is_not(empty()))

    def test_validates_ids_lengths_are_equal_to_piece_count(
        self, sokoban_plus_validator
    ):
        sokoban_plus_validator._validate_ids_counts()
        assert_that(sokoban_plus_validator.errors, is_(empty()))
        sokoban_plus_validator.sokoban_plus._pieces_count = -42
        sokoban_plus_validator._validate_ids_counts()
        assert_that(sokoban_plus_validator.errors, is_not(empty()))

    def test_validates_same_id_set_is_defined_for_both_piece_types(
        self, sokoban_plus_validator
    ):
        sokoban_plus_validator._validate_id_sets_equality()
        assert_that(sokoban_plus_validator.errors, is_(empty()))
        sokoban_plus_validator.sokoban_plus._box_plus_ids = (
            sokoban_plus_validator.sokoban_plus._goal_plus_ids + [1, 2, 3]
        )
        sokoban_plus_validator._validate_id_sets_equality()
        assert_that(sokoban_plus_validator.errors, is_not(empty()))


    def test_it_allows_that_there_are_duplicate_plus_ids_for_same_piece_type(
        self
    ):
        sokoban_plus = SokobanPlusFactory(
            goalorder="1 1 2 2 3 3",
            boxorder="2 2 3 3 1 1",
            pieces_count=10
        )
        sokoban_plus._parse()
        validator = SokobanPlusValidator(sokoban_plus)

        assert_that(validator.is_valid, equal_to(True))
