from typing import ClassVar, List

import pytest

from sokoenginepy.game import BaseTessellation, Config, Direction, PusherStep


class TessellationSpecMixin:
    illegal_directions: ClassVar[List[Direction]]
    legal_directions: ClassVar[List[Direction]]
    legal_moves: ClassVar[List[PusherStep]]
    legal_characters: ClassVar[List[str]]
    tessellation1: ClassVar[BaseTessellation]
    tessellation2: ClassVar[BaseTessellation]

    def test_converts_legal_pusher_steps_to_characters(self):
        for t in [self.tessellation1, self.tessellation2]:
            for index, pusher_step in enumerate(self.legal_moves):
                assert (
                    t.pusher_step_to_char(pusher_step) == self.legal_characters[index]
                )

    def test_converts_legal_characters_to_pusher_steps(self):
        for t in [self.tessellation1, self.tessellation2]:
            for index, pusher_step_str in enumerate(self.legal_characters):
                assert t.char_to_pusher_step(pusher_step_str) == self.legal_moves[index]

    def test_it_raises_on_illegal_character(self):
        for t in [self.tessellation1, self.tessellation2]:
            with pytest.raises(ValueError):
                t.char_to_pusher_step("z")

    def test_it_raises_when_converting_illegal_direction(self):
        for t in [self.tessellation1, self.tessellation2]:
            for illegal_direction in self.illegal_directions:
                move = PusherStep(illegal_direction, Config.NO_ID)
                with pytest.raises(ValueError):
                    t.pusher_step_to_char(move)
                push = PusherStep(illegal_direction, Config.DEFAULT_ID)
                with pytest.raises(ValueError):
                    t.pusher_step_to_char(push)

    def test_neighbor_raises_on_invalid_values(self):
        for t in [self.tessellation1, self.tessellation2]:
            with pytest.raises(IndexError):
                t.neighbor_position(-1, Direction.RIGHT, 2, 2)

            with pytest.raises(ValueError):
                t.neighbor_position(0, Direction.RIGHT, -1, 2)

            with pytest.raises(ValueError):
                t.neighbor_position(0, Direction.RIGHT, 2, -1)

    def test_cell_orientation_raises_on_invalid_values(self):
        for t in [self.tessellation1, self.tessellation2]:
            with pytest.raises(IndexError):
                t.cell_orientation(-1, 2, 2)

            with pytest.raises(ValueError):
                t.cell_orientation(0, -1, 2)

            with pytest.raises(ValueError):
                t.cell_orientation(0, 2, -1)
