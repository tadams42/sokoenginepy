import pytest

from sokoenginepy import AtomicMove


class TessellationSpecMixin:
    def test_converts_legal_atomic_moves_to_characters(self):
        for index, atomic_move in enumerate(self.legal_moves):
            assert (
                self.tessellation.atomic_move_to_char(atomic_move)
                == self.legal_characters[index]
            )

    def test_converts_legal_characters_to_atomic_moves(self):
        for index, atomic_move_str in enumerate(self.legal_characters):
            assert (
                self.tessellation.char_to_atomic_move(atomic_move_str)
                == self.legal_moves[index]
            )

    def test_it_raises_on_illegal_character(self):
        with pytest.raises(ValueError):
            self.tessellation.char_to_atomic_move("z")

    def test_it_raises_when_converting_illegal_direction(self):
        for index, illegal_direction in enumerate(self.illegal_directions):
            move = AtomicMove(illegal_direction, False)
            with pytest.raises(ValueError):
                self.tessellation.atomic_move_to_char(move)
            push = AtomicMove(illegal_direction, True)
            with pytest.raises(ValueError):
                self.tessellation.atomic_move_to_char(push)
