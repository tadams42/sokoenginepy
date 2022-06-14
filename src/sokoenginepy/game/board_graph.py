from __future__ import annotations

from collections import deque
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple, Union

import networkx as nx

from ..io import Puzzle
from .base_tessellation import BaseTessellation, Tessellation
from .board_cell import BoardCell
from .config import Config, Direction, GraphType

# (1, 0, {'direction': Direction.LEFT})
Edge = Tuple[int, int, Dict[str, Union[Direction, int]]]
BoardCellOrStr = Union[BoardCell, str]
Positions = List[int]
Directions = List[Direction]


class BoardGraph:
    """
    Board graph.

    Depending on how ``sokoenginepy`` was installed, it is using either ``NetworkX`` or
    ``Boost.Graph`` under the hood.
    """

    _KEY_CELL = "cell"
    _KEY_DIRECTION = "direction"
    _MAX_EDGE_WEIGHT = 100  # must be > len(Direction)

    def __init__(self, puzzle: Puzzle):
        if puzzle.width > Config.MAX_HEIGHT or puzzle.height > Config.MAX_WIDTH:
            raise ValueError(
                "Board width and height must be >= 0 and <= MAX_BOARD_WIDTH, "
                "MAX_BOARD_HEIGHT`!"
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
        self.reconfigure_edges()

    def __getitem__(self, position: int) -> BoardCell:
        try:
            return self._graph.nodes[position][self._KEY_CELL]

        except KeyError as e:
            if isinstance(position, int) and position >= 0:
                raise IndexError from e
            else:
                raise

    def __setitem__(self, position: int, board_cell: BoardCellOrStr):
        try:
            if isinstance(board_cell, BoardCell):
                self._graph.nodes[position][self._KEY_CELL] = board_cell
            else:
                self._graph.nodes[position][self._KEY_CELL] = BoardCell(board_cell)

        except KeyError as e:
            if isinstance(position, int) and position >= 0:
                raise IndexError from e
            else:
                raise

    def __contains__(self, position: int) -> bool:
        return position in self._graph

    @property
    def tessellation(self) -> Tessellation:
        return self._tessellation

    def to_board_str(self, use_visible_floor=False, rle_encode=False) -> str:
        puzzle = Puzzle.instance_from(
            self._tessellation, self._board_width, self._board_height
        )

        for pos in range(self.vertices_count):
            puzzle[pos] = self[pos].to_str()

        return puzzle.to_board_str(use_visible_floor, rle_encode)

    def __str__(self) -> str:
        return self.to_board_str(True)

    @property
    def vertices_count(self) -> int:
        return self._graph.number_of_nodes()

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

    def has_edge(self, src: int, dst: int, direction: Direction) -> bool:
        retv = False
        out_edge: Edge
        try:
            if src is not None:
                for out_edge in self._graph.edges(src, data=True):
                    retv = retv or (
                        out_edge[1] == dst
                        and out_edge[2][self._KEY_DIRECTION] == direction
                    )
                    if retv:
                        break

        except (KeyError, IndexError, nx.NetworkXError):
            pass

        return retv

    def out_edges_count(self, src: int, dst: int) -> int:
        """
        Number of out-edges from ``src`` to ``dst``.

        Returns:
            Zero when no out edges exist or or any of positions is illegal type or out
            of bound board index.
        """
        try:
            # retv = self._graph.number_of_edges(src, dst)
            retv = len(self._graph[src][dst])
        except (KeyError, IndexError, nx.NetworkXError):
            retv = 0

        return retv

    def remove_all_edges(self):
        self._graph.remove_edges_from(list(self._graph.edges.keys()))

    def add_edge(self, src: int, neighbor: int, direction: Direction):
        """
        Adds edges between to existing positions.

        Raises:
            IndexError: ``src`` or ``neighbor`` off board
            KeyError: ``src`` or ``neighbor`` illegal values
        """
        if self[src] and self[neighbor]:
            self._graph.add_edge(src, neighbor, direction=direction)

    def out_edge_weight(self, target_position: int) -> int:
        """
        Calculates edge weight based on BoardCell on ``target_position``.

        Raises:
            IndexError: ``target_position`` off board
            KeyError: ``target_position`` illegal values
        """
        target_cell = self[target_position]

        weight = 1
        if target_cell and (
            target_cell.is_wall or target_cell.has_box or target_cell.has_pusher
        ):
            weight = self._MAX_EDGE_WEIGHT

        return weight

    def neighbor(self, src: int, direction: Direction) -> Optional[int]:
        """
        Calculates neighbor position in ``direction``.

        Returns:
            Target position or `None`.

        Raises:
            IndexError: ``src`` off board
            KeyError: ``src`` illegal values
        """
        out_edge: Edge
        if self[src]:
            for out_edge in self._graph.edges(src, data=True):
                if out_edge[2][self._KEY_DIRECTION] == direction:
                    return out_edge[1]

        return None

    def wall_neighbors(self, src: int) -> Positions:
        """
        Gets a list of all neighboring walls.

        Raises:
            IndexError: ``src`` off board
            KeyError: ``src`` illegal values
        """
        if self[src]:
            return [n for n in self._graph.neighbors(src) if self[n].is_wall]

        return []

    def all_neighbors(self, src: int) -> Positions:
        """
        Gets a list of all neighbors.

        Raises:
            IndexError: ``src`` off board
            KeyError: ``src`` illegal values
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
            KeyError: ``src`` or ``dst`` illegal values
        """

        if self[src] and self[dst]:
            edge: Edge
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
        obstacles (walls, other pushers, etc...).

        Raises:
            IndexError: ``src`` or ``dst`` off board
            KeyError: ``src`` or ``dst`` illegal values
        """
        if self[src] and self[dst]:
            edge: Edge
            for edge in self._graph.edges(data=True):
                edge[2]["weight"] = self.out_edge_weight(edge[1])

            try:
                return nx.dijkstra_path(self._graph, src, dst)
            except nx.NetworkXNoPath:
                return []

        return []

    def find_jump_path(self, src: int, dst: int) -> Positions:
        """
        Returns:
            List of positions through which pusher must pass when jumping

        Raises:
            IndexError: ``src`` or ``dst`` off board
            KeyError: ``src`` or ``dst`` illegal values
        """
        return self.shortest_path(src, dst)

    def find_move_path(self, src: int, dst: int) -> Positions:
        """
        Returns:
            List of positions through which pusher must pass when moving without
            pushing boxes

        Raises:
            IndexError: ``src`` or ``dst`` off board
            KeyError: ``src`` or ``dst`` illegal values
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
            KeyError: Any of positions in ``positions`` are illegal values
        """

        if positions:
            self[positions[0]]
        else:
            return []

        retv = []

        src_position_index = 0
        out_edge: Edge
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
        for position in range(0, self.vertices_count):
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
        Returns:
            List of positions that are reachable by pusher standing on
            ``pusher_position``.
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
        Returns:
            Top-left position reachable by pusher.
        """
        reachables = self.positions_reachable_by_pusher(
            pusher_position=pusher_position, excluded_positions=excluded_positions
        )
        if reachables:
            return min(reachables)
        else:
            return pusher_position

    def path_destination(self, src: int, directions: Directions) -> int:
        if not directions:
            self[src]

        retv = src
        for direction in directions:
            next_target = self.neighbor(retv, direction)
            if next_target:
                retv = next_target
            else:
                break
        return retv

    def reconfigure_edges(self):
        tessellation = BaseTessellation.instance(self.tessellation)

        self.remove_all_edges()
        for src in range(self.vertices_count):
            for direction in tessellation.legal_directions:
                neighbor_position = tessellation.neighbor_position(
                    src, direction, self.board_width, self.board_height
                )
                if neighbor_position is not None:
                    self.add_edge(src, neighbor_position, direction)

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
            visited = self.vertices_count * [False]
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
