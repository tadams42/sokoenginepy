class OutuputSettings(object):
    """
    Settings that control string output of boards and snapshots.
    """

    def __init__(
        self, break_long_lines=True, rle_encode=False, use_visible_floors=False,
        line_break_at=70,
    ):
        self.break_long_lines = break_long_lines
        self.rle_encode = rle_encode
        self.use_visible_floors = use_visible_floors
        self.line_break_at = line_break_at

    def should_insert_line_break_at(self, at_position):
        retv = False
        if (
            self.break_long_lines and
            self.line_break_at > 0 and
            at_position != 0
        ):
            retv = (at_position % self.line_break_at) == 0

        return retv
