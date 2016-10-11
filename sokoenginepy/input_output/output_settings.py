class OutputSettings:
    """Settings that control string output of boards and snapshots.

    Args:
        break_long_lines (bool): insert line breaks
        rle_encode (bool): RLE encode output
        use_visible_floors (bool): print boards with visible floors
        line_break_at (int): where to insert line breaks?

    """

    def __init__(
        self,
        break_long_lines=True,
        rle_encode=False,
        use_visible_floors=False,
        line_break_at=70
    ):
        self._rle_encode = False
        self._use_visible_floors = False

        self.break_long_lines = break_long_lines
        self.rle_encode = rle_encode
        self.use_visible_floors = use_visible_floors
        self.line_break_at = line_break_at

    def should_insert_line_break_at(self, at_position):
        retv = False
        if (self.break_long_lines and self.line_break_at > 0 and at_position != 0):
            retv = (at_position % self.line_break_at) == 0
        return retv

    @property
    def use_visible_floors(self):
        return self._use_visible_floors

    @use_visible_floors.setter
    def use_visible_floors(self, value):
        if self._rle_encode:
            self._use_visible_floors = True
        else:
            self._use_visible_floors = bool(value)

    @property
    def rle_encode(self):
        return self._rle_encode

    @rle_encode.setter
    def rle_encode(self, value):
        if value:
            self._rle_encode = True
            self._use_visible_floors = True
        else:
            self._rle_encode = False
