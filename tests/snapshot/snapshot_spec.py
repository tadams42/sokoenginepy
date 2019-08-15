from unittest.mock import Mock

import pytest

from sokoenginepy import AtomicMove, Direction, Snapshot, SolvingMode, Tessellation

from ..fixtures import SnapshotFactory


@pytest.fixture
def forward_sokoban_snapshot():
    return SnapshotFactory(
        tessellation_or_description=Tessellation.SOKOBAN,
        moves_data="lurdLURD{lurd}LURD",
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
def reverse_sokoban_snapshot():
    return SnapshotFactory(
        tessellation_or_description=Tessellation.SOKOBAN,
        moves_data="lurdLURD{lurd}[lurd]LURD",
    )


@pytest.fixture
def jumps_count():
    return 1


@pytest.fixture
def sokoban_snapshot():
    return SnapshotFactory(
        tessellation_or_description=Tessellation.SOKOBAN,
        moves_data="lurdLURD{lurd}LURD",
    )


class DescribeGameSnapshot:
    class Describe_moves_count:
        def it_returns_total_count_of_atomic_non_pushes(
            self, forward_sokoban_snapshot, moves_count
        ):
            assert forward_sokoban_snapshot.moves_count == moves_count

        def test_returned_count_doesnt_include_moves_in_jumps_and_selections(
            self, forward_sokoban_snapshot, moves_count
        ):
            assert forward_sokoban_snapshot.moves_count == moves_count

    class Describe_init:
        def it_creates_empty_snapshot_by_default(self):
            snapshot = Snapshot(
                tessellation_or_description=Tessellation.SOKOBAN,
                solving_mode=SolvingMode.FORWARD,
            )
            assert len(snapshot) == 0
            assert snapshot.moves_count == 0
            assert snapshot.pushes_count == 0
            assert snapshot.jumps_count == 0

        def it_ignores_solving_mode_arg_if_moves_data_is_provided(self):
            assert (
                Snapshot(
                    tessellation_or_description=Tessellation.SOKOBAN,
                    moves_data="[lurd]",
                ).solving_mode
                == SolvingMode.REVERSE
            )
            assert (
                Snapshot(
                    tessellation_or_description=Tessellation.SOKOBAN, moves_data="lurd"
                ).solving_mode
                == SolvingMode.FORWARD
            )

    class Describe_get_item:
        def it_retrieves_single_atomic_move(self, forward_sokoban_snapshot):
            assert forward_sokoban_snapshot[0] == AtomicMove(Direction.LEFT)

        def it_retrieves_new_game_snapshot_from_slice(
            self, forward_sokoban_snapshot, reverse_sokoban_snapshot
        ):
            slice_of_snapshot = forward_sokoban_snapshot[0:4]
            assert isinstance(slice_of_snapshot, Snapshot)
            assert str(slice_of_snapshot) == "lurd"
            assert (
                slice_of_snapshot.solving_mode == forward_sokoban_snapshot.solving_mode
            )

            slice_of_snapshot = reverse_sokoban_snapshot[0:4]
            assert isinstance(slice_of_snapshot, Snapshot)
            assert str(slice_of_snapshot) == "[]lurd"
            assert (
                slice_of_snapshot.solving_mode == reverse_sokoban_snapshot.solving_mode
            )

    class Describe_set_item:
        def it_calls_recalc_methods_before_replacing_atomic_move(self, game_snapshot):
            game_snapshot._before_removing_move = Mock()
            game_snapshot._before_inserting_move = Mock()

            old_move = game_snapshot[3]
            new_move = AtomicMove(Direction.UP, box_moved=True)
            game_snapshot[3] = new_move

            assert game_snapshot[3] == new_move
            game_snapshot._before_removing_move.assert_called_once_with(old_move)
            game_snapshot._before_inserting_move.assert_called_once_with(new_move)

        def it_calls_recalc_methods_before_replacing_slice_of_moves(
            self, game_snapshot
        ):
            game_snapshot._before_removing_move = Mock()
            game_snapshot._before_inserting_move = Mock()

            old_moves = game_snapshot._moves[1:5]
            new_moves = [
                AtomicMove(Direction.UP, box_moved=True),
                AtomicMove(Direction.DOWN, box_moved=True),
            ]
            game_snapshot[1:5] = new_moves

            assert game_snapshot._moves[1:3] == new_moves
            assert game_snapshot._before_removing_move.call_count == len(old_moves)
            assert [
                mock_call[0][0]
                for mock_call in game_snapshot._before_removing_move.call_args_list
            ] == old_moves
            assert [
                mock_call[0][0]
                for mock_call in game_snapshot._before_inserting_move.call_args_list
            ] == new_moves

    class Describe_del_item:
        def it_calls_recalc_methods_before_deleting_atomic_move(self, game_snapshot):
            game_snapshot._before_removing_move = Mock()
            old_move = game_snapshot[3]
            del game_snapshot[3]
            game_snapshot._before_removing_move.assert_called_once_with(old_move)

        def it_calls_recalc_methods_before_deleting_slice_of_atomic_moves(
            self, game_snapshot
        ):
            game_snapshot._before_removing_move = Mock()

            old_moves = game_snapshot._moves[1:5]
            del game_snapshot[1:5]

            assert game_snapshot._before_removing_move.call_count == len(old_moves)
            assert [
                mock_call[0][0]
                for mock_call in game_snapshot._before_removing_move.call_args_list
            ] == old_moves

    class Describe_insert:
        def it_calls_recalc_methods_before_inserting_atomic_move(self, game_snapshot):
            game_snapshot._before_inserting_move = Mock()

            new_move = AtomicMove(Direction.UP, box_moved=True)
            game_snapshot.insert(3, new_move)

            game_snapshot._before_inserting_move.assert_called_once_with(new_move)

    class Describe_jumps_count:
        def it_calls_recalc_jumps_before_returning_value(self, game_snapshot):
            game_snapshot._recalculate_jumps_count = Mock()
            game_snapshot.jumps_count
            assert game_snapshot._recalculate_jumps_count.call_count == 1

    class Describe_clear:
        def it_resets_internal_counters(self, game_snapshot):
            game_snapshot.clear()
            assert game_snapshot.moves_count == 0
            assert game_snapshot.pushes_count == 0
            assert game_snapshot.jumps_count == 0

    class Describe_before_inserting_move:
        def it_increases_internal_counters_if_necessary(
            self,
            reverse_sokoban_snapshot,
            atomic_move,
            atomic_push,
            atomic_jump,
            atomic_pusher_selection,
        ):
            before = reverse_sokoban_snapshot.moves_count
            reverse_sokoban_snapshot._before_inserting_move(atomic_move)
            assert reverse_sokoban_snapshot.moves_count == before + 1

            before = reverse_sokoban_snapshot.pushes_count
            reverse_sokoban_snapshot._before_inserting_move(atomic_push)
            assert reverse_sokoban_snapshot.pushes_count == before + 1

            reverse_sokoban_snapshot._before_inserting_move(atomic_jump)
            assert reverse_sokoban_snapshot._jumps_count_invalidated is True

            before_moves, before_pushes, before_jumps_invalidate = (
                reverse_sokoban_snapshot.moves_count,
                reverse_sokoban_snapshot.pushes_count,
                reverse_sokoban_snapshot._jumps_count_invalidated,
            )
            reverse_sokoban_snapshot._before_inserting_move(atomic_pusher_selection)
            assert reverse_sokoban_snapshot.moves_count == before_moves
            assert reverse_sokoban_snapshot.pushes_count == before_pushes
            assert (
                reverse_sokoban_snapshot._jumps_count_invalidated
                == before_jumps_invalidate
            )

        def it_rises_on_move_direction_not_supported_by_snapshot_tessellation(
            self, sokoban_snapshot
        ):
            with pytest.raises(ValueError):
                sokoban_snapshot._before_inserting_move(
                    AtomicMove(Direction.NORTH_WEST)
                )

    class Describe_before_removing_move:
        def it_decreases_internal_counters_if_necessary(
            self,
            reverse_sokoban_snapshot,
            atomic_move,
            atomic_push,
            atomic_jump,
            atomic_pusher_selection,
        ):
            before = reverse_sokoban_snapshot.moves_count
            reverse_sokoban_snapshot._before_removing_move(atomic_move)
            assert reverse_sokoban_snapshot.moves_count == before - 1

            before = reverse_sokoban_snapshot.pushes_count
            reverse_sokoban_snapshot._before_removing_move(atomic_push)
            assert reverse_sokoban_snapshot.pushes_count == before - 1

            reverse_sokoban_snapshot._before_removing_move(atomic_jump)
            assert reverse_sokoban_snapshot._jumps_count_invalidated is True

            before_moves, before_pushes, before_jumps_invalidate = (
                reverse_sokoban_snapshot.moves_count,
                reverse_sokoban_snapshot.pushes_count,
                reverse_sokoban_snapshot._jumps_count_invalidated,
            )
            reverse_sokoban_snapshot._before_removing_move(atomic_pusher_selection)
            assert reverse_sokoban_snapshot.moves_count == before_moves
            assert reverse_sokoban_snapshot.pushes_count == before_pushes
            assert (
                reverse_sokoban_snapshot._jumps_count_invalidated
                == before_jumps_invalidate
            )

    class Describe_recalc_jumps_count:
        def it_recalcs_jumps_count_if_necessary(self, reverse_sokoban_snapshot):
            reverse_sokoban_snapshot._count_jumps = Mock()

            reverse_sokoban_snapshot._jumps_count_invalidated = False
            reverse_sokoban_snapshot._jumps_count = None
            reverse_sokoban_snapshot._recalculate_jumps_count()
            assert reverse_sokoban_snapshot._count_jumps.call_count == 0
            assert reverse_sokoban_snapshot._jumps_count is None

            reverse_sokoban_snapshot._jumps_count_invalidated = True
            reverse_sokoban_snapshot._jumps_count = 0
            reverse_sokoban_snapshot._recalculate_jumps_count()
            assert reverse_sokoban_snapshot._count_jumps.call_count == 1
            assert reverse_sokoban_snapshot._jumps_count is not None
            assert not reverse_sokoban_snapshot._jumps_count_invalidated

    class Describe_str:
        def it_ensures_starting_jump_sequence_for_reverse_mode_snapshots(
            self, reverse_sokoban_snapshot, atomic_jump, atomic_move
        ):
            reverse_sokoban_snapshot.clear()
            assert str(reverse_sokoban_snapshot) == "[]"

            reverse_sokoban_snapshot.append(atomic_jump)
            assert str(reverse_sokoban_snapshot) == "[l]"
            reverse_sokoban_snapshot.clear()

            reverse_sokoban_snapshot.append(atomic_move)
            reverse_sokoban_snapshot.append(atomic_jump)
            assert str(reverse_sokoban_snapshot) == "[]l[l]"
