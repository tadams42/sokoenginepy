from sokoenginepy.board import SokobanPlus
from sokoenginepy.common import DEFAULT_PIECE_ID
from sokoenginepy.tessellation import index_1d


class DescribeBoardState:

    def it_memoizes_pieces(self, board_state):
        width = board_state._variant_board.width

        assert board_state.board_size == board_state._variant_board.size

        assert board_state.pushers_count == 1
        assert sorted(board_state.pushers_ids) == [DEFAULT_PIECE_ID]
        assert board_state.pushers_positions == [index_1d(11, 8, width)]
        assert board_state.normalized_pusher_positions == {
            DEFAULT_PIECE_ID: index_1d(8, 4, width)
        }
        assert board_state.pusher_position(DEFAULT_PIECE_ID) == index_1d(
            11, 8, width
        )
        assert board_state.pusher_id(index_1d(11, 8, width)) == DEFAULT_PIECE_ID

        assert board_state.boxes_count == 6
        assert sorted(board_state.boxes_ids) == [
            DEFAULT_PIECE_ID, DEFAULT_PIECE_ID + 1, DEFAULT_PIECE_ID + 2,
            DEFAULT_PIECE_ID + 3, DEFAULT_PIECE_ID + 4, DEFAULT_PIECE_ID + 5
        ]
        assert board_state.boxes_positions == [
            index_1d(5, 2, width),
            index_1d(7, 3, width),
            index_1d(5, 4, width),
            index_1d(7, 4, width),
            index_1d(2, 7, width),
            index_1d(5, 7, width),
        ]
        assert board_state.box_position(DEFAULT_PIECE_ID) == index_1d(
            5, 2, width
        )
        assert board_state.box_position(DEFAULT_PIECE_ID + 1) == index_1d(
            7, 3, width
        )
        assert board_state.box_position(DEFAULT_PIECE_ID + 2) == index_1d(
            5, 4, width
        )
        assert board_state.box_position(DEFAULT_PIECE_ID + 3) == index_1d(
            7, 4, width
        )
        assert board_state.box_position(DEFAULT_PIECE_ID + 4) == index_1d(
            2, 7, width
        )
        assert board_state.box_position(DEFAULT_PIECE_ID + 5) == index_1d(
            5, 7, width
        )
        assert board_state.box_id(index_1d(5, 2, width)) == DEFAULT_PIECE_ID
        assert board_state.box_id(index_1d(7, 3, width)) == DEFAULT_PIECE_ID + 1
        assert board_state.box_id(index_1d(5, 4, width)) == DEFAULT_PIECE_ID + 2
        assert board_state.box_id(index_1d(7, 4, width)) == DEFAULT_PIECE_ID + 3
        assert board_state.box_id(index_1d(2, 7, width)) == DEFAULT_PIECE_ID + 4
        assert board_state.box_id(index_1d(5, 7, width)) == DEFAULT_PIECE_ID + 5
        assert board_state.box_plus_id(
            DEFAULT_PIECE_ID
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            DEFAULT_PIECE_ID + 1
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            DEFAULT_PIECE_ID + 2
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            DEFAULT_PIECE_ID + 3
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            DEFAULT_PIECE_ID + 4
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.box_plus_id(
            DEFAULT_PIECE_ID + 5
        ) == SokobanPlus.DEFAULT_PLUS_ID

        assert board_state.goals_count == 6
        assert sorted(board_state.goals_ids) == [
            DEFAULT_PIECE_ID, DEFAULT_PIECE_ID + 1, DEFAULT_PIECE_ID + 2,
            DEFAULT_PIECE_ID + 3, DEFAULT_PIECE_ID + 4, DEFAULT_PIECE_ID + 5
        ]
        assert board_state.goals_positions == [
            index_1d(16, 6, width),
            index_1d(17, 6, width),
            index_1d(16, 7, width),
            index_1d(17, 7, width),
            index_1d(16, 8, width),
            index_1d(17, 8, width),
        ]
        assert board_state.goal_position(DEFAULT_PIECE_ID) == index_1d(
            16, 6, width
        )
        assert board_state.goal_position(DEFAULT_PIECE_ID + 1) == index_1d(
            17, 6, width
        )
        assert board_state.goal_position(DEFAULT_PIECE_ID + 2) == index_1d(
            16, 7, width
        )
        assert board_state.goal_position(DEFAULT_PIECE_ID + 3) == index_1d(
            17, 7, width
        )
        assert board_state.goal_position(DEFAULT_PIECE_ID + 4) == index_1d(
            16, 8, width
        )
        assert board_state.goal_position(DEFAULT_PIECE_ID + 5) == index_1d(
            17, 8, width
        )
        assert board_state.goal_id(index_1d(16, 6, width)) == DEFAULT_PIECE_ID
        assert board_state.goal_id(index_1d(17, 6, width)
                                  ) == DEFAULT_PIECE_ID + 1
        assert board_state.goal_id(index_1d(16, 7, width)
                                  ) == DEFAULT_PIECE_ID + 2
        assert board_state.goal_id(index_1d(17, 7, width)
                                  ) == DEFAULT_PIECE_ID + 3
        assert board_state.goal_id(index_1d(16, 8, width)
                                  ) == DEFAULT_PIECE_ID + 4
        assert board_state.goal_id(index_1d(17, 8, width)
                                  ) == DEFAULT_PIECE_ID + 5
        assert board_state.goal_plus_id(
            DEFAULT_PIECE_ID
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            DEFAULT_PIECE_ID + 1
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            DEFAULT_PIECE_ID + 2
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            DEFAULT_PIECE_ID + 3
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            DEFAULT_PIECE_ID + 4
        ) == SokobanPlus.DEFAULT_PLUS_ID
        assert board_state.goal_plus_id(
            DEFAULT_PIECE_ID + 5
        ) == SokobanPlus.DEFAULT_PLUS_ID
