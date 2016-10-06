from sokoenginepy.board import Piece
from sokoenginepy.tessellation import index_1d


class DescribeBoardStateSpec:

    def it_memoizes_pieces(self, board_state):
        width = board_state._variant_board.width

        assert board_state.board_size == board_state._variant_board.size

        assert board_state.pushers_count == 1
        assert sorted(board_state.pushers_ids) == [Piece.DEFAULT_ID]
        assert board_state.pushers_positions == [index_1d(11, 8, width)]
        assert board_state.normalized_pusher_positions == {
            Piece.DEFAULT_ID: index_1d(8, 4, width)
        }
        assert board_state.pusher_position(Piece.DEFAULT_ID) == index_1d(
            11, 8, width
        )
        assert board_state.pusher_id(index_1d(11, 8, width)) == Piece.DEFAULT_ID

        assert board_state.boxes_count == 6
        assert sorted(board_state.boxes_ids) == [
            Piece.DEFAULT_ID, Piece.DEFAULT_ID + 1, Piece.DEFAULT_ID + 2,
            Piece.DEFAULT_ID + 3, Piece.DEFAULT_ID + 4, Piece.DEFAULT_ID + 5
        ]
        assert board_state.boxes_positions == [
            index_1d(5, 2, width),
            index_1d(7, 3, width),
            index_1d(5, 4, width),
            index_1d(7, 4, width),
            index_1d(2, 7, width),
            index_1d(5, 7, width),
        ]
        assert board_state.box_position(Piece.DEFAULT_ID) == index_1d(
            5, 2, width
        )
        assert board_state.box_position(Piece.DEFAULT_ID + 1) == index_1d(
            7, 3, width
        )
        assert board_state.box_position(Piece.DEFAULT_ID + 2) == index_1d(
            5, 4, width
        )
        assert board_state.box_position(Piece.DEFAULT_ID + 3) == index_1d(
            7, 4, width
        )
        assert board_state.box_position(Piece.DEFAULT_ID + 4) == index_1d(
            2, 7, width
        )
        assert board_state.box_position(Piece.DEFAULT_ID + 5) == index_1d(
            5, 7, width
        )
        assert board_state.box_id(index_1d(5, 2, width)) == Piece.DEFAULT_ID
        assert board_state.box_id(index_1d(7, 3, width)) == Piece.DEFAULT_ID + 1
        assert board_state.box_id(index_1d(5, 4, width)) == Piece.DEFAULT_ID + 2
        assert board_state.box_id(index_1d(7, 4, width)) == Piece.DEFAULT_ID + 3
        assert board_state.box_id(index_1d(2, 7, width)) == Piece.DEFAULT_ID + 4
        assert board_state.box_id(index_1d(5, 7, width)) == Piece.DEFAULT_ID + 5
        assert board_state.box_plus_id(
            Piece.DEFAULT_ID
        ) == Piece.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            Piece.DEFAULT_ID + 1
        ) == Piece.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            Piece.DEFAULT_ID + 2
        ) == Piece.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            Piece.DEFAULT_ID + 3
        ) == Piece.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            Piece.DEFAULT_ID + 4
        ) == Piece.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            Piece.DEFAULT_ID + 5
        ) == Piece.DEFAULT_PLUS_ID

        assert board_state.goals_count == 6
        assert sorted(board_state.goals_ids) == [
            Piece.DEFAULT_ID, Piece.DEFAULT_ID + 1, Piece.DEFAULT_ID + 2,
            Piece.DEFAULT_ID + 3, Piece.DEFAULT_ID + 4, Piece.DEFAULT_ID + 5
        ]
        assert board_state.goals_positions == [
            index_1d(16, 6, width),
            index_1d(17, 6, width),
            index_1d(16, 7, width),
            index_1d(17, 7, width),
            index_1d(16, 8, width),
            index_1d(17, 8, width),
        ]
        assert board_state.goal_position(Piece.DEFAULT_ID) == index_1d(
            16, 6, width
        )
        assert board_state.goal_position(Piece.DEFAULT_ID + 1) == index_1d(
            17, 6, width
        )
        assert board_state.goal_position(Piece.DEFAULT_ID + 2) == index_1d(
            16, 7, width
        )
        assert board_state.goal_position(Piece.DEFAULT_ID + 3) == index_1d(
            17, 7, width
        )
        assert board_state.goal_position(Piece.DEFAULT_ID + 4) == index_1d(
            16, 8, width
        )
        assert board_state.goal_position(Piece.DEFAULT_ID + 5) == index_1d(
            17, 8, width
        )
        assert board_state.goal_id(index_1d(16, 6, width)) == Piece.DEFAULT_ID
        assert board_state.goal_id(index_1d(17, 6, width)
                                  ) == Piece.DEFAULT_ID + 1
        assert board_state.goal_id(index_1d(16, 7, width)
                                  ) == Piece.DEFAULT_ID + 2
        assert board_state.goal_id(index_1d(17, 7, width)
                                  ) == Piece.DEFAULT_ID + 3
        assert board_state.goal_id(index_1d(16, 8, width)
                                  ) == Piece.DEFAULT_ID + 4
        assert board_state.goal_id(index_1d(17, 8, width)
                                  ) == Piece.DEFAULT_ID + 5
        assert board_state.goal_plus_id(
            Piece.DEFAULT_ID
        ) == Piece.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            Piece.DEFAULT_ID + 1
        ) == Piece.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            Piece.DEFAULT_ID + 2
        ) == Piece.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            Piece.DEFAULT_ID + 3
        ) == Piece.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            Piece.DEFAULT_ID + 4
        ) == Piece.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            Piece.DEFAULT_ID + 5
        ) == Piece.DEFAULT_PLUS_ID
