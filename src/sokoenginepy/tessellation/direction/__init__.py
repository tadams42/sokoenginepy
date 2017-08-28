try:
    from libsokoengine import Direction
    Direction.__len__ = Direction._len()
except ImportError:
    from .direction import Direction

from .direction import UnknownDirectionError
