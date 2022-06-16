from sokoenginepy.game import (
    Config,
    Direction,
    JumpCommand,
    MoveCommand,
    Mover,
    PusherStep,
    SelectPusherCommand,
    SolvingMode,
)

from .mover_spec import (
    forward_board,
    jump_dest,
    jumps,
    pusher_selections,
    reverse_board,
    undone_jumps,
    undone_pusher_selections,
)


class DescribeSelectPusherCommand:
    def it_executes_pusher_selection(
        self, forward_board, pusher_selections, undone_pusher_selections
    ):
        forward_mover = Mover(forward_board)
        command = SelectPusherCommand(forward_mover, Config.DEFAULT_PIECE_ID + 1)

        assert command.old_pusher_id == forward_mover.selected_pusher
        assert command.new_pusher_id == Config.DEFAULT_PIECE_ID + 1

        command.redo()
        assert command.moves in pusher_selections
        assert command.rendered in pusher_selections
        assert forward_mover.selected_pusher == Config.DEFAULT_PIECE_ID + 1

        command.undo()
        assert command.moves in pusher_selections
        assert command.rendered in undone_pusher_selections
        assert forward_mover.selected_pusher == Config.DEFAULT_PIECE_ID

        command.redo()
        assert command.moves in pusher_selections
        assert command.rendered in pusher_selections
        assert forward_mover.selected_pusher == Config.DEFAULT_PIECE_ID + 1

        command.undo()
        assert command.moves in pusher_selections
        assert command.rendered in undone_pusher_selections
        assert forward_mover.selected_pusher == Config.DEFAULT_PIECE_ID


class DescribeJumpCommand:
    def it_executes_jump(self, forward_board, jumps, undone_jumps, jump_dest):
        reverse_mover = Mover(forward_board, SolvingMode.REVERSE)
        command = JumpCommand(reverse_mover, jump_dest)

        assert command.initial_position == reverse_mover.board_manager.pusher_position(
            Config.DEFAULT_PIECE_ID
        )
        assert command.final_position == jump_dest

        command.redo()
        assert command.moves in jumps
        assert command.rendered in jumps
        assert (
            reverse_mover.board_manager.pusher_position(Config.DEFAULT_PIECE_ID) == jump_dest
        )

        command.undo()
        assert command.moves in jumps
        assert command.rendered in undone_jumps
        assert (
            reverse_mover.board_manager.pusher_position(Config.DEFAULT_PIECE_ID)
            == command.initial_position
        )

        command.redo()
        assert command.moves in jumps
        assert command.rendered in jumps
        assert (
            reverse_mover.board_manager.pusher_position(Config.DEFAULT_PIECE_ID) == jump_dest
        )

        command.undo()
        assert command.moves in jumps
        assert command.rendered in undone_jumps
        assert (
            reverse_mover.board_manager.pusher_position(Config.DEFAULT_PIECE_ID)
            == command.initial_position
        )


class DescribeMoveCommand:
    def it_executes_movement(self, forward_board):
        forward_mover = Mover(forward_board)
        command = MoveCommand(forward_mover, Direction.UP)

        command.redo()
        assert command.moves == [PusherStep(Direction.UP)]
        assert command.rendered == [PusherStep(Direction.UP)]

        command.undo()
        assert command.moves == [PusherStep(Direction.UP)]
        assert command.rendered == [PusherStep(Direction.DOWN)]

        command.redo()
        assert command.moves == [PusherStep(Direction.UP)]
        assert command.rendered == [PusherStep(Direction.UP)]

        command.undo()
        assert command.moves == [PusherStep(Direction.UP)]
        assert command.rendered == [PusherStep(Direction.DOWN)]
