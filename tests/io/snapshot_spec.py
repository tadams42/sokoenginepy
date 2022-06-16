import pytest

from sokoenginepy.game import Direction, PusherStep
from sokoenginepy.io import SokobanSnapshot


class DescribeSnapshot:
    def it_raises_immediately_on_invalid_characters(self):
        with pytest.raises(ValueError):
            SokobanSnapshot("ZOMG!")

        snapshot = SokobanSnapshot()
        with pytest.raises(ValueError):
            snapshot.moves_data = "ZOMG!"

    def it_raises_delayed_on_invalid_groups(self):
        for data in [
            "lurd[lurd",
            "lurd]lurd",
            "lurd{lurd",
            "lurd}lurd",
        ]:
            snapshot = SokobanSnapshot(data)
            with pytest.raises(ValueError):
                # Trigger delayed parsing
                snapshot.moves_count

    def it_correctly_parses_regular_movement(self):
        data = "lurdLURDL"
        snapshot = SokobanSnapshot(data)

        assert snapshot.moves_count == 4
        assert snapshot.pushes_count == 5
        assert snapshot.jumps_count == 0
        assert not snapshot.is_reverse
        assert str(snapshot) == data
        assert str(snapshot) == snapshot.moves_data

    def it_ignores_spaces_in_input(self):
        data = "lu \t\r\nrdLU   \r\r\n\n\t\tRDL"
        snapshot = SokobanSnapshot(data)

        assert snapshot.moves_count == 4
        assert snapshot.pushes_count == 5
        assert snapshot.jumps_count == 0
        assert not snapshot.is_reverse
        assert str(snapshot) == "lurdLURDL"
        assert snapshot.moves_data == data

    def it_correctly_parses_pusher_selections(self):
        for data in [
            "{lurd}lurdLURDL",
            "lurd{lurd}LURDL",
            "lurdLURDL{lurd}",
        ]:
            snapshot = SokobanSnapshot(data)

            assert snapshot.moves_count == 4
            assert snapshot.pushes_count == 5
            assert snapshot.jumps_count == 0
            assert not snapshot.is_reverse
            assert str(snapshot) == data
            assert str(snapshot) == snapshot.moves_data

        data = "[]lurdLURDD"
        snapshot = SokobanSnapshot(data)
        assert snapshot.moves_count == 4
        assert snapshot.pushes_count == 5
        assert snapshot.jumps_count == 1
        assert snapshot.is_reverse
        assert str(snapshot) == data
        assert str(snapshot) == snapshot.moves_data

    def it_doesnt_allow_pushes_in_pusher_selection(self):
        snapshot = SokobanSnapshot("lurd{LURD}")
        with pytest.raises(ValueError):
            # Trigger delayed parsing
            snapshot.moves_count

    def it_correctly_parses_jumps(self):
        for data in [
            "[lurd]lurdLURDL",
            "lurd[lurd]LURDL",
            "lurdLURDL[lurd]",
        ]:
            snapshot = SokobanSnapshot(data)

            assert snapshot.moves_count == 8
            assert snapshot.pushes_count == 5
            assert snapshot.jumps_count == 1
            assert snapshot.is_reverse

    def it_correctly_prints_jumps(self):
        data = "[lurd]lurdLURDL"
        snapshot = SokobanSnapshot(data)
        assert str(snapshot) == data
        assert str(snapshot) == snapshot.moves_data

        data = "lurd[lurd]LURDL"
        snapshot = SokobanSnapshot(data)
        assert str(snapshot) == "[]" + data
        assert str(snapshot) == "[]" + snapshot.moves_data

        data = "lurdLURDL[lurd]"
        snapshot = SokobanSnapshot(data)
        assert str(snapshot) == "[]" + data
        assert str(snapshot) == "[]" + snapshot.moves_data

    def it_doesnt_allow_pushes_in_jumps(self):
        snapshot = SokobanSnapshot("lurd[LURD]")
        with pytest.raises(ValueError):
            # Trigger delayed parsing
            snapshot.moves_count

    def it_correctly_converts_sequence_of_pusher_steps(self):
        snapshot = SokobanSnapshot()

        steps0 = [
            PusherStep(Direction.LEFT),
            PusherStep(Direction.UP),
            PusherStep(Direction.RIGHT),
            PusherStep(Direction.DOWN),
            PusherStep(Direction.LEFT, box_moved=True),
            PusherStep(Direction.UP, box_moved=True),
            PusherStep(Direction.RIGHT, box_moved=True),
            PusherStep(Direction.DOWN, box_moved=True),
            PusherStep(Direction.DOWN, box_moved=True),
        ]

        steps = steps0
        snapshot.pusher_steps = steps
        assert str(snapshot) == "lurdLURDD"
        assert snapshot.moves_count == 4
        assert snapshot.pushes_count == 5
        assert snapshot.jumps_count == 0
        assert not snapshot.is_reverse

        steps = steps0 + [
            PusherStep(Direction.LEFT, is_jump=True),
            PusherStep(Direction.UP, is_jump=True),
            PusherStep(Direction.RIGHT, is_jump=True),
            PusherStep(Direction.DOWN, is_jump=True),
        ]
        snapshot.pusher_steps = steps
        assert str(snapshot) == "[]lurdLURDD[lurd]"
        assert snapshot.moves_count == 8
        assert snapshot.pushes_count == 5
        assert snapshot.jumps_count == 1
        assert snapshot.is_reverse

        steps = steps0 + [
            PusherStep(Direction.LEFT, is_pusher_selection=True),
            PusherStep(Direction.UP, is_pusher_selection=True),
            PusherStep(Direction.RIGHT, is_pusher_selection=True),
            PusherStep(Direction.DOWN, is_pusher_selection=True),
        ]
        snapshot.pusher_steps = steps
        assert str(snapshot) == "lurdLURDD{lurd}"
        assert snapshot.moves_count == 4
        assert snapshot.pushes_count == 5
        assert snapshot.jumps_count == 0
        assert not snapshot.is_reverse
