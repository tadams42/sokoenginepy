from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple, Union

import networkx as nx

from ..io import Puzzle
from .base_tessellation import BaseTessellation, Tessellation
from .board_cell import BoardCell
from .config import Config, Direction, GraphType

# (1, 0, {'direction': Direction.LEFT})
_InternalEdge = Tuple[int, int, Dict[str, Union[Direction, int]]]
BoardCellOrStr = Union[BoardCell, str]
Positions = List[int]
Directions = List[Direction]


@dataclass
class Edge:
    """
    `BoardGraph` edge.
    """

    u: int
    v: int
    direction: Direction


class BoardGraph:
    """
    Board graph.

    Depending on how ``sokoenginepy`` was installed, it is using either ``NetworkX`` or
    ``Boost.Graph`` under the hood.

    Raises:
        ValueError: when ``puzzle`` width is greater than `.Config.MAX_WIDTH` or
            or ``puzzle`` height is greater than `.Config.MAX_HEIGHT`
    """

    _KEY_CELL = "cell"
    _KEY_DIRECTION = "direction"
    _MAX_EDGE_WEIGHT = 100  # must be > len(Direction)

    def __init__(self, puzzle: Puzzle):
        if puzzle.width > Config.MAX_HEIGHT:
            raise ValueError(
                f"Puzzle width {puzzle.width} must be <= Config.MAX_WIDTH!"
            )
        if puzzle.height > Config.MAX_WIDTH:
            raise ValueError(
                f"Puzzle height {puzzle.height} must be <= Config.MAX_HEIGHT!"
            )

        self._board_width = puzzle.width
        self._board_height = puzzle.height
        self._tessellation = puzzle.tessellation

        tessellation = BaseTessellation.instance(self._tessellation)
        if tessellation.graph_type == GraphType.DIRECTED:
            self._graph = nx.DiGraph()
        elif tessellation.graph_type == GraphType.DIRECTED_MULTI:
            self._graph = nx.MultiDiGraph()
        else:
            raise ValueError(f"Unknown graph_type: {tessellation.graph_type.name}!")

        for position in range(0, self.board_width * self.board_height):
            self._graph.add_node(
                position, **{self._KEY_CELL: BoardCell(puzzle[position])}
            )
        self._reconfigure_edges()

    def __getitem__(self, position: int) -> BoardCell:
        """
        Raises:
            IndexError: ``position`` is off board
        """

        try:
            return self._graph.nodes[position][self._KEY_CELL]

        except KeyError as e:
            raise IndexError(f"Board index {position} is out of range!") from e

    def __setitem__(self, position: int, board_cell: BoardCellOrStr):
        """
        Raises:
            IndexError: ``position`` is off board
        """

        try:
            if isinstance(board_cell, BoardCell):
                self._graph.nodes[position][self._KEY_CELL] = board_cell
            else:
                self._graph.nodes[position][self._KEY_CELL] = BoardCell(board_cell)

        except (KeyError, IndexError, nx.NetworkXError) as e:
            raise IndexError(f"Board index {position} is out of range!") from e

    def __contains__(self, position: int) -> bool:
        return position in self._graph

    @property
    def tessellation(self) -> Tessellation:
        return self._tessellation

    def to_board_str(self, use_visible_floor=False, rle_encode=False) -> str:
        puzzle = Puzzle.instance_from(
            self._tessellation, self._board_width, self._board_height
        )

        for pos in range(self._vertices_count):
            puzzle[pos] = self[pos].to_str()

        return puzzle.to_board_str(use_visible_floor, rle_encode)

    def __str__(self) -> str:
        return self.to_board_str(False)

    @property
    def size(self) -> int:
        return self._board_width * self._board_height

    @property
    def edges_count(self) -> int:
        return self._graph.number_of_edges()

    @property
    def board_width(self) -> int:
        return self._board_width

    @property
    def board_height(self) -> int:
        return self._board_height

    def out_edges(self, src: int) -> List[Edge]:
        """
        Edges inspector, for debugging purposes.

        Raises:
            IndexError: ``src`` is off board
        """
        retv = []

        try:
            for out_edge in self._graph.edges(src, data=True):
                retv.append(
                    Edge(
                        u=src,
                        v=out_edge[1],
                        direction=out_edge[2][self._KEY_DIRECTION],
                        # weight=out_edge[2].get("weight", None),
                    )
                )

        except (KeyError, IndexError, nx.NetworkXError) as e:
            raise IndexError(f"Board index {src} is out of range!")

        return retv

    def neighbor(self, src: int, direction: Direction) -> int:
        """
        Neighbor position in ``direction``.

        Returns:
            Target position or Config.NO_POS

        Raises:
            IndexError: ``src`` is off board
        """
        out_edge: InternalEdge
        if self[src]:
            for out_edge in self._graph.edges(src, data=True):
                if out_edge[2][self._KEY_DIRECTION] == direction:
                    return out_edge[1]

        return Config.NO_POS

    def wall_neighbors(self, src: int) -> Positions:
        """
        Raises:
            IndexError: ``src`` off board
        """
        if self[src]:
            return [n for n in self._graph.neighbors(src) if self[n].is_wall]

        return []

    def all_neighbors(self, src: int) -> Positions:
        """
        Raises:
            IndexError: ``src`` off board
        """

        if self[src]:
            return list(self._graph.neighbors(src))

        return []

    def shortest_path(self, src: int, dst: int) -> Positions:
        """
        Calculates shortest path between two positions with all positions having equal
        weight.

        Raises:
            IndexError: ``src`` or ``dst`` off board
        """

        if self[src] and self[dst]:
            edge: _InternalEdge
            for edge in self._graph.edges(data=True):
                edge[2]["weight"] = 1

            try:
                return nx.shortest_path(self._graph, src, dst, 1)
            except nx.NetworkXNoPath:
                return []

        return []

    def dijkstra_path(self, src: int, dst: int) -> Positions:
        """
        Calculates shortest path between two positions not passing through board
        obstacles (walls, boxes, other pushers, etc...).

        Raises:
            IndexError: ``src`` or ``dst`` off board
        """
        if self[src] and self[dst]:
            edge: _InternalEdge
            for edge in self._graph.edges(data=True):
                edge[2]["weight"] = self._out_edge_weight(edge[1])

            try:
                return nx.dijkstra_path(self._graph, src, dst)
            except nx.NetworkXNoPath:
                return []

        return []

    def find_jump_path(self, src: int, dst: int) -> Positions:
        """
        Finds list of positions through which pusher must pass when jumping

        Raises:
            IndexError: ``src`` or ``dst`` off board
        """
        return self.shortest_path(src, dst)

    def find_move_path(self, src: int, dst: int) -> Positions:
        """
        Finds list of positions through which pusher must pass when moving without
        pushing boxes

        Raises:
            IndexError: ``src`` or ``dst`` off board
        """
        path = self.dijkstra_path(src, dst)

        retv = path[:1]
        for position in path[1:]:
            if self[position].can_put_pusher_or_box:
                retv.append(position)
            else:
                break
        if retv != path:
            return []
        return path

    def positions_path_to_directions_path(self, positions: Positions) -> Directions:
        """
        Converts path expressed as positions to one expressed as :class:`.Direction`.

        Raises:
            IndexError: Any of positions in ``positions`` off board
        """

        if positions:
            self[positions[0]]
        else:
            return []

        retv = []

        src_position_index = 0
        out_edge: _InternalEdge
        for dst in positions[1:]:
            src_position = positions[src_position_index]
            src_position_index += 1

            if self[src_position] and self[dst]:
                for out_edge in self._graph.edges(src_position, data=True):
                    if out_edge[1] == dst:
                        retv.append(out_edge[2][self._KEY_DIRECTION])

        return retv

    def mark_play_area(self):
        """
        Sets flag on all :class:`.BoardCell` in graph that are playable: reachable by
        any box or any pusher.
        """
        piece_positions = []
        for position in range(0, self._vertices_count):
            if self[position].has_box or self[position].has_pusher:
                self[position].is_in_playable_area = True
                piece_positions.append(position)
            else:
                self[position].is_in_playable_area = False

        for piece_position in piece_positions:
            reachables = self._reachables(
                root=piece_position, is_obstacle_cb=lambda x: self[x].is_wall
            )

            for reachable_position in reachables:
                self[reachable_position].is_in_playable_area = True

    def positions_reachable_by_pusher(
        self, pusher_position: int, excluded_positions: Optional[Positions] = None
    ) -> Positions:
        """
        Finds all positions that are reachable by pusher standing on
        ``pusher_position``.

        Doesn't require that ``pusher_position`` actually has pusher.

        Raises:
            IndexError: when ``pusher_position`` is off board. Doesn't throw if any
                position in ``excluded_positions`` is off board; it simply ignores those
        """
        return self._reachables(
            root=pusher_position,
            is_obstacle_cb=lambda x: not self[x].can_put_pusher_or_box,
            excluded_positions=excluded_positions,
        )

    def normalized_pusher_position(
        self, pusher_position: int, excluded_positions: Optional[Positions] = None
    ) -> int:
        """
        Finds top-left position reachable by pusher without pushing any boxes.

        Doesn't require that ``pusher_position`` actually has pusher.

        Raises:
            IndexError: when ``pusher_position`` is off board. Doesn't throw if any
                position in ``excluded_positions`` is off board; it simply ignores those
        """
        reachables = self.positions_reachable_by_pusher(
            pusher_position=pusher_position, excluded_positions=excluded_positions
        )
        if reachables:
            return min(reachables)
        else:
            return pusher_position

    def path_destination(self, src: int, directions: Directions) -> int:
        """
        Given movement path ``directions``, calculates position at the end of tha
        movement.

        If any direction in ``directions`` would've lead off board, stops the
        search and returns position reached up to that point.
        """
        if not directions:
            self[src]

        retv = src
        for direction in directions:
            next_target = self.neighbor(retv, direction)
            if next_target != Config.NO_POS:
                retv = next_target
            else:
                break
        return retv

    def _out_edges_count(self, src: int, dst: int) -> int:
        """
        Number of out-edges from ``src`` to ``dst``.

        Returns:
            Zero when no out edges exist or or any of positions is illegal type or out
            of board position.
        """
        try:
            # retv = self._graph.number_of_edges(src, dst)
            retv = len(self._graph[src][dst])
        except (KeyError, IndexError, nx.NetworkXError):
            retv = 0

        return retv

    def _remove_all_edges(self):
        self._graph.remove_edges_from(list(self._graph.edges.keys()))

    def _add_edge(self, src: int, neighbor: int, direction: Direction):
        if self[src] and self[neighbor]:
            self._graph.add_edge(src, neighbor, direction=direction)

    def _out_edge_weight(self, target_position: int) -> int:
        """Calculates edge weight based on BoardCell in ``target_position``."""
        target_cell = self[target_position]

        weight = 1
        if target_cell and (
            target_cell.is_wall or target_cell.has_box or target_cell.has_pusher
        ):
            weight = self._MAX_EDGE_WEIGHT

        return weight

    def _reconfigure_edges(self):
        tessellation = BaseTessellation.instance(self.tessellation)

        self._remove_all_edges()
        for src in range(self._vertices_count):
            for direction in tessellation.legal_directions:
                neighbor_position = tessellation.neighbor_position(
                    src, direction, self.board_width, self.board_height
                )
                if neighbor_position >= 0 and neighbor_position != Config.NO_POS:
                    self._add_edge(src, neighbor_position, direction)

    @property
    def _vertices_count(self) -> int:
        return self._graph.number_of_nodes()

    _CurrentReachables = Sequence[int]
    _ToInspectVertices = Sequence[int]
    _ExcludedVertices = Optional[List[int]]
    _AnimationFrameCallback = Callable[
        [int, _CurrentReachables, _ToInspectVertices, _ExcludedVertices], None
    ]

    def _reachables(
        self,
        root: int,
        excluded_positions: Optional[Positions] = None,
        is_obstacle_cb: Optional[Callable[[int], bool]] = None,
        add_animation_frame_cb: Optional[_AnimationFrameCallback] = None,
    ) -> List[int]:
        """
        Calculates all positions reachable from ``root``.

        Args:
            root: initial position for search
            excluded_positions: these positions will be marked as unreachable without
                calculating their status
            is_obstacle_cb: callable that checks if given position on graph is obstacle
            add_animation_frame_cb: if not None, this callable will be called after
                each step of search. Useful for visualization of algorithm and debugging
        """
        excluded: Set[int] = set(excluded_positions) if excluded_positions else set()

        if is_obstacle_cb is None:
            is_obstacle_cb = lambda x: not self[x].can_put_pusher_or_box

        reachables = deque()

        if self[root]:
            visited = self._vertices_count * [False]
            visited[root] = True
            to_inspect = deque([root])

            while len(to_inspect) > 0:
                current_position = to_inspect.popleft()

                if current_position == root or current_position not in excluded:
                    reachables.append(current_position)

                for neighbor in self.all_neighbors(current_position):
                    if not visited[neighbor]:
                        if not is_obstacle_cb(neighbor):
                            to_inspect.append(neighbor)
                        visited[neighbor] = True

                if add_animation_frame_cb is not None:
                    add_animation_frame_cb(
                        current_position, reachables, to_inspect, excluded_positions
                    )

        if root in excluded:
            return [pos for pos in reachables if pos != root]
        else:
            return list(reachables)
