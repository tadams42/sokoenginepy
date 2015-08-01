import pytest
from factories import GameSnapshotFactory
from hamcrest import assert_that, equal_to, instance_of, is_, none, is_not
from sokoenginepy import (
    GameSnapshot, Variant, GameSolvingMode, AtomicMove, Direction,
    SokoengineError, SnapshotConversionError
)
from unittest.mock import Mock


@pytest.fixture
def forward_game_snapshot():
    return GameSnapshotFactory(
        variant=Variant.SOKOBAN,
        moves_data="lurdLURD{lurd}LURD"
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
        variant=Variant.SOKOBAN,
        moves_data="lurdLURD{lurd}[lurd]LURD"
    )

@pytest.fixture
def jumps_count():
    return 1

@pytest.fixture
def sokoban_game_snapshot():
    return GameSnapshotFactory(
        variant=Variant.SOKOBAN,
        moves_data="lurdLURD{lurd}LURD"
    )

class DescribeGameSnapshot(object):
    class Describe_moves_count(object):
        def test_it_returns_total_count_of_atomic_non_pushes(
            self, forward_game_snapshot, moves_count
        ):
            assert_that(forward_game_snapshot.moves_count, equal_to(moves_count))

        def test_returned_count_doesnt_include_moves_in_jumps_and_selections(
            self, forward_game_snapshot, moves_count
        ):

            assert_that(forward_game_snapshot.moves_count, equal_to(moves_count))

    class Describe_init(object):
        def test_it_creates_sokoban_snapshot_by_default(self):
            assert_that(
                GameSnapshot().variant,
                equal_to(Variant.SOKOBAN)
            )

        def test_it_creates_forward_snaphost_by_default(self):
            assert_that(
                GameSnapshot().solving_mode,
                equal_to(GameSolvingMode.FORWARD)
            )

        def test_it_creates_empty_snapshot_by_default(self):
            assert_that(len(GameSnapshot()), equal_to(0))
            assert_that(GameSnapshot().moves_count, equal_to(0))
            assert_that(GameSnapshot().pushes_count, equal_to(0))
            assert_that(GameSnapshot().jumps_count, equal_to(0))

        def test_it_ignores_solving_mode_arg_if_moves_data_is_provided(self):
            assert_that(
                GameSnapshot(
                    solving_mode=GameSolvingMode.FORWARD, moves_data="[lurd]"
                ).solving_mode,
                equal_to(GameSolvingMode.REVERSE)
            )
            assert_that(
                GameSnapshot(
                    solving_mode=GameSolvingMode.REVERSE, moves_data="lurd"
                ).solving_mode,
                equal_to(GameSolvingMode.FORWARD)
            )

    class Describe_get_item(object):
        def test_it_retrieves_single_atomic_move(self, forward_game_snapshot):
            assert_that(
                forward_game_snapshot[0],
                equal_to(AtomicMove(Direction.LEFT))
            )

        def test_it_retrieves_new_game_snapshot_from_slice(
            self, forward_game_snapshot, reverse_game_snapshot
        ):
            slice_of_snapshot = forward_game_snapshot[0:4]
            assert_that(slice_of_snapshot, instance_of(GameSnapshot))
            assert_that(slice_of_snapshot.to_s(), equal_to('lurd'))
            assert_that(slice_of_snapshot.solving_mode, equal_to(
                forward_game_snapshot.solving_mode
            ))

            slice_of_snapshot = reverse_game_snapshot[0:4]
            assert_that(slice_of_snapshot, instance_of(GameSnapshot))
            assert_that(slice_of_snapshot.to_s(), equal_to('[]lurd'))
            assert_that(slice_of_snapshot.solving_mode, equal_to(
                reverse_game_snapshot.solving_mode
            ))

    class Describe_set_item(object):
        def test_it_calls_recalc_methods_before_replacing_atomic_move(
            self, game_snapshot
        ):
            game_snapshot._before_removing_move = Mock()
            game_snapshot._before_inserting_move = Mock()

            old_move = game_snapshot[3]
            new_move = AtomicMove(Direction.UP, box_moved=True)
            game_snapshot[3] = new_move

            assert_that(game_snapshot[3], equal_to(new_move))
            game_snapshot._before_removing_move.assert_called_once_with(old_move)
            game_snapshot._before_inserting_move.assert_called_once_with(new_move)

        def test_it_calls_recalc_methods_before_replacing_slice_of_moves(
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

            assert_that(
                game_snapshot._moves[1:3], equal_to(new_moves)
            )
            assert_that(
                game_snapshot._before_removing_move.call_count,
                equal_to(len(old_moves))
            )
            assert_that(
                [
                    mock_call[0][0] for mock_call
                    in game_snapshot._before_removing_move.call_args_list
                ],
                equal_to(old_moves)
            )
            assert_that(
                [
                    mock_call[0][0] for mock_call
                    in game_snapshot._before_inserting_move.call_args_list
                ],
                equal_to(new_moves)
            )

    class Describe_del_item(object):
        def test_it_calls_recalc_methods_before_deleting_atomic_move(
            self, game_snapshot
        ):
            game_snapshot._before_removing_move = Mock()
            old_move = game_snapshot[3]
            del(game_snapshot[3])
            game_snapshot._before_removing_move.assert_called_once_with(old_move)

        def test_it_calls_recalc_methods_before_deleting_slice_of_atomic_moves(
            self, game_snapshot
        ):
            game_snapshot._before_removing_move = Mock()

            old_moves = game_snapshot._moves[1:5]
            del(game_snapshot[1:5])

            assert_that(
                game_snapshot._before_removing_move.call_count,
                equal_to(len(old_moves))
            )
            assert_that(
                [
                    mock_call[0][0] for mock_call
                    in game_snapshot._before_removing_move.call_args_list
                ],
                equal_to(old_moves)
            )

    class Describe_insert(object):
        def test_it_calls_recalc_methods_before_inserting_atomic_move(
            self, game_snapshot
        ):
            game_snapshot._before_inserting_move = Mock()

            new_move = AtomicMove(Direction.UP, box_moved=True)
            game_snapshot.insert(3, new_move)

            game_snapshot._before_inserting_move.assert_called_once_with(new_move)

    class Describe_jumps_count(object):
        def test_it_calls_recalc_jumps_before_returning_value(self, game_snapshot):
            game_snapshot._recalc_jumps_count = Mock()
            game_snapshot.jumps_count
            game_snapshot._recalc_jumps_count.assert_called_once()

    class Describe_clear(object):
        def test_it_resets_internal_counters(self, game_snapshot):
            game_snapshot.clear()
            assert_that(game_snapshot.moves_count, equal_to(0))
            assert_that(game_snapshot.pushes_count, equal_to(0))
            assert_that(game_snapshot.jumps_count, equal_to(0))

    class Describe_before_inserting_move(object):
        def test_it_increases_internal_counters_if_necessary(
            self, reverse_game_snapshot, atomic_move, atomic_push, atomic_jump,
            atomic_pusher_selection
        ):
            before = reverse_game_snapshot.moves_count
            reverse_game_snapshot._before_inserting_move(atomic_move)
            assert_that(reverse_game_snapshot.moves_count, equal_to(before + 1))

            before = reverse_game_snapshot.pushes_count
            reverse_game_snapshot._before_inserting_move(atomic_push)
            assert_that(reverse_game_snapshot.pushes_count, equal_to(before + 1))

            reverse_game_snapshot._before_inserting_move(atomic_jump)
            assert_that(
                reverse_game_snapshot._jumps_count_invalidated,
                equal_to(True)
            )

            before_moves, before_pushes, before_jumps_invalidate = (
                reverse_game_snapshot.moves_count,
                reverse_game_snapshot.pushes_count,
                reverse_game_snapshot._jumps_count_invalidated
            )
            reverse_game_snapshot._before_inserting_move(atomic_pusher_selection)
            assert_that(reverse_game_snapshot.moves_count, equal_to(before_moves))
            assert_that(reverse_game_snapshot.pushes_count, equal_to(before_pushes))
            assert_that(
                reverse_game_snapshot._jumps_count_invalidated,
                equal_to(before_jumps_invalidate)
            )

        def test_it_rises_on_move_direction_not_supported_by_snapshot_tessellation(
            self, sokoban_game_snapshot
        ):
            with pytest.raises(SokoengineError):
                sokoban_game_snapshot._before_inserting_move(
                    AtomicMove(Direction.NORTH_WEST)
                )

    class Describe_before_removing_move(object):
        def test_it_decreases_internal_counters_if_necessary(
            self, reverse_game_snapshot, atomic_move, atomic_push, atomic_jump,
            atomic_pusher_selection
        ):
            before = reverse_game_snapshot.moves_count
            reverse_game_snapshot._before_removing_move(atomic_move)
            assert_that(reverse_game_snapshot.moves_count, equal_to(before - 1))

            before = reverse_game_snapshot.pushes_count
            reverse_game_snapshot._before_removing_move(atomic_push)
            assert_that(reverse_game_snapshot.pushes_count, equal_to(before - 1))

            reverse_game_snapshot._before_removing_move(atomic_jump)
            assert_that(
                reverse_game_snapshot._jumps_count_invalidated,
                equal_to(True)
            )

            before_moves, before_pushes, before_jumps_invalidate = (
                reverse_game_snapshot.moves_count,
                reverse_game_snapshot.pushes_count,
                reverse_game_snapshot._jumps_count_invalidated
            )
            reverse_game_snapshot._before_removing_move(atomic_pusher_selection)
            assert_that(reverse_game_snapshot.moves_count, equal_to(before_moves))
            assert_that(reverse_game_snapshot.pushes_count, equal_to(before_pushes))
            assert_that(
                reverse_game_snapshot._jumps_count_invalidated,
                equal_to(before_jumps_invalidate)
            )

    class Describe_recalc_jumps_count(object):
        def test_it_recalcs_jumps_count_if_necessary(
            self, reverse_game_snapshot
        ):
            reverse_game_snapshot._count_jumps = Mock()

            reverse_game_snapshot._jumps_count_invalidated = False
            reverse_game_snapshot._jumps_count = None
            reverse_game_snapshot._recalc_jumps_count()
            assert_that(reverse_game_snapshot._count_jumps.call_count, equal_to(0))
            assert_that(reverse_game_snapshot._jumps_count, is_(none()))

            reverse_game_snapshot._jumps_count_invalidated = True
            reverse_game_snapshot._jumps_count = 0
            reverse_game_snapshot._recalc_jumps_count()
            assert_that(reverse_game_snapshot._count_jumps.call_count, equal_to(1))
            assert_that(reverse_game_snapshot._jumps_count, is_not(none()))
            assert_that(reverse_game_snapshot._jumps_count_invalidated, equal_to(False))

    class Describe_parse_string(object):
        def test_it_replaces_internal_data_with_atomic_moves_from_string(
            self, sokoban_game_snapshot
        ):
            sokoban_game_snapshot._parse_string("LURD")
            assert_that(len(sokoban_game_snapshot), equal_to(4))
            assert_that(sokoban_game_snapshot[0], equal_to(AtomicMove(Direction.LEFT, box_moved=True)))
            assert_that(sokoban_game_snapshot[1], equal_to(AtomicMove(Direction.UP, box_moved=True)))
            assert_that(sokoban_game_snapshot[2], equal_to(AtomicMove(Direction.RIGHT, box_moved=True)))
            assert_that(sokoban_game_snapshot[3], equal_to(AtomicMove(Direction.DOWN, box_moved=True)))

        def test_it_raises_on_parsing_errors(self, sokoban_game_snapshot):
            with pytest.raises(SnapshotConversionError):
                sokoban_game_snapshot._parse_string(
                    moves_data="42"
                )

    class Describe_to_s(object):
        def test_it_ensures_starting_jump_sequence_for_reverse_mode_snapshots(
            self, reverse_game_snapshot, atomic_jump, atomic_move
        ):
            reverse_game_snapshot.clear()
            assert_that(reverse_game_snapshot.to_s(), equal_to("[]"))

            reverse_game_snapshot.append(atomic_jump)
            assert_that(reverse_game_snapshot.to_s(), equal_to("[l]"))
            reverse_game_snapshot.clear()

            reverse_game_snapshot.append(atomic_move)
            reverse_game_snapshot.append(atomic_jump)
            assert_that(reverse_game_snapshot.to_s(), equal_to("[]l[l]"))
