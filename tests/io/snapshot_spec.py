from dataclasses import dataclass
from typing import List

import pytest

from sokoenginepy.game import Config, Direction, PusherStep, Tessellation
from sokoenginepy.io import Snapshot


@dataclass
class SnapshotConversionTestCase:
    tessellation: Tessellation
    illegal_directions: List[Direction]
    legal_directions: List[Direction]
    legal_moves: List[PusherStep]
    legal_characters: List[str]


@pytest.fixture
def sokoban_conversion_data():
    return SnapshotConversionTestCase(
        Tessellation.SOKOBAN,
        illegal_directions=[
            Direction.NORTH_WEST,
            Direction.NORTH_EAST,
            Direction.SOUTH_WEST,
            Direction.SOUTH_EAST,
        ],
        legal_directions=[
            Direction.LEFT,
            Direction.RIGHT,
            Direction.UP,
            Direction.DOWN,
        ],
        legal_moves=[
            PusherStep(Direction.LEFT, Config.NO_ID),
            PusherStep(Direction.RIGHT, Config.NO_ID),
            PusherStep(Direction.UP, Config.NO_ID),
            PusherStep(Direction.DOWN, Config.NO_ID),
            PusherStep(Direction.LEFT, Config.DEFAULT_ID),
            PusherStep(Direction.RIGHT, Config.DEFAULT_ID),
            PusherStep(Direction.UP, Config.DEFAULT_ID),
            PusherStep(Direction.DOWN, Config.DEFAULT_ID),
        ],
        legal_characters=["l", "r", "u", "d", "L", "R", "U", "D"],
    )


@pytest.fixture
def trioban_conversion_data():
    return SnapshotConversionTestCase(
        Tessellation.TRIOBAN,
        illegal_directions=[Direction.UP, Direction.DOWN],
        legal_directions=[
            Direction.LEFT,
            Direction.RIGHT,
            Direction.NORTH_WEST,
            Direction.NORTH_EAST,
            Direction.SOUTH_WEST,
            Direction.SOUTH_EAST,
        ],
        legal_moves=[
            PusherStep(Direction.LEFT, Config.NO_ID),
            PusherStep(Direction.RIGHT, Config.NO_ID),
            PusherStep(Direction.NORTH_WEST, Config.NO_ID),
            PusherStep(Direction.NORTH_EAST, Config.NO_ID),
            PusherStep(Direction.SOUTH_WEST, Config.NO_ID),
            PusherStep(Direction.SOUTH_EAST, Config.NO_ID),
            PusherStep(Direction.LEFT, Config.DEFAULT_ID),
            PusherStep(Direction.RIGHT, Config.DEFAULT_ID),
            PusherStep(Direction.NORTH_WEST, Config.DEFAULT_ID),
            PusherStep(Direction.NORTH_EAST, Config.DEFAULT_ID),
            PusherStep(Direction.SOUTH_WEST, Config.DEFAULT_ID),
            PusherStep(Direction.SOUTH_EAST, Config.DEFAULT_ID),
        ],
        legal_characters=["l", "r", "u", "n", "s", "d", "L", "R", "U", "N", "S", "D"],
    )


@pytest.fixture
def octoban_conversion_data():
    return SnapshotConversionTestCase(
        Tessellation.OCTOBAN,
        illegal_directions=[],
        legal_directions=[
            Direction.LEFT,
            Direction.RIGHT,
            Direction.UP,
            Direction.DOWN,
            Direction.NORTH_WEST,
            Direction.NORTH_EAST,
            Direction.SOUTH_WEST,
            Direction.SOUTH_EAST,
        ],
        legal_moves=[
            PusherStep(Direction.LEFT, Config.NO_ID),
            PusherStep(Direction.RIGHT, Config.NO_ID),
            PusherStep(Direction.UP, Config.NO_ID),
            PusherStep(Direction.DOWN, Config.NO_ID),
            PusherStep(Direction.NORTH_WEST, Config.NO_ID),
            PusherStep(Direction.NORTH_EAST, Config.NO_ID),
            PusherStep(Direction.SOUTH_WEST, Config.NO_ID),
            PusherStep(Direction.SOUTH_EAST, Config.NO_ID),
            PusherStep(Direction.LEFT, Config.DEFAULT_ID),
            PusherStep(Direction.RIGHT, Config.DEFAULT_ID),
            PusherStep(Direction.UP, Config.DEFAULT_ID),
            PusherStep(Direction.DOWN, Config.DEFAULT_ID),
            PusherStep(Direction.NORTH_WEST, Config.DEFAULT_ID),
            PusherStep(Direction.NORTH_EAST, Config.DEFAULT_ID),
            PusherStep(Direction.SOUTH_WEST, Config.DEFAULT_ID),
            PusherStep(Direction.SOUTH_EAST, Config.DEFAULT_ID),
        ],
        legal_characters=[
            "l",
            "r",
            "u",
            "d",
            "w",
            "n",
            "s",
            "e",
            "L",
            "R",
            "U",
            "D",
            "W",
            "N",
            "S",
            "E",
        ],
    )


@pytest.fixture
def hexoban_conversion_data():
    return SnapshotConversionTestCase(
        Tessellation.HEXOBAN,
        illegal_directions=[Direction.UP, Direction.DOWN],
        legal_directions=[
            Direction.LEFT,
            Direction.RIGHT,
            Direction.NORTH_WEST,
            Direction.NORTH_EAST,
            Direction.SOUTH_WEST,
            Direction.SOUTH_EAST,
        ],
        legal_moves=[
            PusherStep(Direction.LEFT, Config.NO_ID),
            PusherStep(Direction.RIGHT, Config.NO_ID),
            PusherStep(Direction.NORTH_WEST, Config.NO_ID),
            PusherStep(Direction.NORTH_EAST, Config.NO_ID),
            PusherStep(Direction.SOUTH_WEST, Config.NO_ID),
            PusherStep(Direction.SOUTH_EAST, Config.NO_ID),
            PusherStep(Direction.LEFT, Config.DEFAULT_ID),
            PusherStep(Direction.RIGHT, Config.DEFAULT_ID),
            PusherStep(Direction.NORTH_WEST, Config.DEFAULT_ID),
            PusherStep(Direction.NORTH_EAST, Config.DEFAULT_ID),
            PusherStep(Direction.SOUTH_WEST, Config.DEFAULT_ID),
            PusherStep(Direction.SOUTH_EAST, Config.DEFAULT_ID),
        ],
        legal_characters=["l", "r", "u", "n", "s", "d", "L", "R", "U", "N", "S", "D"],
    )


class DescribeSnapshot:
    def it_raises_immediately_on_invalid_characters(self):
        with pytest.raises(ValueError):
            Snapshot(Tessellation.SOKOBAN, "ZOMG!")

        snapshot = Snapshot(Tessellation.SOKOBAN)
        with pytest.raises(ValueError):
            snapshot.moves_data = "ZOMG!"

    def it_raises_delayed_on_invalid_groups(self):
        for data in [
            "lurd[lurd",
            "lurd]lurd",
            "lurd{lurd",
            "lurd}lurd",
        ]:
            snapshot = Snapshot(Tessellation.SOKOBAN, data)
            with pytest.raises(ValueError):
                # Trigger delayed parsing
                snapshot.moves_count

    def it_correctly_parses_regular_movement(self):
        data = "lurdLURDL"
        snapshot = Snapshot(Tessellation.SOKOBAN, data)

        assert snapshot.moves_count == 4
        assert snapshot.pushes_count == 5
        assert snapshot.jumps_count == 0
        assert not snapshot.is_reverse
        assert str(snapshot) == data
        assert str(snapshot) == snapshot.moves_data

    def it_ignores_spaces_in_input(self):
        data = "lu \t\r\nrdLU   \r\r\n\n\t\tRDL"
        snapshot = Snapshot(Tessellation.SOKOBAN, data)

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
            snapshot = Snapshot(Tessellation.SOKOBAN, data)

            assert snapshot.moves_count == 4
            assert snapshot.pushes_count == 5
            assert snapshot.jumps_count == 0
            assert not snapshot.is_reverse
            assert str(snapshot) == data
            assert str(snapshot) == snapshot.moves_data

        data = "[]lurdLURDD"
        snapshot = Snapshot(Tessellation.SOKOBAN, data)
        assert snapshot.moves_count == 4
        assert snapshot.pushes_count == 5
        assert snapshot.jumps_count == 1
        assert snapshot.is_reverse
        assert str(snapshot) == data
        assert str(snapshot) == snapshot.moves_data

    def it_doesnt_allow_pushes_in_pusher_selection(self):
        snapshot = Snapshot(Tessellation.SOKOBAN, "lurd{LURD}")
        with pytest.raises(ValueError):
            # Trigger delayed parsing
            snapshot.moves_count

    def it_correctly_parses_jumps(self):
        for data in [
            "[lurd]lurdLURDL",
            "lurd[lurd]LURDL",
            "lurdLURDL[lurd]",
        ]:
            snapshot = Snapshot(Tessellation.SOKOBAN, data)

            assert snapshot.moves_count == 8
            assert snapshot.pushes_count == 5
            assert snapshot.jumps_count == 1
            assert snapshot.is_reverse

    def it_correctly_prints_jumps(self):
        data = "[lurd]lurdLURDL"
        snapshot = Snapshot(Tessellation.SOKOBAN, data)
        assert str(snapshot) == data
        assert str(snapshot) == snapshot.moves_data

        data = "lurd[lurd]LURDL"
        snapshot = Snapshot(Tessellation.SOKOBAN, data)
        assert str(snapshot) == "[]" + data
        assert str(snapshot) == "[]" + snapshot.moves_data

        data = "lurdLURDL[lurd]"
        snapshot = Snapshot(Tessellation.SOKOBAN, data)
        assert str(snapshot) == "[]" + data
        assert str(snapshot) == "[]" + snapshot.moves_data

    def it_doesnt_allow_pushes_in_jumps(self):
        snapshot = Snapshot(Tessellation.SOKOBAN, "lurd[LURD]")
        with pytest.raises(ValueError):
            # Trigger delayed parsing
            snapshot.moves_count

    def it_correctly_converts_sequence_of_pusher_steps(self):
        snapshot = Snapshot(Tessellation.SOKOBAN)

        steps0 = [
            PusherStep(Direction.LEFT),
            PusherStep(Direction.UP),
            PusherStep(Direction.RIGHT),
            PusherStep(Direction.DOWN),
            PusherStep(Direction.LEFT, moved_box_id=Config.DEFAULT_ID),
            PusherStep(Direction.UP, moved_box_id=Config.DEFAULT_ID),
            PusherStep(Direction.RIGHT, moved_box_id=Config.DEFAULT_ID),
            PusherStep(Direction.DOWN, moved_box_id=Config.DEFAULT_ID),
            PusherStep(Direction.DOWN, moved_box_id=Config.DEFAULT_ID),
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

    def it_converts_legal_pusher_steps_to_characters(
        self,
        sokoban_conversion_data: SnapshotConversionTestCase,
        trioban_conversion_data: SnapshotConversionTestCase,
        hexoban_conversion_data: SnapshotConversionTestCase,
        octoban_conversion_data: SnapshotConversionTestCase,
    ):
        for data in [
            sokoban_conversion_data,
            trioban_conversion_data,
            hexoban_conversion_data,
            octoban_conversion_data,
        ]:
            for idx, pusher_step in enumerate(data.legal_moves):
                snapshot = Snapshot(data.tessellation)
                snapshot.pusher_steps = [pusher_step]
                assert str(snapshot) == data.legal_characters[idx]

    def it_raises_when_converting_illegal_direction(
        self,
        sokoban_conversion_data: SnapshotConversionTestCase,
        trioban_conversion_data: SnapshotConversionTestCase,
        hexoban_conversion_data: SnapshotConversionTestCase,
        octoban_conversion_data: SnapshotConversionTestCase,
    ):
        for data in [
            sokoban_conversion_data,
            trioban_conversion_data,
            hexoban_conversion_data,
            octoban_conversion_data,
        ]:
            for direction in data.illegal_directions:
                snapshot = Snapshot(data.tessellation)
                with pytest.raises(ValueError):
                    snapshot.pusher_steps = [PusherStep(direction, Config.NO_ID)]
                with pytest.raises(ValueError):
                    snapshot.pusher_steps = [PusherStep(direction, Config.DEFAULT_ID)]

    def it_converts_legal_characters_to_pusher_steps(
        self,
        sokoban_conversion_data: SnapshotConversionTestCase,
        trioban_conversion_data: SnapshotConversionTestCase,
        hexoban_conversion_data: SnapshotConversionTestCase,
        octoban_conversion_data: SnapshotConversionTestCase,
    ):
        for data in [
            sokoban_conversion_data,
            trioban_conversion_data,
            hexoban_conversion_data,
            octoban_conversion_data,
        ]:
            for idx, step_char in enumerate(data.legal_characters):
                snapshot = Snapshot(data.tessellation, moves_data=step_char)
                assert snapshot.pusher_steps[0] == data.legal_moves[idx]
