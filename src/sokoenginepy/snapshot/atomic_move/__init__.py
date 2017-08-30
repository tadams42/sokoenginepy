try:
    from sokoenginecpp import AtomicMove
except ImportError:
    from .atomic_move import AtomicMove

from .atomic_move import AtomicMoveCharacters
