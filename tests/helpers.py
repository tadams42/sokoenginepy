from inspect import getsourcefile
from os.path import abspath

import pytest
from faker import Faker
from unipath import Path

from sokoenginepy.common import UnknownDirectionError
from sokoenginepy.snapshot import AtomicMove

TEST_RESOURCES_ROOT = (
    Path(abspath(getsourcefile(lambda: 0))).ancestor(1).child('res')
)

fake = Faker()


class TessellationSpecMixin:

    def test_converts_legal_atomic_moves_to_characters(self):
        for index, atomic_move in enumerate(self.legal_moves):
            assert (
                self.tessellation.atomic_move_to_char(atomic_move) ==
                self.legal_characters[index]
            )

    def test_converts_legal_characters_to_atomic_moves(self):
        for index, atomic_move_str in enumerate(self.legal_characters):
            assert (
                self.tessellation.char_to_atomic_move(atomic_move_str) ==
                self.legal_moves[index]
            )

    def test_it_raises_on_illegal_character(self):
        with pytest.raises(UnknownDirectionError):
            self.tessellation.char_to_atomic_move('z')

    def test_it_raises_when_converting_illegal_direction(self):
        for index, illegal_direction in enumerate(self.illegal_directions):
            move = AtomicMove(illegal_direction, False)
            with pytest.raises(UnknownDirectionError):
                self.tessellation.atomic_move_to_char(move)
            push = AtomicMove(illegal_direction, True)
            with pytest.raises(UnknownDirectionError):
                self.tessellation.atomic_move_to_char(push)
