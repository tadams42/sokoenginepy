from ..core import Variant, SokobanPlus
from ..variant import VariantBoard


class GameBoard:

    def __init__(
        self,
        board_width=0,
        board_height=0,
        variant=Variant.SOKOBAN,
        board_str=""
    ):
        self._variant_board = VariantBoard.factory(
            board_width=board_width,
            board_height=board_height,
            variant=variant,
            board_str=board_str
        )

        # self._sokoban_plus = SokobanPlus()

    @property
    def pushers_count(self):
        pass

    @property
    def pushers_ids(self):
        pass

    @property
    def pushers_positions(self):
        pass

    def pusher_positon(self, id):
        pass

    def pusher_id(self, on_position):
        pass

    @property
    def boxes_count(self):
        pass

    @property
    def boxes_ids(self):
        pass

    @property
    def boxes_positions(self):
        pass

    def box_position(self, id):
        pass

    def box_id(self, on_position):
        pass

    def box_plus_id(self, id):
        pass

    @property
    def goals_count(self):
        pass

    @property
    def goals_ids(self):
        pass

    @property
    def goals_positions(self):
        pass

    def goal_position(self, id):
        pass

    def goal_id(self, on_position):
        pass

    def goal_plus_id(self, id):
        pass

    def cell_orientation(self, position):
        pass

    @property
    def variant(self):
        return self._variant_board.variant

    def is_solved(self):
        pass

    def is_playable(self):
        pass

    def switch_boxes_and_goals(self):
        pass

    @property
    def sokoban_plus(self):
        return (self._sokoban_plus.boxorder, self._sokoban_plus.goalorder)

    @sokoban_plus.setter
    def sokoban_plus(self, sokoban_plus_tuple):
        self._sokoban_plus = SokobanPlus(
            self.boxes_count, sokoban_plus_tuple[0], sokoban_plus_tuple[1]
        )

    def toggle_sokoban_plus(self):
        pass

    def is_sokoban_plus_enabled(self):
        pass

    def transfer_box(self, old_position, new_position):
        pass

    def transfer_pusher(self, old_position, new_position):
        pass

    def zobrist_hash(self):
        pass

    def normalized_zobrist_hash(self):
        pass

    @property
    def width(self):
        pass

    @property
    def height(self):
        pass

    @property
    def size(self):
        pass

    def clear(self):
        pass

    def mark_play_area(self):
        pass

    def positions_reachable_by_pusher(self, pusher_id):
        pass
