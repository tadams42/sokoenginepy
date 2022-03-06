try:
    from sokoenginepyext import AtomicMove
except ImportError:
    from .atomic_move import AtomicMove
