import textwrap
from itertools import permutations

import pytest

from sokoenginepy.game import (
    BoardGraph,
    BoardManager,
    BoardState,
    CellAlreadyOccupiedError,
    Config,
    SokobanPlus,
    index_1d,
)
from sokoenginepy.io import SokobanPuzzle


@pytest.fixture
def puzzle():
    #   0123456789012345678
    data = """
        ----#####----------
        ----#--@#----------
        ----#$--#----------
        --###--$##---------
        --#--$-$-#---------
        ###-#-##-#---######
        #---#-##-#####--..#
        #-$--$----------..#
        #####-###-#@##--..#
        ----#-----#########
        ----#######--------
    """
    data = textwrap.dedent(data)
    return SokobanPuzzle(board=data)


@pytest.fixture
def board_graph(puzzle):
    return BoardGraph(puzzle)


@pytest.fixture
def switched_puzzle():
    #   0123456789012345678
    data = """
        ----#####----------
        ----#--@#----------
        ----#.--#----------
        --###--.##---------
        --#--.-.-#---------
        ###-#-##-#---######
        #---#-##-#####--$$#
        #-.--.----------$$#
        #####-###-#@##--$$#
        ----#-----#########
        ----#######--------
    """
    data = textwrap.dedent(data)
    return SokobanPuzzle(board=data)


@pytest.fixture
def pushers_positions(puzzle):
    return {
        Config.DEFAULT_ID: index_1d(7, 1, puzzle.width),
        Config.DEFAULT_ID + 1: index_1d(11, 8, puzzle.width),
    }


@pytest.fixture
def invalid_pusher_position():
    return index_1d(11, 8, 42)


@pytest.fixture
def boxes_positions(puzzle):
    return {
        Config.DEFAULT_ID: index_1d(5, 2, puzzle.width),
        Config.DEFAULT_ID + 1: index_1d(7, 3, puzzle.width),
        Config.DEFAULT_ID + 2: index_1d(5, 4, puzzle.width),
        Config.DEFAULT_ID + 3: index_1d(7, 4, puzzle.width),
        Config.DEFAULT_ID + 4: index_1d(2, 7, puzzle.width),
        Config.DEFAULT_ID + 5: index_1d(5, 7, puzzle.width),
    }


@pytest.fixture
def invalid_box_position():
    return index_1d(5, 7, 42)


@pytest.fixture
def goals_positions(puzzle):
    return {
        Config.DEFAULT_ID: index_1d(16, 6, puzzle.width),
        Config.DEFAULT_ID + 1: index_1d(17, 6, puzzle.width),
        Config.DEFAULT_ID + 2: index_1d(16, 7, puzzle.width),
        Config.DEFAULT_ID + 3: index_1d(17, 7, puzzle.width),
        Config.DEFAULT_ID + 4: index_1d(16, 8, puzzle.width),
        Config.DEFAULT_ID + 5: index_1d(17, 8, puzzle.width),
    }


@pytest.fixture
def invalid_goal_position():
    return index_1d(17, 8, 42)


@pytest.fixture
def all_solutions(goals_positions):
    def calc():
        for boxes_positions in permutations(goals_positions.values()):
            yield BoardState(
                boxes_positions=list(boxes_positions), pushers_positions=[]
            )

    return list(calc())


@pytest.fixture
def sokoban_plus_solutions():
    return [
        BoardState(
            boxes_positions=[149, 130, 131, 150, 168, 169], pushers_positions=[]
        ),
        BoardState(
            boxes_positions=[149, 130, 131, 150, 169, 168], pushers_positions=[]
        ),
        BoardState(
            boxes_positions=[149, 130, 131, 168, 150, 169], pushers_positions=[]
        ),
        BoardState(
            boxes_positions=[149, 130, 131, 168, 169, 150], pushers_positions=[]
        ),
        BoardState(
            boxes_positions=[149, 130, 131, 169, 150, 168], pushers_positions=[]
        ),
        BoardState(
            boxes_positions=[149, 130, 131, 169, 168, 150], pushers_positions=[]
        ),
    ]


@pytest.fixture
def switched_boxes(goals_positions):
    return {
        Config.DEFAULT_ID: goals_positions[Config.DEFAULT_ID],
        Config.DEFAULT_ID + 1: goals_positions[Config.DEFAULT_ID + 1],
        Config.DEFAULT_ID + 2: goals_positions[Config.DEFAULT_ID + 2],
        Config.DEFAULT_ID + 3: goals_positions[Config.DEFAULT_ID + 3],
        Config.DEFAULT_ID + 4: goals_positions[Config.DEFAULT_ID + 4],
        Config.DEFAULT_ID + 5: goals_positions[Config.DEFAULT_ID + 5],
    }


@pytest.fixture
def switched_goals(boxes_positions):
    return {
        Config.DEFAULT_ID: boxes_positions[Config.DEFAULT_ID],
        Config.DEFAULT_ID + 1: boxes_positions[Config.DEFAULT_ID + 1],
        Config.DEFAULT_ID + 2: boxes_positions[Config.DEFAULT_ID + 2],
        Config.DEFAULT_ID + 3: boxes_positions[Config.DEFAULT_ID + 3],
        Config.DEFAULT_ID + 4: boxes_positions[Config.DEFAULT_ID + 4],
        Config.DEFAULT_ID + 5: boxes_positions[Config.DEFAULT_ID + 5],
    }


@pytest.fixture
def switched_goals_plus(boxes_positions):
    # boxorder 1 3 2
    # goalorder 3 2 1
    # (box, goal) id pairs [(2, 1), (3, 2), (1, 3), (4, 4), (5, 5), (6, 6)]
    return {
        Config.DEFAULT_ID: boxes_positions[Config.DEFAULT_ID + 1],
        Config.DEFAULT_ID + 1: boxes_positions[Config.DEFAULT_ID + 2],
        Config.DEFAULT_ID + 2: boxes_positions[Config.DEFAULT_ID],
        Config.DEFAULT_ID + 3: boxes_positions[Config.DEFAULT_ID + 3],
        Config.DEFAULT_ID + 4: boxes_positions[Config.DEFAULT_ID + 4],
        Config.DEFAULT_ID + 5: boxes_positions[Config.DEFAULT_ID + 5],
    }


@pytest.fixture
def switched_boxes_plus(goals_positions):
    # boxorder 1 3 2
    # goalorder 3 2 1
    # (box, goal) id pairs [(2, 1), (3, 2), (1, 3), (4, 4), (5, 5), (6, 6)]
    return {
        Config.DEFAULT_ID: goals_positions[Config.DEFAULT_ID + 2],
        Config.DEFAULT_ID + 1: goals_positions[Config.DEFAULT_ID],
        Config.DEFAULT_ID + 2: goals_positions[Config.DEFAULT_ID + 1],
        Config.DEFAULT_ID + 3: goals_positions[Config.DEFAULT_ID + 3],
        Config.DEFAULT_ID + 4: goals_positions[Config.DEFAULT_ID + 4],
        Config.DEFAULT_ID + 5: goals_positions[Config.DEFAULT_ID + 5],
    }


@pytest.fixture
def boxes_ids():
    return [
        Config.DEFAULT_ID,
        Config.DEFAULT_ID + 1,
        Config.DEFAULT_ID + 2,
        Config.DEFAULT_ID + 3,
        Config.DEFAULT_ID + 4,
        Config.DEFAULT_ID + 5,
    ]


@pytest.fixture
def goals_ids():
    return [
        Config.DEFAULT_ID,
        Config.DEFAULT_ID + 1,
        Config.DEFAULT_ID + 2,
        Config.DEFAULT_ID + 3,
        Config.DEFAULT_ID + 4,
        Config.DEFAULT_ID + 5,
    ]


@pytest.fixture
def pusher_ids():
    return [Config.DEFAULT_ID, Config.DEFAULT_ID + 1]


@pytest.fixture
def normalized_pushers_positions(board_width):
    return {
        Config.DEFAULT_ID: index_1d(5, 1, board_width),
        Config.DEFAULT_ID + 1: index_1d(8, 4, board_width),
    }


class DescribeBoardManager:
    def it_memoizes_pushers(
        self, board_graph, pushers_positions, invalid_pusher_position
    ):
        board_manager = BoardManager(board_graph)

        assert board_manager.pushers_count == 2
        assert sorted(board_manager.pushers_ids) == list(pushers_positions.keys())
        assert board_manager.pushers_positions == pushers_positions

        for pusher_id, pusher_position in pushers_positions.items():
            assert board_manager.pusher_position(pusher_id) == pusher_position
            assert board_manager.pusher_id_on(pusher_position) == pusher_id
            assert board_manager.has_pusher(pusher_id)
            assert board_manager.has_pusher_on(pusher_position)

        with pytest.raises(KeyError):
            board_manager.pusher_position(
                Config.DEFAULT_ID + board_manager.pushers_count
            )
        with pytest.raises(KeyError):
            board_manager.pusher_id_on(invalid_pusher_position)

        assert not board_manager.has_pusher(
            Config.DEFAULT_ID + board_manager.pushers_count
        )
        assert not board_manager.has_pusher_on(invalid_pusher_position)

    def test_has_methods_dont_raise_for_invalid_args(self, board_graph):
        board_manager = BoardManager(board_graph)

        assert not board_manager.has_pusher(-1)
        assert not board_manager.has_pusher(42000)

        assert not board_manager.has_box(-1)
        assert not board_manager.has_box_on(42000)

        assert not board_manager.has_goal(-1)
        assert not board_manager.has_goal_on(42000)

    def it_memoizes_boxes(
        self, board_graph, boxes_positions, boxes_ids, invalid_box_position
    ):
        board_manager = BoardManager(board_graph)

        assert board_manager.boxes_count == 6
        assert sorted(board_manager.boxes_ids) == boxes_ids
        assert board_manager.boxes_positions == boxes_positions

        for box_id, box_position in boxes_positions.items():
            assert board_manager.box_position(box_id) == box_position
            assert board_manager.box_id_on(box_position) == box_id
            assert board_manager.has_box(box_id)
            assert board_manager.has_box_on(box_position)

        with pytest.raises(KeyError):
            board_manager.box_position(Config.DEFAULT_ID + board_manager.boxes_count)
        with pytest.raises(KeyError):
            board_manager.box_id_on(invalid_box_position)

        assert not board_manager.has_box(Config.DEFAULT_ID + board_manager.boxes_count)
        assert not board_manager.has_box_on(invalid_box_position)

        for box_id, box_position in boxes_positions.items():
            assert board_manager.box_plus_id(box_id) == SokobanPlus.DEFAULT_PLUS_ID

        # Doesn't rise KeyError if plus is disabled...
        assert (
            board_manager.box_plus_id(Config.DEFAULT_ID + board_manager.boxes_count)
            == SokobanPlus.DEFAULT_PLUS_ID
        )

        board_manager.boxorder = "1 3 2"
        board_manager.goalorder = "3 1 2"
        board_manager.enable_sokoban_plus()

        assert board_manager.box_plus_id(Config.DEFAULT_ID) == 1
        assert board_manager.box_plus_id(Config.DEFAULT_ID + 1) == 3
        assert board_manager.box_plus_id(Config.DEFAULT_ID + 2) == 2
        assert (
            board_manager.box_plus_id(Config.DEFAULT_ID + 3)
            == SokobanPlus.DEFAULT_PLUS_ID
        )
        assert (
            board_manager.box_plus_id(Config.DEFAULT_ID + 4)
            == SokobanPlus.DEFAULT_PLUS_ID
        )
        assert (
            board_manager.box_plus_id(Config.DEFAULT_ID + 5)
            == SokobanPlus.DEFAULT_PLUS_ID
        )

        with pytest.raises(KeyError):
            assert board_manager.box_plus_id(
                Config.DEFAULT_ID + board_manager.boxes_count
            )

    def it_memoizes_goals(
        self, board_graph, goals_positions, goals_ids, invalid_goal_position
    ):
        board_manager = BoardManager(board_graph)

        assert board_manager.goals_count == 6
        assert sorted(board_manager.goals_ids) == goals_ids
        assert board_manager.goals_positions == goals_positions

        for goal_id, goal_position in goals_positions.items():
            assert board_manager.goal_position(goal_id) == goal_position
            assert board_manager.goal_id_on(goal_position) == goal_id
            assert board_manager.has_goal(goal_id)
            assert board_manager.has_goal_on(goal_position)

        with pytest.raises(KeyError):
            board_manager.goal_position(Config.DEFAULT_ID + board_manager.goals_count)
        with pytest.raises(KeyError):
            board_manager.goal_id_on(invalid_goal_position)

        assert not board_manager.has_goal(Config.DEFAULT_ID + board_manager.goals_count)
        assert not board_manager.has_goal_on(invalid_goal_position)

        for goal_id, goal_position in goals_positions.items():
            assert board_manager.goal_plus_id(goal_id) == SokobanPlus.DEFAULT_PLUS_ID

        # Doesn't rise KeyError if plus is disabled...
        assert (
            board_manager.goal_plus_id(Config.DEFAULT_ID + board_manager.goals_count)
            == SokobanPlus.DEFAULT_PLUS_ID
        )

        board_manager.boxorder = "1 3 2"
        board_manager.goalorder = "3 1 2"
        board_manager.enable_sokoban_plus()

        assert board_manager.goal_plus_id(Config.DEFAULT_ID) == 3
        assert board_manager.goal_plus_id(Config.DEFAULT_ID + 1) == 1
        assert board_manager.goal_plus_id(Config.DEFAULT_ID + 2) == 2
        assert (
            board_manager.goal_plus_id(Config.DEFAULT_ID + 3)
            == SokobanPlus.DEFAULT_PLUS_ID
        )
        assert (
            board_manager.goal_plus_id(Config.DEFAULT_ID + 4)
            == SokobanPlus.DEFAULT_PLUS_ID
        )
        assert (
            board_manager.goal_plus_id(Config.DEFAULT_ID + 5)
            == SokobanPlus.DEFAULT_PLUS_ID
        )

        with pytest.raises(KeyError):
            assert board_manager.goal_plus_id(
                Config.DEFAULT_ID + board_manager.goals_count
            )

    def it_calculates_all_valid_board_solutions(
        self, board_graph, all_solutions, sokoban_plus_solutions
    ):
        board_manager = BoardManager(board_graph)

        assert list(board_manager.solutions()) == all_solutions

        board_manager.boxorder = "1 3 2"
        board_manager.goalorder = "3 2 1"
        board_manager.enable_sokoban_plus()

        assert list(board_manager.solutions()) == sokoban_plus_solutions

    def it_moves_boxes(self, board_graph):
        board_manager = BoardManager(board_graph)

        old_box_position = board_manager.box_position(Config.DEFAULT_ID)
        board_manager.move_box(Config.DEFAULT_ID, 0)
        assert board_manager.box_position(Config.DEFAULT_ID) == 0
        assert board_manager.has_box_on(0)
        assert not board_manager.has_box_on(old_box_position)
        assert board_manager.board[0].has_box
        assert not board_manager.board[old_box_position].has_box
        board_manager.move_box(Config.DEFAULT_ID, old_box_position)

        board_manager.move_box_from(old_box_position, 0)
        assert board_manager.box_position(Config.DEFAULT_ID) == 0
        assert board_manager.has_box_on(0)
        assert not board_manager.has_box_on(old_box_position)
        assert board_manager.board[0].has_box
        assert not board_manager.board[old_box_position].has_box

    def it_validates_positions_when_moving_boxes(self, board_graph):
        board_manager = BoardManager(board_graph)

        with pytest.raises(IndexError):
            board_manager.move_box(Config.DEFAULT_ID, 42000)
        with pytest.raises(IndexError):
            board_manager.move_box(Config.DEFAULT_ID, -1)

        old_box_position = board_manager.box_position(Config.DEFAULT_ID)
        with pytest.raises(IndexError):
            board_manager.move_box_from(old_box_position, 42000)
        with pytest.raises(IndexError):
            board_manager.move_box_from(old_box_position, -1)

        with pytest.raises(IndexError):
            board_manager.move_box_from(42000, 0)
        with pytest.raises(IndexError):
            board_manager.move_box_from(-1, 0)

    def it_moves_pushers(self, board_graph):
        board_manager = BoardManager(board_graph)

        old_pusher_position = board_manager.pusher_position(Config.DEFAULT_ID)
        board_manager.move_pusher(Config.DEFAULT_ID, 0)
        assert board_manager.pusher_position(Config.DEFAULT_ID) == 0
        assert board_manager.has_pusher_on(0)
        assert not board_manager.has_pusher_on(old_pusher_position)
        assert board_manager.board[0].has_pusher
        assert not board_manager.board[old_pusher_position].has_pusher
        board_manager.move_pusher(Config.DEFAULT_ID, old_pusher_position)

        board_manager.move_pusher_from(old_pusher_position, 0)
        assert board_manager.pusher_position(Config.DEFAULT_ID) == 0
        assert board_manager.has_pusher_on(0)
        assert not board_manager.has_pusher_on(old_pusher_position)
        assert board_manager.board[0].has_pusher
        assert not board_manager.board[old_pusher_position].has_pusher

    def it_validates_positions_when_moving_pushers(self, board_graph):
        board_manager = BoardManager(board_graph)

        with pytest.raises(IndexError):
            board_manager.move_pusher(Config.DEFAULT_ID, 42000)
        with pytest.raises(IndexError):
            board_manager.move_pusher(Config.DEFAULT_ID, -1)

        old_pusher_position = board_manager.pusher_position(Config.DEFAULT_ID)
        with pytest.raises(IndexError):
            board_manager.move_pusher_from(old_pusher_position, 42000)
        with pytest.raises(IndexError):
            board_manager.move_pusher_from(old_pusher_position, -1)

        with pytest.raises(IndexError):
            board_manager.move_pusher_from(42000, 0)
        with pytest.raises(IndexError):
            board_manager.move_pusher_from(-1, 0)

    def test_moving_box_onto_obstacle_raises_exception(
        self, board_graph, pushers_positions, boxes_positions
    ):
        wall_position = index_1d(4, 0, board_graph.board_width)
        board_manager = BoardManager(board_graph)
        box_id = Config.DEFAULT_ID
        box_position = board_manager.box_position(box_id)

        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_box(box_id, boxes_positions[Config.DEFAULT_ID + 1])
        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_box_from(
                box_position, boxes_positions[Config.DEFAULT_ID + 1]
            )

        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_box(box_id, pushers_positions[Config.DEFAULT_ID])
        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_box_from(
                box_position, pushers_positions[Config.DEFAULT_ID]
            )

        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_box(box_id, wall_position)
        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_box_from(box_position, wall_position)

    def test_moving_pusher_onto_obstacle_raises_exception(
        self, board_graph, boxes_positions, pushers_positions
    ):
        wall_position = index_1d(4, 0, board_graph.board_width)
        board_manager = BoardManager(board_graph)
        pusher_id = Config.DEFAULT_ID
        pusher_position = board_manager.pusher_position(pusher_id)

        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_pusher(pusher_id, boxes_positions[Config.DEFAULT_ID])
        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_pusher_from(
                pusher_position, boxes_positions[Config.DEFAULT_ID]
            )

        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_pusher(
                pusher_id, pushers_positions[Config.DEFAULT_ID + 1]
            )
        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_pusher_from(
                pusher_position, pushers_positions[Config.DEFAULT_ID + 1]
            )

        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_pusher(pusher_id, wall_position)
        with pytest.raises(CellAlreadyOccupiedError):
            board_manager.move_pusher_from(pusher_position, wall_position)

    def it_implements_switching_box_and_goal_positions(
        self,
        board_graph,
        boxes_positions,
        switched_boxes,
        goals_positions,
        switched_goals,
        puzzle,
        switched_puzzle,
    ):
        board_manager = BoardManager(board_graph)

        board_manager.switch_boxes_and_goals()
        assert board_manager.boxes_positions == switched_boxes
        assert board_manager.goals_positions == switched_goals
        assert str(board_manager.board) == str(switched_puzzle)

        board_manager.switch_boxes_and_goals()
        assert board_manager.boxes_positions == boxes_positions
        assert board_manager.goals_positions == goals_positions
        assert str(board_manager.board) == str(puzzle)

    def test_switching_respects_sokoban_plus_if_enabled(
        self,
        board_graph,
        switched_boxes_plus,
        switched_goals_plus,
        boxes_positions,
        goals_positions,
    ):
        board_manager = BoardManager(board_graph, boxorder="1 3 2", goalorder="3 2 1")

        board_manager.enable_sokoban_plus()

        board_manager.switch_boxes_and_goals()
        assert board_manager.boxes_positions == switched_boxes_plus
        assert board_manager.goals_positions == switched_goals_plus

        board_manager.switch_boxes_and_goals()
        assert board_manager.boxes_positions == boxes_positions
        assert board_manager.goals_positions == goals_positions

    def test_switching_moves_pusher_out_of_the_way(self):
        board = """
            ########
            #------#
            #--+---#
            #----$-#
            ########
        """
        board = textwrap.dedent(board)

        switched_board = """
            ########
            #------#
            #--$---#
            #----+-#
            ########
        """
        switched_board = textwrap.dedent(switched_board)

        puzzle = SokobanPuzzle(board=board)
        graph = BoardGraph(puzzle)
        board_manager = BoardManager(graph)

        board_manager.switch_boxes_and_goals()
        assert (
            board_manager.board.to_board_str(use_visible_floor=True)
            == switched_board.lstrip("\n").rstrip()
        )
        board_manager.switch_boxes_and_goals()
        assert (
            board_manager.board.to_board_str(use_visible_floor=True)
            == board.lstrip("\n").rstrip()
        )
