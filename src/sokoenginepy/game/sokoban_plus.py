from __future__ import annotations

from typing import Dict, Final, List, Optional

from .config import Config


class SokobanPlusDataError(ValueError):
    pass


class SokobanPlus:
    """
    Manages Sokoban+ data for game board.

    **Sokoban+ rules**

    In this variant of game rules, each box and each goal on board get number tag
    (color). Game objective changes slightly: board is considered solved only when
    each goal is filled with box of the same tag. So, for example goal tagged with
    number 9 must be filled with any box tagged with number 9.

    Multiple boxes and goals may share same plus id, but the number of boxes with one
    plus id must be equal to number of goals with that same plus id. There is also
    default plus id that represents non tagged boxes and goals.

    Sokoban+ ids for given board are defined by two strings called goalorder and
    boxorder. For example, boxorder "13 24 3 122 1" would give plus_id = 13 to box id
    = 1, plus_id = 24 to box ID = 2, etc...

    **Valid Sokoban+ id sequences**

    Boxorder and goalorder must define ids for equal number of boxes and goals. This
    means that in case of boxorder assigning plus id "42" to two boxes, goalorder
    must also contain number 42 twice.

    Sokoban+ data parser accepts any positive integer as plus id.
    """

    LEGACY_DEFAULT_PLUS_ID: Final[int] = 99

    #: Sokoban+ ID for pieces that don't have one or when Sokoban+ is disabled.
    #:
    #: Original Sokoban+ implementation used number 99 for default plus ID. As
    #: there can be more than 99 boxes on board, sokoenginepy changes this
    #: detail and uses :const:`DEFAULT_PLUS_ID` as default plus ID. When loading
    #: older puzzles with Sokoban+, legacy default value is converted
    #: transparently.
    DEFAULT_PLUS_ID: Final[int] = 0

    def __init__(
        self,
        pieces_count: int,
        boxorder: Optional[str] = None,
        goalorder: Optional[str] = None,
    ):
        """
        Args:
            boxorder: Space separated integers describing Sokoban+ IDs for boxes
            goalorder: Space separated integers describing Sokoban+ IDs for goals
            pieces_count: Total count of boxes/goals on board
        """
        self._is_enabled = False
        self._is_validated = False
        self._errors: List[str] = []

        self._pieces_count = pieces_count
        self._box_plus_ids: Dict[int, int] = {}
        self._goal_plus_ids: Dict[int, int] = {}
        self._boxorder: str = boxorder or ""
        self._goalorder: str = goalorder or ""

    @classmethod
    def is_valid_plus_id(cls, plus_id: int) -> bool:
        return isinstance(plus_id, int) and plus_id >= cls.DEFAULT_PLUS_ID

    @property
    def pieces_count(self) -> int:
        return self._pieces_count

    @pieces_count.setter
    def pieces_count(self, rv):
        if rv != self._pieces_count:
            self.is_enabled = False
            self._is_validated = False
            self._pieces_count = int(rv)

    @property
    def boxorder(self) -> str:
        if self.is_enabled and self.is_valid:
            return self._rstrip_default_plus_ids(
                " ".join(str(i) for i in self._box_plus_ids.values())
            )
        else:
            return self._boxorder

    @boxorder.setter
    def boxorder(self, rv):
        if rv != self._boxorder:
            self.is_enabled = False
            self._is_validated = False
            self._boxorder = rv or ""

    @property
    def goalorder(self) -> str:
        if self.is_enabled and self.is_valid:
            return self._rstrip_default_plus_ids(
                " ".join(str(i) for i in self._goal_plus_ids.values())
            )
        else:
            return self._goalorder

    @goalorder.setter
    def goalorder(self, rv):
        if rv != self._goalorder:
            self.is_enabled = False
            self._is_validated = False
            self._goalorder = rv or ""

    @property
    def is_valid(self) -> bool:
        if self._is_validated:
            return not self._errors

        self._errors = []
        try:
            self._box_plus_ids = self._parse_and_clean_ids_string(self._boxorder)
            self._goal_plus_ids = self._parse_and_clean_ids_string(self._goalorder)
        except ValueError as exc:
            self._errors.append(str(exc))

        self._validate_plus_ids(self._box_plus_ids)
        self._validate_plus_ids(self._goal_plus_ids)
        self._validate_piece_count()
        self._validate_ids_counts()
        self._validate_id_sets_equality()
        self._is_validated = True

        return not self._errors

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    @property
    def errors(self) -> List[str]:
        return self._errors

    @is_enabled.setter
    def is_enabled(self, value):
        """
        Raises:
            :exc:`SokobanPlusDataError`: Trying to enable invalid Sokoban+
        """
        if value:
            if not self.is_valid:
                raise SokobanPlusDataError(self._errors)
        self._is_enabled = value

    @property
    def is_validated(self):
        return self._is_validated

    def box_plus_id(self, for_box_id: int) -> int:
        """
        Get Sokoban+ ID for box.

        Returns:
            If Sokoban+ is enabled returns Sokoban+ ID of a box. If not, returns
            :const:`DEFAULT_PLUS_ID`

        Raises:
            :exc:`KeyError`: No box with ID ``for_box_id``, but only if i Sokoban+ is
                enabled
        """
        try:
            return self._get_plus_id(for_box_id, from_where=self._box_plus_ids)
        except KeyError:
            raise KeyError("No box with ID: {0}".format(for_box_id))

    def goal_plus_id(self, for_goal_id: int) -> int:
        """
        Get Sokoban+ ID for goal.

        Returns:
            If Sokoban+ is enabled returns Sokoban+ ID of a goal. If not,
            returns :const:`DEFAULT_PLUS_ID`

        Raises:
            :exc:`KeyError`: No goal with ID ``for_goal_id``, but only if Sokoban+ is
                enabled
        """
        try:
            return self._get_plus_id(for_goal_id, from_where=self._goal_plus_ids)
        except KeyError:
            raise KeyError("No goal with ID: {0}".format(for_goal_id))

    def _rstrip_default_plus_ids(self, plus_ids_str):
        # TODO: Might not work correctly for "3 5 4 6 2 19" or "3 5 4 6 2 10"
        if self.pieces_count < self.LEGACY_DEFAULT_PLUS_ID:
            return plus_ids_str.rstrip(
                str(self.DEFAULT_PLUS_ID) + " " + str(self.LEGACY_DEFAULT_PLUS_ID)
            )
        else:
            return plus_ids_str.rstrip(str(self.DEFAULT_PLUS_ID) + " ")

    def _get_plus_id(self, for_id: int, from_where: Dict[int, int]):
        if not self.is_enabled:
            return self.DEFAULT_PLUS_ID
        else:
            return from_where[for_id]

    def _parse_and_clean_ids_string(self, plus_ids_str) -> Dict[int, int]:
        """
        Safely replaces legacy default plus ids with default ones.

        Returns:
            dict: dict that maps piece IDs to piece Sokoban+ IDs
        """

        def convert_or_raise(id_str):
            try:
                return int(id_str)
            except ValueError:
                raise SokobanPlusDataError(
                    "Can't parse Sokoban+ string! Illegal characters found. "
                    "Only digits and spaces allowed."
                )

        trimmed = [
            convert_or_raise(id_str)
            for id_str in self._rstrip_default_plus_ids(plus_ids_str).split()
        ]

        cleaned = [
            self.DEFAULT_PLUS_ID
            if (
                i == self.LEGACY_DEFAULT_PLUS_ID
                and self.pieces_count < self.LEGACY_DEFAULT_PLUS_ID
            )
            else i
            for i in trimmed
        ]

        expanded = cleaned + [self.DEFAULT_PLUS_ID] * (self.pieces_count - len(cleaned))

        retv = dict()
        for index, plus_id in enumerate(expanded):
            retv[Config.DEFAULT_PIECE_ID + index] = plus_id

        return retv

    def _validate_plus_ids(self, ids: Dict[int, int]):
        if ids:
            for i in ids.values():
                if not self.is_valid_plus_id(i):
                    self._errors.append(f"Invalid Sokoban+ ID: {i}")

    def _validate_piece_count(self):
        if self.pieces_count < 0:
            self._errors.append("Sokoban+ can't be applied to zero pieces count.")

    def _validate_ids_counts(self):
        if self._box_plus_ids and len(self._box_plus_ids) != self.pieces_count:
            self._errors.append(
                "Sokoban+ boxorder data doesn't contain same amount of IDs "
                + "as there are pieces on board! (pieces_count: {0})".format(
                    self.pieces_count
                )
            )

        if self._goal_plus_ids and len(self._goal_plus_ids) != self.pieces_count:
            self._errors.append(
                "Sokoban+ goalorder data doesn't contain same amount of IDs "
                + "as there are pieces on board! (pieces_count: {0})".format(
                    self.pieces_count
                )
            )

    def _validate_id_sets_equality(self):
        if self._box_plus_ids:
            boxes = set(
                pid
                for pid in self._box_plus_ids.values()
                if pid != self.DEFAULT_PLUS_ID
            )
        else:
            boxes = set()

        if self._goal_plus_ids:
            goals = set(
                pid
                for pid in self._goal_plus_ids.values()
                if pid != self.DEFAULT_PLUS_ID
            )
        else:
            goals = set()

        if boxes != goals:
            self._errors.append(
                "Sokoban+ data doesn't define equal sets of IDs for "
                + "boxes and goals"
            )

    def __repr__(self):
        return (
            "SokobanPlus("
            + "pieces_count={0}, boxorder='{1}', goalorder='{2}')".format(
                self.pieces_count, self.boxorder, self.goalorder
            )
        )

    def __str__(self):
        return (
            "SokobanPlus("
            + "pieces_count={0}, boxorder='{1}', goalorder='{2}')".format(
                self.pieces_count, self.boxorder, self.goalorder
            )
        )
