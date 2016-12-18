from abc import ABC, abstractmethod

from .. import game, snapshot
from .cell_orientation import CellOrientation
from .direction import UnknownDirectionError

_TESSELLATIONS = dict()


class Tessellation(ABC):
    """Base class for all variant tessellation implementations."""

    @classmethod
    def instance_for(cls, variant=game.Variant.SOKOBAN):
        from .hexoban_tessellation import HexobanTessellation
        from .octoban_tessellation import OctobanTessellation
        from .sokoban_tessellation import SokobanTessellation
        from .trioban_tessellation import TriobanTessellation

        variant = game.Variant.instance_from(variant)

        for klass in cls.__subclasses__():
            if variant.name.lower() in klass.__name__.lower():
                if variant not in _TESSELLATIONS.keys():
                    _TESSELLATIONS[variant] = klass()
                return _TESSELLATIONS[variant]

        raise game.UnknownVariantError(variant)

    @property
    @abstractmethod
    def legal_directions(self):
        """Directions generally accepted by Tessellation.

        Returns:
            list: of :class:`.Direction`
        """
        pass

    @abstractmethod
    def neighbor_position(self, position, direction, board_width, board_height):
        """Calculates neighbor position in given direction and verifies calculated position.

        Returns:
            int: If resulting position is off-board returns None, otherwise position

        Raises:
            :exc:`.UnknownDirectionError`: in case direction is not one of self.legal_directions

        Position is always expressed as int index of board graph vertex. To
        convert 2D coordinates into vertex index, use :func:`.index_1d` method
        """
        pass

    @property
    @abstractmethod
    def _char_to_atomic_move_dict(self):
        """Dict mapping string to :class:`.AtomicMove` parameters,"""
        pass

    @property
    @abstractmethod
    def graph_type(self):
        """Type of graph used in given tessellation."""
        pass

    def char_to_atomic_move(self, input_chr):
        """
        Converts string to :class:`.AtomicMove` instance or raises
        :exc:`.UnknownDirectionError` if conversion not possible.
        """
        if isinstance(input_chr, snapshot.AtomicMove.Characters):
            input_chr = input_chr.value

        direction, box_moved = self._char_to_atomic_move_dict.get(
            input_chr, (None, None)
        )

        if direction is None:
            raise UnknownDirectionError(input_chr)

        return snapshot.AtomicMove(direction=direction, box_moved=box_moved)

    @property
    @abstractmethod
    def _atomic_move_to_char_dict(self):
        """Dict mapping :class:`.AtomicMove` parameters to string representation."""
        pass

    def atomic_move_to_char(self, atomic_move):
        """
        Converts :class:`.AtomicMove` to string or raises
        :exc:`.UnknownDirectionError` if conversion not possible.
        """
        retv = self._atomic_move_to_char_dict.get(
            (atomic_move.direction, atomic_move.is_push_or_pull), None
        )

        if retv is None:
            raise UnknownDirectionError(atomic_move)

        return retv

    def cell_orientation(self, position, board_width, board_height):
        """Calculates board cell orientation for given position.

        Returns:
            CellOrientation: cell orientation for given ``position``
        """
        return CellOrientation.DEFAULT
