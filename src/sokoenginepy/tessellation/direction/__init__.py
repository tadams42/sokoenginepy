try:
    from libsokoengine import Direction
except ImportError:
    from .direction import Direction

from .direction import UnknownDirectionError
