from unittest.mock import Mock

import pytest

from factories import GameSnapshotFactory
from sokoenginepy.common import Direction, SokoengineError, Variant
from sokoenginepy.game import GameSnapshot, GameSolvingMode
from sokoenginepy.snapshot import AtomicMove, SnapshotConversionError


@pytest.fixture
def forward_game_snapshot():
    return GameSnapshotFactory(
        variant=Variant.SOKOBAN, moves_data="lurdLURD{lurd}LURD"
    )


@pytest.fixture
def moves_count():
    return 4


@pytest.fixture
def pushes_count():
    return 8


@pytest.fixture
def pusher_selections_count():
    return 1


@pytest.fixture
def reverse_game_snapshot():
    return GameSnapshotFactory(
        variant=Variant.SOKOBAN, moves_data="lurdLURD{lurd}[lurd]LURD"
    )


@pytest.fixture
def jumps_count():
    return 1


@pytest.fixture
def sokoban_game_snapshot():
    return GameSnapshotFactory(
        variant=Variant.SOKOBAN, moves_data="lurdLURD{lurd}LURD"
    )


class DescribeGameSnapshot:

    class Describe_moves_count:

        def it_returns_total_count_of_atomic_non_pushes(
            self, forward_game_snapshot, moves_count
        ):
            assert forward_game_snapshot.moves_count == moves_count

        def test_returned_count_doesnt_include_moves_in_jumps_and_selections(
            self, forward_game_snapshot, moves_count
        ):
            assert forward_game_snapshot.moves_count == moves_count

    class Describe_init:

        def it_creates_sokoban_snapshot_by_default(self):
            assert GameSnapshot().variant == Variant.SOKOBAN

        def it_creates_forward_snaphost_by_default(self):
            assert GameSnapshot().solving_mode == GameSolvingMode.FORWARD

        def it_creates_empty_snapshot_by_default(self):
            assert len(GameSnapshot()) == 0
            assert GameSnapshot().moves_count == 0
            assert GameSnapshot().pushes_count == 0
            assert GameSnapshot().jumps_count == 0

        def it_ignores_solving_mode_arg_if_moves_data_is_provided(self):
            assert GameSnapshot(
                solving_mode=GameSolvingMode.FORWARD, moves_data="[lurd]"
            ).solving_mode == GameSolvingMode.REVERSE
            assert GameSnapshot(
                solving_mode=GameSolvingMode.REVERSE, moves_data="lurd"
            ).solving_mode == GameSolvingMode.FORWARD

    class Describe_get_item:

        def it_retrieves_single_atomic_move(self, forward_game_snapshot):
            assert forward_game_snapshot[0] == AtomicMove(Direction.LEFT)

        def it_retrieves_new_game_snapshot_from_slice(
            self, forward_game_snapshot, reverse_game_snapshot
        ):
            slice_of_snapshot = forward_game_snapshot[0:4]
            assert isinstance(slice_of_snapshot, GameSnapshot)
            assert slice_of_snapshot.to_s() == 'lurd'
            assert slice_of_snapshot.solving_mode == forward_game_snapshot.solving_mode

            slice_of_snapshot = reverse_game_snapshot[0:4]
            assert isinstance(slice_of_snapshot, GameSnapshot)
            assert slice_of_snapshot.to_s() == '[]lurd'
            assert slice_of_snapshot.solving_mode == reverse_game_snapshot.solving_mode

    class Describe_set_item:

        def it_calls_recalc_methods_before_replacing_atomic_move(
            self, game_snapshot
        ):
            game_snapshot._before_removing_move = Mock()
            game_snapshot._before_inserting_move = Mock()

            old_move = game_snapshot[3]
            new_move = AtomicMove(Direction.UP, box_moved=True)
            game_snapshot[3] = new_move

            assert game_snapshot[3] == new_move
            game_snapshot._before_removing_move.assert_called_once_with(
                old_move
            )
            game_snapshot._before_inserting_move.assert_called_once_with(
                new_move
            )

        def it_calls_recalc_methods_before_replacing_slice_of_moves(
            self, game_snapshot
        ):
            game_snapshot._before_removing_move = Mock()
            game_snapshot._before_inserting_move = Mock()

            old_moves = game_snapshot._moves[1:5]
            new_moves = [
                AtomicMove(
                    Direction.UP, box_moved=True
                ),
                AtomicMove(
                    Direction.DOWN, box_moved=True
                ),
            ]
            game_snapshot[1:5] = new_moves

            assert game_snapshot._moves[1:3] == new_moves
            assert game_snapshot._before_removing_move.call_count == len(
                old_moves
            )
            assert [
                mock_call[0][0]
                for mock_call in
                game_snapshot._before_removing_move.call_args_list
            ] == old_moves
            assert [
                mock_call[0][0]
                for mock_call in
                game_snapshot._before_inserting_move.call_args_list
            ] == new_moves

    class Describe_del_item:

        def it_calls_recalc_methods_before_deleting_atomic_move(
            self, game_snapshot
        ):
            game_snapshot._before_removing_move = Mock()
            old_move = game_snapshot[3]
            del (game_snapshot[3])
            game_snapshot._before_removing_move.assert_called_once_with(
                old_move
            )

        def it_calls_recalc_methods_before_deleting_slice_of_atomic_moves(
            self, game_snapshot
        ):
            game_snapshot._before_removing_move = Mock()

            old_moves = game_snapshot._moves[1:5]
            del (game_snapshot[1:5])

            assert game_snapshot._before_removing_move.call_count == len(
                old_moves
            )
            assert [
                mock_call[0][0]
                for mock_call in
                game_snapshot._before_removing_move.call_args_list
            ] == old_moves

    class Describe_insert:

        def it_calls_recalc_methods_before_inserting_atomic_move(
            self, game_snapshot
        ):
            game_snapshot._before_inserting_move = Mock()

            new_move = AtomicMove(Direction.UP, box_moved=True)
            game_snapshot.insert(3, new_move)

            game_snapshot._before_inserting_move.assert_called_once_with(
                new_move
            )

    class Describe_jumps_count:

        def it_calls_recalc_jumps_before_returning_value(self, game_snapshot):
            game_snapshot._recalc_jumps_count = Mock()
            game_snapshot.jumps_count
            assert game_snapshot._recalc_jumps_count.call_count == 1

    class Describe_clear:

        def it_resets_internal_counters(self, game_snapshot):
            game_snapshot.clear()
            assert game_snapshot.moves_count == 0
            assert game_snapshot.pushes_count == 0
            assert game_snapshot.jumps_count == 0

    class Describe_before_inserting_move:

        def it_increases_internal_counters_if_necessary(
            self, reverse_game_snapshot, atomic_move, atomic_push, atomic_jump,
            atomic_pusher_selection
        ):
            before = reverse_game_snapshot.moves_count
            reverse_game_snapshot._before_inserting_move(atomic_move)
            assert reverse_game_snapshot.moves_count == before + 1

            before = reverse_game_snapshot.pushes_count
            reverse_game_snapshot._before_inserting_move(atomic_push)
            assert reverse_game_snapshot.pushes_count == before + 1

            reverse_game_snapshot._before_inserting_move(atomic_jump)
            assert reverse_game_snapshot._jumps_count_invalidated == True

            before_moves, before_pushes, before_jumps_invalidate = (
                reverse_game_snapshot.moves_count,
                reverse_game_snapshot.pushes_count,
                reverse_game_snapshot._jumps_count_invalidated
            )
            reverse_game_snapshot._before_inserting_move(
                atomic_pusher_selection
            )
            assert reverse_game_snapshot.moves_count == before_moves
            assert reverse_game_snapshot.pushes_count == before_pushes
            assert reverse_game_snapshot._jumps_count_invalidated == before_jumps_invalidate

        def it_rises_on_move_direction_not_supported_by_snapshot_tessellation(
            self, sokoban_game_snapshot
        ):
            with pytest.raises(SokoengineError):
                sokoban_game_snapshot._before_inserting_move(
                    AtomicMove(Direction.NORTH_WEST)
                )

    class Describe_before_removing_move:

        def it_decreases_internal_counters_if_necessary(
            self, reverse_game_snapshot, atomic_move, atomic_push, atomic_jump,
            atomic_pusher_selection
        ):
            before = reverse_game_snapshot.moves_count
            reverse_game_snapshot._before_removing_move(atomic_move)
            assert reverse_game_snapshot.moves_count == before - 1

            before = reverse_game_snapshot.pushes_count
            reverse_game_snapshot._before_removing_move(atomic_push)
            assert reverse_game_snapshot.pushes_count == before - 1

            reverse_game_snapshot._before_removing_move(atomic_jump)
            assert reverse_game_snapshot._jumps_count_invalidated == True

            before_moves, before_pushes, before_jumps_invalidate = (
                reverse_game_snapshot.moves_count,
                reverse_game_snapshot.pushes_count,
                reverse_game_snapshot._jumps_count_invalidated
            )
            reverse_game_snapshot._before_removing_move(atomic_pusher_selection)
            assert reverse_game_snapshot.moves_count == before_moves
            assert reverse_game_snapshot.pushes_count == before_pushes
            assert reverse_game_snapshot._jumps_count_invalidated == before_jumps_invalidate

    class Describe_recalc_jumps_count:

        def it_recalcs_jumps_count_if_necessary(self, reverse_game_snapshot):
            reverse_game_snapshot._count_jumps = Mock()

            reverse_game_snapshot._jumps_count_invalidated = False
            reverse_game_snapshot._jumps_count = None
            reverse_game_snapshot._recalc_jumps_count()
            assert reverse_game_snapshot._count_jumps.call_count == 0
            assert reverse_game_snapshot._jumps_count is None

            reverse_game_snapshot._jumps_count_invalidated = True
            reverse_game_snapshot._jumps_count = 0
            reverse_game_snapshot._recalc_jumps_count()
            assert reverse_game_snapshot._count_jumps.call_count == 1
            assert reverse_game_snapshot._jumps_count is not None
            assert not reverse_game_snapshot._jumps_count_invalidated

    class Describe_parse_string:

        def it_replaces_internal_data_with_atomic_moves_from_string(
            self, sokoban_game_snapshot
        ):
            sokoban_game_snapshot._parse_string("LURD")
            assert len(sokoban_game_snapshot) == 4
            assert sokoban_game_snapshot[0] == AtomicMove(
                Direction.LEFT, box_moved=True
            )
            assert sokoban_game_snapshot[1] == AtomicMove(
                Direction.UP, box_moved=True
            )
            assert sokoban_game_snapshot[2] == AtomicMove(
                Direction.RIGHT, box_moved=True
            )
            assert sokoban_game_snapshot[3] == AtomicMove(
                Direction.DOWN, box_moved=True
            )

        def it_raises_on_parsing_errors(self, sokoban_game_snapshot):
            with pytest.raises(SnapshotConversionError):
                sokoban_game_snapshot._parse_string(moves_data="42")

    class Describe_to_s:

        def it_ensures_starting_jump_sequence_for_reverse_mode_snapshots(
            self, reverse_game_snapshot, atomic_jump, atomic_move
        ):
            reverse_game_snapshot.clear()
            assert reverse_game_snapshot.to_s() == "[]"

            reverse_game_snapshot.append(atomic_jump)
            assert reverse_game_snapshot.to_s() == "[l]"
            reverse_game_snapshot.clear()

            reverse_game_snapshot.append(atomic_move)
            reverse_game_snapshot.append(atomic_jump)
            assert reverse_game_snapshot.to_s() == "[]l[l]"
