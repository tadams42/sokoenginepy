from .. import utilities
from .piece import DEFAULT_PIECE_ID


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

    Attributes:
        DEFAULT_PLUS_ID: Sokoban+ ID for pieces that don't have one or when
            Sokoban+ is disabled.

            Original Sokoban+ implementation used number 99 for default plus ID. As
            there can be more than 99 boxes on board, sokoenginepy changes this
            detail and uses :const:`DEFAULT_PLUS_ID` as default plus ID. When loading
            older puzzles with Sokoban+, legacy default value is converted
            transparently.

    Args:
        boxorder (str): Space separated integers describing Sokoban+ IDs for boxes
        goalorder (str): Space separated integers describing Sokoban+ IDs for goals
        pieces_count (int): Total count of boxes/goals on board
    """

    _LEGACY_DEFAULT_PLUS_ID = 99
    DEFAULT_PLUS_ID = 0

    def __init__(self, pieces_count, boxorder=None, goalorder=None):
        self._is_enabled = False
        self._is_validated = False
        self.errors = []

        self._pieces_count = pieces_count
        self._box_plus_ids = None
        self._goal_plus_ids = None
        self._boxorder = None
        self._goalorder = None

        self.boxorder = boxorder or ""
        self.goalorder = goalorder or ""

    @classmethod
    def is_sokoban_plus_string(cls, line):
        return utilities.contains_only_digits_and_spaces(
            line
        ) and not utilities.is_blank(line)

    @classmethod
    def is_valid_plus_id(cls, plus_id):
        return isinstance(plus_id, int) and plus_id >= cls.DEFAULT_PLUS_ID

    @property
    def pieces_count(self):
        return self._pieces_count

    @pieces_count.setter
    def pieces_count(self, rv):
        if rv != self._pieces_count:
            self.is_enabled = False
            self._is_validated = False
            self._pieces_count = int(rv)

    @property
    def boxorder(self):
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
    def goalorder(self):
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
    def is_valid(self):
        if self._is_validated:
            return not self.errors

        self.errors = []
        try:
            self._box_plus_ids = self._parse_and_clean_ids_string(self._boxorder)
            self._goal_plus_ids = self._parse_and_clean_ids_string(self._goalorder)
        except ValueError as exc:
            self.errors.append(str(exc))

        self._validate_plus_ids(self._box_plus_ids)
        self._validate_plus_ids(self._goal_plus_ids)
        self._validate_piece_count()
        self._validate_ids_counts()
        self._validate_id_sets_equality()
        self._is_validated = True

        return not self.errors

    @property
    def is_enabled(self):
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, value):
        """
        Raises:
            :exc:`SokobanPlusDataError`: Trying to enable invalid Sokoban+
        """
        if value:
            if not self.is_valid:
                raise SokobanPlusDataError(self.errors)
        self._is_enabled = value

    def box_plus_id(self, for_box_id):
        """
        Get Sokoban+ ID for box.

        Args:
            for_box_id (int): box ID

        Returns:
            int: If Sokoban+ is enabled returns Sokoban+ ID of a box. If not, returns
            :const:`DEFAULT_PLUS_ID`

        Raises:
            :exc:`KeyError`: No box with ID ``for_box_id``, but only if i Sokoban+ is
                enabled
        """
        try:
            return self._get_plus_id(for_box_id, from_where=self._box_plus_ids)
        except KeyError:
            raise KeyError("No box with ID: {0}".format(for_box_id))

    def goal_plus_id(self, for_goal_id):
        """
        Get Sokoban+ ID for goal.

        Args:
            for_goal_id (int): goal ID

        Returns:
            int: If Sokoban+ is enabled returns Sokoban+ ID of a goal. If not,
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
        if self.pieces_count < self._LEGACY_DEFAULT_PLUS_ID:
            return plus_ids_str.rstrip(
                str(self.DEFAULT_PLUS_ID) + " " + str(self._LEGACY_DEFAULT_PLUS_ID)
            )
        else:
            return plus_ids_str.rstrip(str(self.DEFAULT_PLUS_ID) + " ")

    def _get_plus_id(self, for_id, from_where):
        if not self.is_enabled:
            return self.DEFAULT_PLUS_ID
        else:
            return from_where[for_id]

    def _parse_and_clean_ids_string(self, plus_ids_str):
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
                i == self._LEGACY_DEFAULT_PLUS_ID
                and self.pieces_count < self._LEGACY_DEFAULT_PLUS_ID
            )
            else i
            for i in trimmed
        ]

        expanded = cleaned + [self.DEFAULT_PLUS_ID] * (self.pieces_count - len(cleaned))

        retv = dict()
        for index, plus_id in enumerate(expanded):
            retv[DEFAULT_PIECE_ID + index] = plus_id

        return retv

    def _validate_plus_ids(self, ids):
        if ids:
            for i in ids.values():
                if not self.is_valid_plus_id(i):
                    self.errors.append("Invalid Sokoban+ ID: {0}".format(i))

    def _validate_piece_count(self):
        if self.pieces_count < 0:
            self.errors.append("Sokoban+ can't be applied to zero pieces count.")

    def _validate_ids_counts(self):
        if self._box_plus_ids and len(self._box_plus_ids) != self.pieces_count:
            self.errors.append(
                "Sokoban+ boxorder data doesn't contain same amount of IDs "
                + "as there are pieces on board! (pieces_count: {0})".format(
                    self.pieces_count
                )
            )

        if self._goal_plus_ids and len(self._goal_plus_ids) != self.pieces_count:
            self.errors.append(
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
            self.errors.append(
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
