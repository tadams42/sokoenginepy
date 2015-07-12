
class OutuputSettings(object):

    break_long_lines = True
    rle_compress = False
    use_visible_floors = False
    line_break_at = 70

    def should_insert_line_break_at(self, at_position):
        retv = False
        if (
            self.break_long_lines and
            self.line_break_at > 0 and
            at_position != 0
        ):
            retv = (at_position % self.line_break_at) == 0

        return retv
