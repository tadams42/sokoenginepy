try:
    from sokoenginecpp import Direction
except ImportError:
    from .direction import Direction

from .direction import UnknownDirectionError
