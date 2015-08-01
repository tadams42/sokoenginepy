from functools import reduce

from ..core import Variant

from .text_utils import (
    is_pusher, is_box, is_goal, is_atomic_move_char, SpecialSnapshotCharacters
)
from .output_settings import OutputSettings


class Puzzle(object):
    """
    Board with all its meta data and snapshots.

    No data validation is performed, to make parsing of Sokoban files as fast
    as possible. Proper validation is triggered when Puzzle is converted into
    GameBoard.
    """

    def __init__(
        self, board="", variant=Variant.SOKOBAN, title="", author="", boxorder="",
        goalorder="", notes="", snapshots=[], created_at="", updated_at=""
    ):
        self.id = 1
        self.board = board
        self.variant = variant
        self.title = title
        self.author = author
        self.boxorder = boxorder
        self.goalorder = goalorder
        self.notes = notes
        self.snapshots = snapshots
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def variant(self):
        return self._variant

    @variant.setter
    def variant(self, value):
        self._variant = Variant.factory(value)

    def clear(self):
        self.board = ""
        self.variant = Variant.SOKOBAN
        self.title = ""
        self.author = ""
        self.boxorder = ""
        self.goalorder = ""
        self.notes = ""
        self.snapshots = []
        self.created_at = ""
        self.updated_at = ""

    def reformat(self, output_settings=OutputSettings()):
        self.board = self.to_game_board().to_s(output_settings)
        for snapshot in self.snapshots:
            snapshot.reformat(output_settings)

    def to_game_board(self):
        from ..game import GameBoard
        retv = GameBoard(board_str=self.board, variant=self.variant)
        retv.sokoban_plus = (self.boxorder, self.goalorder)
        return retv

    def pushers_count(self):
        reduce(
            lambda x, y: x + y,
            [1 if is_pusher(chr) else 0 for chr in self.board],
            0
        )

    def boxes_count(self):
        reduce(
            lambda x, y: x + y,
            [1 if is_box(chr) else 0 for chr in self.board],
            0
        )

    def goals_count(self):
        reduce(
            lambda x, y: x + y,
            [1 if is_goal(chr) else 0 for chr in self.board],
            0
        )


class PuzzleSnapshot(object):
    """
    Snapshot with all its meta data.

    No data validation is performed, to make parsing of Sokoban files as fast
    as possible. Proper validation is triggered when PuzzleSnapshot is
    converted into GameSnapshot.
    """
    def __init__(
        self, moves="", title="", duration=None, solver="", notes="",
        created_at="", updated_at="", variant = Variant.SOKOBAN
    ):
        self.id = 1
        self.moves = moves
        self.title = title
        self.duration = duration
        self.solver = solver
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at
        self.variant = variant

    @property
    def variant(self):
        return self._variant

    @variant.setter
    def variant(self, value):
        self._variant = Variant.factory(value)

    def to_game_snapshot(self):
        from ..game import GameSnapshot
        return GameSnapshot(variant = self.variant, moves_data = self.moves)

    def reformat(self, output_settings=OutputSettings()):
        self.moves = self.to_game_snapshot().to_s(output_settings)

    def clear(self):
        self.moves = ""
        self.title = ""
        self.duration = None
        self.solver = ""
        self.notes = ""
        self.created_at = ""
        self.updated_at = ""
        self.variant = Variant.SOKOBAN

    def pushes_count(self):
        reduce(
            lambda x, y: x + y,
            [
                1 if is_atomic_move_char(chr) and chr.isupper() else 0
                for chr in self.moves
            ], 0
        )

    def moves_count(self):
        """
        This is just informative number. Because snapshot is not fully parsed,
        this method may also account moves that are part of jumps or pusher
        selections.
        """
        reduce(
            lambda x, y: x + y,
            [
                1 if is_atomic_move_char(chr) and chr.islower() else 0
                for chr in self.moves
            ], 0
        )

    def is_reverse(self):
        reduce(
            lambda x, y: x or y,
            [
                chr == SpecialSnapshotCharacters.JUMP_BEGIN or
                chr == SpecialSnapshotCharacters.JUMP_END
                for chr in self.moves
            ], False
        )
