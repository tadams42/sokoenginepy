from functools import reduce

from cached_property import cached_property

from ..board import is_box, is_goal, is_pusher
from ..common import Variant
from ..snapshot import SpecialSnapshotCharacters, is_atomic_move
from .output_settings import OutputSettings


class Puzzle:
    """Textual representation of game board with all its meta data and snapshots.

    No data validation is performed, to make parsing of Sokoban files as fast
    as possible. Proper validation is triggered when Puzzle is converted into
    game board.
    """

    def __init__(
        self,
        board="",
        variant=Variant.SOKOBAN,
        title="",
        author="",
        boxorder="",
        goalorder="",
        notes="",
        snapshots=None,
        created_at="",
        updated_at=""
    ):
        self._variant = None
        self.pid = 1
        self._board = board
        self.variant = variant
        self.title = title
        self.author = author
        self.boxorder = boxorder
        self.goalorder = goalorder
        self.notes = notes
        self.snapshots = snapshots or []
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def variant(self):
        return self._variant

    @variant.setter
    def variant(self, value):
        self._variant = Variant.factory(value)

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, rv):
        self._board = rv
        if 'pushers_count' in self.__dict__:
            del self.__dict__['pushers_count']
        if 'boxes_count' in self.__dict__:
            del self.__dict__['boxes_count']
        if 'goals_count' in self.__dict__:
            del self.__dict__['goals_count']

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
        # TODO Convert to VariantBoard, but add boxorder and goalorder attrs to
        # to variant board boefore we can do it
        from ..game import GameBoard
        retv = GameBoard(board_str=self.board, variant=self.variant)
        retv.sokoban_plus = (self.boxorder, self.goalorder)
        return retv

    @cached_property
    def pushers_count(self):
        return reduce(
            lambda x, y: x + y,
            [1 if is_pusher(chr) else 0 for chr in self.board], 0
        )

    @cached_property
    def boxes_count(self):
        return reduce(
            lambda x, y: x + y, [1 if is_box(chr) else 0 for chr in self.board],
            0
        )

    @cached_property
    def goals_count(self):
        return reduce(
            lambda x, y: x + y,
            [1 if is_goal(chr) else 0 for chr in self.board], 0
        )


class PuzzleSnapshot:
    """Snapshot with all its meta data.

    No data validation is performed, to make parsing of Sokoban files as fast
    as possible. Proper validation is triggered when PuzzleSnapshot is
    converted into GameSnapshot.
    """

    def __init__(
        self,
        moves="",
        title="",
        duration=None,
        solver="",
        notes="",
        created_at="",
        updated_at="",
        variant=Variant.SOKOBAN
    ):
        self._variant = None
        self.pid = 1
        self._moves = moves
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

    @property
    def moves(self):
        return self._moves

    @moves.setter
    def moves(self, rv):
        self._moves = rv
        if 'pushes_count' in self.__dict__:
            del self.__dict__['pushes_count']
        if 'moves_count' in self.__dict__:
            del self.__dict__['moves_count']
        if 'is_reverse' in self.__dict__:
            del self.__dict__['is_reverse']

    def to_game_snapshot(self):
        from ..game import GameSnapshot
        return GameSnapshot(variant=self.variant, moves_data=self.moves)

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

    @cached_property
    def pushes_count(self):
        return reduce(
            lambda x, y: x + y, [
                1 if is_atomic_move(chr) and chr.isupper() else 0
                for chr in self.moves
            ], 0
        )

    @cached_property
    def moves_count(self):
        """
        This is just informative number. Because snapshot is not fully parsed,
        this method may also account moves that are part of jumps or pusher
        selections.
        """
        return reduce(
            lambda x, y: x + y, [
                1 if is_atomic_move(chr) and chr.islower() else 0
                for chr in self.moves
            ], 0
        )

    @cached_property
    def is_reverse(self):
        return reduce(
            lambda x, y: x or y, [
                chr == SpecialSnapshotCharacters.JUMP_BEGIN or
                chr == SpecialSnapshotCharacters.JUMP_END for chr in self.moves
            ], False
        )
