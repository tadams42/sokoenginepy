"""
Global sokoenginepy settings.
"""

#: Use more visibe characer for Boards when printing them?
OUTPUT_BOARDS_WITH_VISIBLE_FLOORS = False

#: When printing Boards, should they be RLE encoded?
RLE_ENCODE_BOARD_STRINGS = False

#: word wraping when printing Snapshots?
BREAK_LONG_SNAPSHOT_STRINGS = True

#: How many characerts for each line of snapshot string?
SNAPSHOT_LINE_BREAKS_AT = 80


def should_insert_line_break_at(position):
    """
    For given ``position`` in string, should we insert line break?
    """
    if BREAK_LONG_SNAPSHOT_STRINGS and SNAPSHOT_LINE_BREAKS_AT > 0 and position:
        return (position % SNAPSHOT_LINE_BREAKS_AT) == 0
    return False
