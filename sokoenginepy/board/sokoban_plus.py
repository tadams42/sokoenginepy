from ..common import PrettyPrintable, SokoengineError
from .piece import Piece


class SokobanPlusDataError(SokoengineError):
    """
    Exception
    """
    pass


class SokobanPlus(PrettyPrintable):
    """
    Manages Sokoban+ data for game board

    **Sokoban+ rules**

    In this variant of game rules, each box and each goal on board get number
    tag (color). Game objective changes slightly: board is considered solved
    only when each goal is filled with box of the same tag. So, for example goal
    tagged with number 9 must be filled with any box tagged with number 9.

    Multiple boxes and goals may share same plus id, but the number of boxes
    with one plus id must be equal to number of goals with that same plus id.
    There is also default plus id that represents non tagged boxes and goals.

    Sokoban+ ids for given board are defined by two strings called goalorder
    and boxorder.
    For example, boxorder "13 24 3 122 1" would give plus_id = 13 to box id = 1,
    plus_id = 24 to box ID = 2, etc...

    **Valid Sokoban+ id sequences**

    Boxorder and goalorder must define ids for equal number of boxes and goals.
    This means that in case of boxorder asigning plus id "42" to two boxes,
    goalorder must also contain number 42 twice.
    Sokoban+ data parser accepts any positive integer as plus id, but it is
    encouraged to use small numbers because they are prettier once board is
    rendered with displayed Sokoban+ IDs.

    **Default plus_id in Sokoban+ strings**

    Original implementation used number 99 for default plus ID. As there can be
    more than 99 boxes on board, sokoenginepy changes this detail and uses
    Piece.DEFAULT_PLUS_ID as default plus ID. When loading older puzzles
    with Sokoban+, legacy default value is converted transparently.
    """

    _LEGACY_DEFAULT_PLUS_ID = 99

    def __init__(self, pieces_count, boxorder, goalorder):
        self._is_enabled = False
        self._is_validated = False
        self.errors = []

        self._pieces_count = pieces_count
        self._box_plus_ids = None
        self._goal_plus_ids = None
        self._boxorder = None
        self._goalorder = None

        self.boxorder = boxorder
        self.goalorder = goalorder

    @property
    def pieces_count(self):
        return self._pieces_count

    @property
    def boxorder(self):
        if self.is_valid:
            return self._rstrip_default_plus_ids(
                " ".join(str(i) for i in self._box_plus_ids.values())
            )
        else:
            return self._boxorder

    @boxorder.setter
    def boxorder(self, rv):
        self.is_enabled = False
        self._is_validated = False
        self._boxorder = rv

    @property
    def goalorder(self):
        if self.is_valid:
            return self._rstrip_default_plus_ids(
                " ".join(str(i) for i in self._goal_plus_ids.values())
            )
        else:
            return self._goalorder

    @goalorder.setter
    def goalorder(self, rv):
        self.is_enabled = False
        self._is_validated = False
        self._goalorder = rv

    @property
    def is_valid(self):
        self._validate_and_parse()
        return not self.errors

    @property
    def is_enabled(self):
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, value):
        if value:
            if not self.is_valid:
                raise SokobanPlusDataError(self.errors)
            self._is_enabled = True
        else:
            self._is_enabled = False

    def box_plus_id(self, for_box_id):
        """
        plus ID from boxorder or Box.DEFAULT_PLUS_ID if there isn't one
        defined or self.is_enabled == False
        """
        return self._get_plus_id(for_box_id, from_where=self._box_plus_ids)

    def goal_plus_id(self, for_goal_id):
        """
        plus ID from goalorder or Goal.DEFAULT_PLUS_ID if there isn't one
        defined or self.is_enabled == False
        """
        return self._get_plus_id(for_goal_id, from_where=self._goal_plus_ids)

    def _rstrip_default_plus_ids(self, plus_ids_str):
        if self.pieces_count < self._LEGACY_DEFAULT_PLUS_ID:
            return plus_ids_str.rstrip(
                str(Piece.DEFAULT_PLUS_ID) + " " +
                str(self._LEGACY_DEFAULT_PLUS_ID)
            )
        else:
            return plus_ids_str.rstrip(str(Piece.DEFAULT_PLUS_ID) + " ")

    def _get_plus_id(self, for_id, from_where):
        if not self.is_enabled:
            return Piece.DEFAULT_PLUS_ID
        else:
            return from_where[for_id]

    def _collect_ids_dict(self, ids_list):
        """
        Safely replaces legacy default plus ids with default ones and fills ids
        list to pieces_count length with default plus ids.
        """
        trimmed = [
            int(id)
            for id in self.
            _rstrip_default_plus_ids(" ".join(str(i) for i in ids_list)).split()
        ]


        replaced = [
            Piece.DEFAULT_PLUS_ID if (
                i == self._LEGACY_DEFAULT_PLUS_ID and
                self.pieces_count < self._LEGACY_DEFAULT_PLUS_ID
            ) else i for i in trimmed
        ]

        expanded = replaced + [Piece.DEFAULT_PLUS_ID] * (
            self.pieces_count - len(replaced)
        )

        retv = dict()
        for index, plus_id in enumerate(expanded):
            retv[Piece.DEFAULT_ID + index] = plus_id

        return retv

    def _parse(self):

        def parse_sokoban_plus_data(line):
            parsed_plus_ids = []
            try:
                parsed_plus_ids = [int(j) for j in line.split()]
            except ValueError:
                raise SokobanPlusDataError(
                    "Can't parse Sokoban+ string! Illegal characters found. "
                    "Only digits and spaces allowed."
                )

            return parsed_plus_ids

        self._box_plus_ids = self._collect_ids_dict(
            parse_sokoban_plus_data(self._boxorder)
        )
        self._goal_plus_ids = self._collect_ids_dict(
            parse_sokoban_plus_data(self._goalorder)
        )

    def _validate_plus_ids(self, ids):
        if ids:
            for i in ids:
                if not Piece.is_valid_plus_id(i):
                    self.errors.append("Invalid Sokoban+ ID: {0}".format(i))

    def _validate_piece_count(self):
        if self.pieces_count < 0:
            self.errors.append(
                "Sokoban+ can't be applied to zero pieces count."
            )

    def _validate_ids_counts(self):
        error_template = (
            "Sokoban+ {0} data doesn't contain same amount of ids as there are "
            "pieces on board! (pieces_count: {1})".format(
                "{0}", self.pieces_count
            )
        )

        if self._box_plus_ids and len(self._box_plus_ids) != self.pieces_count:
            self.errors.append(error_template.format("boxorder"))
        if self._goal_plus_ids and len(self._goal_plus_ids) != self.pieces_count:
            self.errors.append(error_template.format("goalorder"))

    def _validate_id_sets_equality(self):
        if self._box_plus_ids:
            boxes = set(
                id for id in self._box_plus_ids.values()
                if id != Piece.DEFAULT_PLUS_ID
            )
        else:
            boxes = []

        if self._goal_plus_ids:
            goals = set(
                id for id in self._goal_plus_ids.values()
                if id != Piece.DEFAULT_PLUS_ID
            )
        else:
            goals = []

        if boxes != goals:
            self.errors.append(
                "Sokoban+ data doesn't define equal sets of IDs for boxes and goals"
            )

    @property
    def _representation_attributes(self):
        return {
            'pieces_count': self.pieces_count,
            'boxorder': self.boxorder,
            'goalorder': self.goalorder,
        }

    def _validate_and_parse(self):
        if self._is_validated:
            return not self.errors

        self.errors = []
        try:
            self._parse()
        except SokobanPlusDataError as e:
            self.errors.append(str(e))

        self._validate_plus_ids(self._box_plus_ids)
        self._validate_plus_ids(self._goal_plus_ids)
        self._validate_piece_count()
        self._validate_ids_counts()
        self._validate_id_sets_equality()
        self._is_validated = True
