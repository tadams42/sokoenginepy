try:
    from sokoenginepyext import AtomicMove, InvalidAtomicMoveError
except ImportError:
    from .atomic_move import AtomicMove, InvalidAtomicMoveError
