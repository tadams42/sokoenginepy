import pytest

from sokoenginepy.game import PusherStep


class TessellationSpecMixin:
    def test_converts_legal_pusher_steps_to_characters(self):
        for index, pusher_step in enumerate(self.legal_moves):
            assert (
                self.tessellation.pusher_step_to_char(pusher_step)
                == self.legal_characters[index]
            )

    def test_converts_legal_characters_to_pusher_steps(self):
        for index, pusher_step_str in enumerate(self.legal_characters):
            assert (
                self.tessellation.char_to_pusher_step(pusher_step_str)
                == self.legal_moves[index]
            )

    def test_it_raises_on_illegal_character(self):
        with pytest.raises(ValueError):
            self.tessellation.char_to_pusher_step("z")

    def test_it_raises_when_converting_illegal_direction(self):
        for index, illegal_direction in enumerate(self.illegal_directions):
            move = PusherStep(illegal_direction, False)
            with pytest.raises(ValueError):
                self.tessellation.pusher_step_to_char(move)
            push = PusherStep(illegal_direction, True)
            with pytest.raises(ValueError):
                self.tessellation.pusher_step_to_char(push)
