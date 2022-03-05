from functools import cached_property, reduce
from operator import add, or_

from ..board import BoardCell, VariantBoard
from ..snapshot import AtomicMove, Snapshot
from ..tessellation import Tessellation


class Puzzle:
    """
    Textual representation of game board with all its meta data and snapshots.

    No data validation is performed, to make parsing of Sokoban files as fast as
    possible. Proper validation is triggered when Puzzle is converted into game
    board.
    """

    def __init__(
        self,
        board="",
        title="",
        author="",
        boxorder="",
        goalorder="",
        notes="",
        snapshots=None,
        created_at="",
        updated_at="",
        tessellation_or_description=Tessellation.SOKOBAN,
    ):
        self._tessellation = None
        self.tessellation = tessellation_or_description
        self.pid = 1
        self._board = board
        self.title = title
        self.author = author
        self.boxorder = boxorder
        self.goalorder = goalorder
        self.notes = notes
        self.snapshots = snapshots or []
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def tessellation(self):
        return self._tessellation.value

    @tessellation.setter
    def tessellation(self, tessellation_or_description):
        self._tessellation = Tessellation.instance_from(tessellation_or_description)

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, rv):
        self._board = rv
        if "pushers_count" in self.__dict__:
            del self.__dict__["pushers_count"]
        if "boxes_count" in self.__dict__:
            del self.__dict__["boxes_count"]
        if "goals_count" in self.__dict__:
            del self.__dict__["goals_count"]

    def clear(self):
        self.board = ""
        self.tessellation = Tessellation.SOKOBAN
        self.title = ""
        self.author = ""
        self.boxorder = ""
        self.goalorder = ""
        self.notes = ""
        self.snapshots = []
        self.created_at = ""
        self.updated_at = ""

    def reformat(self):
        self.board = str(self.to_game_board())
        for snap in self.snapshots:
            snap.reformat()

    def to_game_board(self):
        retv = VariantBoard.instance_from(
            tessellation_or_description=self.tessellation, board_str=self.board
        )
        return retv

    @cached_property
    def pushers_count(self):
        return reduce(
            add, [1 if BoardCell.is_pusher_chr(chr) else 0 for chr in self.board], 0
        )

    @cached_property
    def boxes_count(self):
        return reduce(
            add, [1 if BoardCell.is_box_chr(chr) else 0 for chr in self.board], 0
        )

    @cached_property
    def goals_count(self):
        return reduce(
            add, [1 if BoardCell.is_goal_chr(chr) else 0 for chr in self.board], 0
        )


class PuzzleSnapshot:
    """
    :class:`.Snapshot` with all its meta data.

    No data validation is performed, to make parsing of Sokoban files as fast as
    possible. Proper validation is triggered when PuzzleSnapshot is converted into
    :class:`.Snapshot`.
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
        tessellation_or_description=Tessellation.SOKOBAN,
    ):
        self._tessellation = None
        self.tessellation = tessellation_or_description
        self.pid = 1
        self._moves = moves
        self.title = title
        self.duration = duration
        self.solver = solver
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def tessellation(self):
        return self._tessellation.value

    @tessellation.setter
    def tessellation(self, tessellation_or_description):
        self._tessellation = Tessellation.instance_from(tessellation_or_description)

    @property
    def moves(self):
        return self._moves

    @moves.setter
    def moves(self, rv):
        self._moves = rv
        if "pushes_count" in self.__dict__:
            del self.__dict__["pushes_count"]
        if "moves_count" in self.__dict__:
            del self.__dict__["moves_count"]
        if "is_reverse" in self.__dict__:
            del self.__dict__["is_reverse"]

    def to_game_snapshot(self):
        return Snapshot(
            tessellation_or_description=self.tessellation, moves_data=self.moves
        )

    def reformat(self):
        self.moves = str(self.to_game_snapshot())

    @cached_property
    def pushes_count(self):
        return reduce(
            add,
            [
                1 if (AtomicMove.is_atomic_move_chr(chr) and chr.isupper()) else 0
                for chr in self.moves
            ],
            0,
        )

    @cached_property
    def moves_count(self):
        """
        This is just informative number. Because snapshot is not fully parsed, this
        method may also account moves that are part of jumps or pusher selections.
        """
        return reduce(
            add,
            [
                1 if (AtomicMove.is_atomic_move_chr(chr) and chr.islower()) else 0
                for chr in self.moves
            ],
            0,
        )

    @cached_property
    def is_reverse(self):
        return reduce(
            or_,
            [
                chr == Snapshot.JUMP_BEGIN or chr == Snapshot.JUMP_END
                for chr in self.moves
            ],
            False,
        )
