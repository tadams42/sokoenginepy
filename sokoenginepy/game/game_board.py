from .sokoban_plus import SokobanPlus


class GameBoard(object):
    pass

    @property
    def sokoban_plus(self):
        return (
            self._sokoban_plus.boxorder,
            self._sokoban_plus.goalorder
        )

    @sokoban_plus.setter
    def sokoban_plus(self, sokoban_plus_tuple):
        self._sokoban_plus = SokobanPlus(
            self.boxes_count, sokoban_plus_tuple[0], sokoban_plus_tuple[1]
        )

    @property
    def boxes_count(self):
        return self._boxes_count
