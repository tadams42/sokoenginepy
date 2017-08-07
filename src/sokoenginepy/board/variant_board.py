import re
import textwrap
from abc import ABCMeta, abstractmethod
from collections.abc import Container
from functools import reduce

import networkx

from .. import settings, tessellation, utilities
from .board_cell import BoardCell, BoardConversionError
from .graph import BoardGraph

_RE_BOARD_STRING = re.compile(
    r"^([0-9\s" + re.escape("".join(c for c in BoardCell.Characters)) +
    re.escape("".join(c for c in utilities.RleCharacters)) + "])*$"
)


class VariantBoard(Container, metaclass=ABCMeta):
    """Base board class for variant specific implementations.

    Internally it is stored as directed graph structure.

    Implements concerns of

        - board cell access/editing
        - string (de)serialization
        - resizing
        - board-space searching

    All positions are int indexes of graph vertices. To convert 2D coordinate
    into vertex index, use :func:`.index_1d`

    Args:
        tessellation_or_description (Tessellation): game tessellation or string
            describing it
        board_width (int): number of columns
        board_height (int): number of rows
        board_str (string): textual representation of board
    """

    @classmethod
    def instance_from(
        cls, tessellation_or_description, board_width=0, board_height=0,
        board_str=""
    ):

        #pylint: disable=unused-variable
        from .hexoban_board import HexobanBoard
        from .octoban_board import OctobanBoard
        from .sokoban_board import SokobanBoard
        from .trioban_board import TriobanBoard

        tessellation_instance = tessellation.Tessellation.instance_from(
            tessellation_or_description
        )

        for klass in VariantBoard.__subclasses__():
            if tessellation_instance.name.lower() in klass.__name__.lower():
                return klass(
                    board_width=board_width, board_height=board_height,
                    board_str=board_str
                )

        raise tessellation.UnknownTessellationError(tessellation)

    def __init__(
        self, tessellation_or_description, board_width=0, board_height=0,
        board_str=""
    ):
        super().__init__()
        self._tessellation_instance = tessellation.Tessellation.instance_from(
            tessellation_or_description
        ).value
        self._graph = None
        self._width = 0
        self._height = 0
        self._resizer = self._resizer_class(self)

        if not utilities.is_blank(board_str):
            self._reinit_with_string(board_str)
        else:
            self._reinit(board_width, board_height)

    @property
    def tessellation(self):
        return self._tessellation_instance

    @classmethod
    def is_board_string(cls, line):
        """
        Checks if line contains only characters legal in textual representation
        of boards.

        Note:
            Doesn't check if it actually contains legal board, it only checks
            that there are no illegal characters. To find out if line is actual
            board representation, it must be converted to actual game board.
        """
        return (
            not utilities.contains_only_digits_and_spaces(line) and reduce(
                lambda x, y: x and y, [
                    True if _RE_BOARD_STRING.match(l) else False
                    for l in line.splitlines()
                ], True
            )
        )

    @classmethod
    def parse_board_string(cls, line):
        """Tries to parse board from string.

        Returns:
            list: list of board strings, each representing single board line
        """
        if utilities.is_blank(line):
            return []
        if not cls.is_board_string(line):
            raise BoardConversionError(
                "Illegal characters found in board string"
            )

        line = utilities.rle_decode(line)
        return utilities.normalize_width(line.split('\n'))

    @property
    @abstractmethod
    def _resizer_class(self):
        """
        subclass of VariantBoardResizer
        """
        pass

    def _reinit(self, width, height, reconfigure_edges=True):
        self._graph = BoardGraph(width * height, self.tessellation.graph_type)

        self._width = width
        self._height = height

        if reconfigure_edges:
            self._graph.reconfigure_edges(
                self.width, self.height, self.tessellation
            )

    def _reinit_with_string(self, board_str, reconfigure_edges=True):
        if not utilities.is_blank(board_str):
            board_rows = self._parse_string(board_str)
            width = len(board_rows[0]) if len(board_rows) > 0 else 0
            height = len(board_rows)
            self._reinit(width, height, reconfigure_edges)
            for y, row in enumerate(board_rows):
                for x, character in enumerate(row):
                    self._graph[utilities.index_1d(x, y, self._width)
                               ] = BoardCell(character)

    def __eq__(self, rv):
        if (self.tessellation == rv.tessellation and self.width == rv.width and
                self.height == rv.height):
            for vertex in range(0, self.size):
                if self[vertex] != rv[vertex]:
                    return False
            return True
        else:
            return False

    def __ne__(self, rv):
        return not self == rv

    @abstractmethod
    def _parse_string(self, board_str):
        """Override this in subclass to handle tessellation speciffic strings.

        Should return list of strings where each string represents all BoardCell
        in single line of game board.
        """
        return self.parse_board_string(board_str)

    def __getitem__(self, position):
        try:
            return self._graph[position]
        except IndexError:
            raise IndexError('Board index out of range')
        except KeyError:
            raise IndexError('Board index out of range')
        except networkx.NetworkXError:
            raise IndexError('Board index out of range')
        except ValueError:
            raise IndexError('Board index out of range')

    def __setitem__(self, position, board_cell):
        try:
            if isinstance(board_cell, BoardCell):
                self._graph[position] = board_cell
            else:
                self._graph[position] = BoardCell(board_cell)
        except IndexError:
            raise IndexError('Board index out of range')
        except KeyError:
            raise IndexError('Board index out of range')
        except networkx.NetworkXError:
            raise IndexError('Board index out of range')
        except ValueError:
            raise IndexError('Board index out of range')

    def __contains__(self, position):
        return position in self._graph

    def __str__(self):
        """
        Override this in subclass to handle tessellation speciffic strings.
        """
        rows = []
        for y in range(0, self.height):
            row = "".join(
                str(cell)
                for cell in (
                    self[utilities.index_1d(x, y, self.width)]
                    for x in range(0, self.width)
                )
            )
            # Intentionally rstripping only if not using visible floors
            row = row.rstrip()
            if settings.RLE_ENCODE_BOARD_STRINGS:
                row = utilities.rle_encode(row)
            rows.append(row)

        if settings.RLE_ENCODE_BOARD_STRINGS:
            return utilities.RleCharacters.RLE_ROW_SEPARATOR.join(rows)
        else:
            return "\n".join(rows)

    def __repr__(self):
        board_str = textwrap.indent(
            ',\n'.join(["'{0}'".format(l) for l in str(self).split('\n')]),
            '    '
        )
        return "{klass}(board_str='\\n'.join([\n{board_str}\n]))".format(
            klass=self.__class__.__name__, board_str=board_str
        )

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def size(self):
        return self._width * self._height

    def neighbor(self, from_position, direction):
        """
        Returns:
            int: neighbor position in ``direction`` or None if neighbor
            position in ``direction`` would lead of board

        Raises:
            IndexError: if ``from_position`` is out of board position
        """
        try:
            return self._graph.neighbor(from_position, direction)
        except IndexError:
            raise IndexError('Board index out of range')
        except KeyError:
            raise IndexError('Board index out of range')
        except networkx.NetworkXError:
            raise IndexError('Board index out of range')
        except ValueError:
            raise IndexError('Board index out of range')

    def wall_neighbors(self, from_position):
        """
        Returns:
            list: of neighbor positions that are walls
        """
        try:
            return self._graph.wall_neighbors(from_position)
        except IndexError:
            raise IndexError('Board index out of range')
        except KeyError:
            raise IndexError('Board index out of range')
        except networkx.NetworkXError:
            raise IndexError('Board index out of range')
        except ValueError:
            raise IndexError('Board index out of range')

    def all_neighbors(self, from_position):
        """
        Returns:
            list: of neighbor positions
        """
        try:
            return self._graph.all_neighbors(from_position)
        except IndexError:
            raise IndexError('Board index out of range')
        except KeyError:
            raise IndexError('Board index out of range')
        except networkx.NetworkXError:
            raise IndexError('Board index out of range')
        except ValueError:
            raise IndexError('Board index out of range')

    def clear(self):
        """Empties all board cells."""
        for vertex in range(0, self.size):
            self[vertex].clear()

    def mark_play_area(self):
        """
        Returns:
            list: of positions that are playable (reachable by any box or
            pusher)
        """
        piece_positions = []
        for vertex in range(0, self.size):
            if self[vertex].has_box or self[vertex].has_pusher:
                self[vertex].is_in_playable_area = True
                piece_positions.append(vertex)
            else:
                self[vertex].is_in_playable_area = False

        def is_obstacle(vertex):
            return self[vertex].is_wall

        for piece_position in piece_positions:
            reachables = self._graph.reachables(
                root=piece_position, is_obstacle_callable=is_obstacle
            )

            for reachable_vertex in reachables:
                self[reachable_vertex].is_in_playable_area = True

    def positions_reachable_by_pusher(
        self, pusher_position, excluded_positions=None
    ):
        """
        Returns:
            list: of positions that are reachable by pusher standing on
            ``position``
        """

        def is_obstacle(position):
            return not self[position].can_put_pusher_or_box

        try:
            return self._graph.reachables(
                root=pusher_position, is_obstacle_callable=is_obstacle,
                excluded_positions=excluded_positions
            )
        except IndexError:
            raise IndexError('Board index out of range')
        except KeyError:
            raise IndexError('Board index out of range')
        except networkx.NetworkXError:
            raise IndexError('Board index out of range')
        except ValueError:
            raise IndexError('Board index out of range')

    def normalized_pusher_position(
        self, pusher_position, excluded_positions=None
    ):
        """
        Returns:
            int: Top-left position reachable by pusher
        """
        try:
            reachables = self.positions_reachable_by_pusher(
                pusher_position=pusher_position,
                excluded_positions=excluded_positions
            )
            if reachables:
                return min(reachables)
            else:
                return pusher_position
        except IndexError:
            raise IndexError('Board index out of range')
        except KeyError:
            raise IndexError('Board index out of range')
        except networkx.NetworkXError:
            raise IndexError('Board index out of range')
        except ValueError:
            raise IndexError('Board index out of range')

    def path_destination(self, start_position, direction_path):
        if start_position not in self:
            raise IndexError('Board index out of range')

        try:
            retv = start_position
            for direction in direction_path:
                next_target = self.neighbor(retv, direction)
                if next_target:
                    retv = next_target
                else:
                    break
            return retv
        except IndexError:
            raise IndexError('Board index out of range')
        except KeyError:
            raise IndexError('Board index out of range')
        except networkx.NetworkXError:
            raise IndexError('Board index out of range')
        except ValueError:
            raise IndexError('Board index out of range')

    def find_jump_path(self, start_position, end_position):
        """
        Returns:
            list: of positions through which pusher must pass when jumping
        """
        if start_position not in self:
            raise IndexError('Board index out of range')
        return self._graph.shortest_path(start_position, end_position)

    def find_move_path(self, start_position, end_position):
        """
        Returns:
            list: of positions through which pusher must pass when moving
            without pushing boxes
        """
        if start_position not in self:
            raise IndexError('Board index out of range')

        path = self._graph.dijkstra_path(start_position, end_position)

        retv = path[:1]
        for position in path[1:]:
            if self[position].can_put_pusher_or_box:
                retv.append(position)
            else:
                break
        if retv != path:
            return []
        return path

    def cell_orientation(self, position):
        """
        Returns:
            CellOrientation: game variant specific parameter
        """
        return self.tessellation.cell_orientation(
            position, self._width, self._height
        )

    def position_path_to_direction_path(self, position_path):
        """
        Returns:
            list: of :class:`.Direction`
        """
        try:
            return self._graph.position_path_to_direction_path(position_path)
        except IndexError:
            raise IndexError('Board index out of range')
        except KeyError:
            raise IndexError('Board index out of range')
        except networkx.NetworkXError:
            raise IndexError('Board index out of range')
        except ValueError:
            raise IndexError('Board index out of range')

    def add_row_top(self):
        self._resizer.add_row_top(reconfigure_edges=True)

    def add_row_bottom(self):
        self._resizer.add_row_bottom(reconfigure_edges=True)

    def add_column_left(self):
        self._resizer.add_column_left(reconfigure_edges=True)

    def add_column_right(self):
        self._resizer.add_column_right(reconfigure_edges=True)

    def remove_row_top(self):
        self._resizer.remove_row_top(reconfigure_edges=True)

    def remove_row_bottom(self):
        self._resizer.remove_row_bottom(reconfigure_edges=True)

    def remove_column_left(self):
        self._resizer.remove_column_left(reconfigure_edges=True)

    def remove_column_right(self):
        self._resizer.remove_column_right(reconfigure_edges=True)

    def trim_left(self):
        self._resizer.trim_left(reconfigure_edges=True)

    def trim_right(self):
        self._resizer.trim_right(reconfigure_edges=True)

    def trim_top(self):
        self._resizer.trim_top(reconfigure_edges=True)

    def trim_bottom(self):
        self._resizer.trim_bottom(reconfigure_edges=True)

    def reverse_rows(self):
        self._resizer.reverse_rows(reconfigure_edges=True)

    def reverse_columns(self):
        self._resizer.reverse_columns(reconfigure_edges=True)

    def resize(self, new_width, new_height):
        old_width = self.width
        old_height = self.height

        if new_height != old_height:
            if new_height > old_height:
                amount = new_height - old_height
                for _ in range(0, amount):
                    self._resizer.add_row_bottom(reconfigure_edges=False)
            else:
                amount = old_height - new_height
                for _ in range(0, amount):
                    self._resizer.remove_row_bottom(reconfigure_edges=False)

        if new_width != old_width:
            if new_width > old_width:
                amount = new_width - old_width
                for _ in range(0, amount):
                    self._resizer.add_column_right(reconfigure_edges=False)
            else:
                amount = old_width - new_width
                for _ in range(0, amount):
                    self._resizer.remove_column_right(reconfigure_edges=False)

        if old_width != self.width or old_height != self.height:
            self._graph.reconfigure_edges(
                self.width, self.height, self.tessellation
            )

    def resize_and_center(self, new_width, new_height):
        left = right = top = bottom = 0

        if new_width > self.width:
            left = int((new_width - self.width) / 2)
            right = new_width - self.width - left

        if new_height > self.height:
            top = int((new_height - self.height) / 2)
            bottom = new_height - self.height - top

        if (left, right, top, bottom) != (0, 0, 0, 0):
            for _ in range(0, left):
                self._resizer.add_column_left(reconfigure_edges=False)
            for _ in range(0, top):
                self._resizer.add_row_top(reconfigure_edges=False)

            self.resize(self.width + right, self.height + bottom)

    def trim(self):
        old_width = self.width
        old_height = self.height

        self._resizer.trim_top(reconfigure_edges=False)
        self._resizer.trim_bottom(reconfigure_edges=False)
        self._resizer.trim_left(reconfigure_edges=False)
        self._resizer.trim_right(reconfigure_edges=False)

        if old_width != self.width or old_height != old_height:
            self._graph.reconfigure_edges(
                self.width, self.height, self.tessellation
            )


class VariantBoardResizer(metaclass=ABCMeta):
    """
    Implements board graph transformations related to adding/removing board
    rows and columnns.
    """

    #pylint: disable=protected-access
    def __init__(self, variant_board):
        self.board = variant_board

    def add_row_top(self, reconfigure_edges):
        old_body = self.board._graph
        old_height = self.board.height

        self.board._reinit(
            self.board.width, self.board.height + 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, old_height):
                self.board[utilities.index_1d(x, y + 1, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, self.board.width)]

    def add_row_bottom(self, reconfigure_edges):
        old_body = self.board._graph
        old_height = self.board.height

        self.board._reinit(
            self.board.width, self.board.height + 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, old_height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, self.board.width)]

    def add_column_left(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width + 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, old_width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x + 1, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, old_width)]

    def add_column_right(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width + 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, old_width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, old_width)]

    def remove_row_top(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height - 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y + 1, self.board.width)]

    def remove_row_bottom(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height - 1,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, self.board.width)]

    def remove_column_left(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width - 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x + 1, y, old_width)]

    def remove_column_right(self, reconfigure_edges):
        old_body = self.board._graph
        old_width = self.board.width

        self.board._reinit(
            self.board.width - 1, self.board.height,
            reconfigure_edges=reconfigure_edges
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] =\
                    old_body[utilities.index_1d(x, y, old_width)]

    def trim_left(self, reconfigure_edges):
        amount = self.board.width
        for y in range(0, self.board.height):
            border_found = False
            for x in range(0, self.board.width):
                border_found = self.board[utilities.index_1d(
                    x, y, self.board.width
                )].is_border_element
                if border_found:
                    if x < amount:
                        amount = x
                    break

        for _ in range(0, amount):
            self.remove_column_left(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )

    def trim_right(self, reconfigure_edges):
        self.reverse_columns(reconfigure_edges=False)
        self.trim_left(reconfigure_edges=False)
        self.reverse_columns(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )

    def trim_top(self, reconfigure_edges):
        amount = self.board.height
        for x in range(0, self.board.width):
            border_found = False
            for y in range(0, self.board.height):
                border_found = self.board[utilities.index_1d(
                    x, y, self.board.width
                )].is_border_element
                if border_found:
                    if y < amount:
                        amount = y
                    break

        for _ in range(0, amount):
            self.remove_row_top(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )

    def trim_bottom(self, reconfigure_edges):
        self.reverse_rows(reconfigure_edges=False)
        self.trim_top(reconfigure_edges=False)
        self.reverse_rows(reconfigure_edges=False)

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )

    def reverse_rows(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height, reconfigure_edges=False
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] = \
                    old_body[utilities.index_1d(
                        x, self.board.height - y - 1, self.board.width
                    )]

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )

    def reverse_columns(self, reconfigure_edges):
        old_body = self.board._graph

        self.board._reinit(
            self.board.width, self.board.height, reconfigure_edges=False
        )

        for x in range(0, self.board.width):
            for y in range(0, self.board.height):
                self.board[utilities.index_1d(x, y, self.board.width)] = \
                    old_body[utilities.index_1d(
                        self.board.width - x - 1, y, self.board.width
                    )]

        if reconfigure_edges:
            self.board._graph.reconfigure_edges(
                self.board.width, self.board.height, self.board.tessellation
            )
