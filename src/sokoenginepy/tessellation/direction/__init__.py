try:
    from sokoenginepyext import Direction, UnknownDirectionError
except ImportError:
    from .direction import Direction, UnknownDirectionError
