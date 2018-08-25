try:
    from sokoenginepyext import HashedBoardManager
except ImportError:
    from .hashed_board_manager import HashedBoardManager
