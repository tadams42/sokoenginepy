from abc import ABCMeta, abstractmethod
from typing import List, Mapping, Tuple

from .cell_orientation import CellOrientation
from .direction import Direction


class TessellationBase(metaclass=ABCMeta):
    """
    Base class for all tessellation implementations."""

    @property
    @abstractmethod
    def legal_directions(self) -> List[Direction]:
        """
        Directions generally accepted by Tessellation.

        Returns:
            list: sequence of :class:`.Direction`
        """
        pass

    @abstractmethod
    def neighbor_position(
        self, position: int, direction: Direction, board_width: int, board_height: int
    ) -> int:
        """
        Calculates neighbor position in given direction.

        Position is always expressed as 1D index of board graph vertex. To convert 2D
        coordinates into vertex index, use :func:`.index_1d` method

        Returns:
            int: If resulting position is off-board returns None, otherwise position

        Raises:
            :exc:`.ValueError`: in case direction is not one of
                self.legal_directions
        """
        pass

    @property
    @abstractmethod
    def _char_to_atomic_move_dict(self) -> Mapping[str, Tuple[Direction, bool]]:
        """Dict mapping string to :class:`.AtomicMove` parameters,"""
        pass

    @property
    @abstractmethod
    def graph_type(self) -> "GraphType":
        """
        Type of graph used in given tessellation.

        Returns:
            GraphType: type of graph
        """
        pass

    def char_to_atomic_move(self, input_chr: str) -> "AtomicMove":
        """
        Converts character to :class:`.AtomicMove`.

        Returns:
           AtomicMove: resulting :class:`.AtomicMove`

        Raises:
            :exc:`.ValueError` if conversion not possible.
        """
        from ..snapshot import AtomicMove

        direction, box_moved = self._char_to_atomic_move_dict.get(
            input_chr, (None, None)
        )

        if direction is None:
            raise ValueError(input_chr)

        return AtomicMove(direction=direction, box_moved=box_moved)

    @property
    @abstractmethod
    def _atomic_move_to_char_dict(self) -> Mapping[Tuple[Direction, bool], str]:
        """
        Dict mapping :class:`.AtomicMove` parameters to string representation.
        """
        pass

    def atomic_move_to_char(self, atomic_move: "AtomicMove") -> str:
        """
        Converts :class:`.AtomicMove` to string

        Returns:
           str: resulting string representation of :class:`.AtomicMove`

        Raises:
            :exc:`.ValueError` if conversion not possible.
        """
        retv = self._atomic_move_to_char_dict.get(
            (atomic_move.direction, atomic_move.is_push_or_pull), None
        )

        if retv is None:
            raise ValueError(atomic_move)

        return retv

    def cell_orientation(
        self, position: int, board_width: int, board_height: int
    ) -> CellOrientation:
        """
        Calculates board cell orientation for given position.

        Returns:
            CellOrientation: cell orientation for given ``position``
        """
        return CellOrientation.DEFAULT

    def __eq__(self, rv):
        return self.__class__.__name__ == rv.__class__.__name__

    def __ne__(self, other):
        return not self == other
