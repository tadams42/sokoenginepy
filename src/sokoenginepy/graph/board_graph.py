from collections import deque
from enum import IntEnum
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union

import networkx as nx

# (1, 0, {'direction': Direction.LEFT})
Edge = Tuple[int, int, Dict]


class GraphType(IntEnum):
    DIRECTED = 0
    DIRECTED_MULTI = 1


class EngineConfig(IntEnum):
    MAX_BOARD_WIDTH = 4096
    MAX_BOARD_HEIGHT = 4096


class BoardGraph:
    """Board graph implementation using NetworkX."""

    _KEY_CELL = "cell"
    _KEY_DIRECTION = "direction"
    _MAX_EDGE_WEIGHT = 100  # must be > len(Direction)

    def __init__(self, board_width: int, board_height: int, graph_type: "GraphType"):
        from ..board import BoardCell

        if (
            board_width < 0
            or board_height < 0
            or board_width > EngineConfig.MAX_BOARD_WIDTH
            or board_height > EngineConfig.MAX_BOARD_HEIGHT
        ):
            raise ValueError(
                "Board width and height must be >= 0 and <= MAX_BOARD_WIDTH, "
                "MAX_BOARD_HEIGHT`!"
            )

        self._board_width = board_width
        self._board_height = board_height

        if graph_type == GraphType.DIRECTED:
            self._graph = nx.DiGraph()
        elif graph_type == GraphType.DIRECTED_MULTI:
            self._graph = nx.MultiDiGraph()
        else:
            raise ValueError("Unknown graph_type: {}!".format(graph_type))

        for position in range(0, self.board_width * self.board_height):
            self._graph.add_node(position, **{self._KEY_CELL: BoardCell()})

    @property
    def board_width(self) -> int:
        return self._board_width

    @property
    def board_height(self) -> int:
        return self._board_height

    def __getitem__(self, position: int) -> "BoardCell":
        try:
            return self._graph.nodes[position][self._KEY_CELL]

        except KeyError as e:
            if isinstance(position, int) and position >= 0:
                raise IndexError from e
            else:
                raise

    def __setitem__(self, position: int, board_cell: Union["BoardCell", str]):
        from ..board import BoardCell

        try:
            self._graph.nodes[position][self._KEY_CELL] = BoardCell(board_cell)

        except KeyError as e:
            if isinstance(position, int) and position >= 0:
                raise IndexError from e
            else:
                raise

    def __contains__(self, position: int) -> bool:
        return position in self._graph

    @property
    def vertices_count(self) -> int:
        return self._graph.number_of_nodes()

    @property
    def edges_count(self) -> bool:
        return self._graph.number_of_edges()

    def has_edge(
        self, source_position: int, target_position: int, direction: "Direction"
    ) -> bool:
        retv = False
        try:
            if source_position is not None:
                for out_edge in self._graph.edges(source_position, data=True):
                    retv = retv or (
                        out_edge[1] == target_position
                        and out_edge[2][self._KEY_DIRECTION] == direction
                    )
                    if retv:
                        break

        except (KeyError, IndexError, nx.NetworkXError):
            pass

        return retv

    def out_edges_count(self, source_position: int, target_position: int) -> int:
        """
        Number of out-edges from ``source_position`` to ``dest_position``

        Returns:
            Zero when no out edges exist or or any of positions is illegal type or out
            of bound board index.
        """
        try:
            retv = len(self._graph[source_position][target_position])
        except (KeyError, IndexError, nx.NetworkXError):
            retv = 0

        return retv

    def remove_all_edges(self):
        self._graph.remove_edges_from(list(self._graph.edges.keys()))

    def add_edge(
        self, source_position: int, neighbor_position: int, direction: "Direction"
    ):
        """
        Adds edges between to existing positions.

        Raises:
            IndexError: ``source_position`` or ``neighbor_position`` off board
            KeyError: ``source_position`` or ``neighbor_position`` illegal values
        """
        if self[source_position] and self[neighbor_position]:
            self._graph.add_edge(
                source_position, neighbor_position, direction=direction
            )

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

    def neighbor(self, from_position: int, direction: "Direction") -> int:
        """
        Calculates neighbor position in ``direction``

        Returns:
            int: target position or None

        Raises:
            IndexError: ``from_position`` off board
            KeyError: ``from_position`` illegal values
        """
        if self[from_position]:
            for out_edge in self._graph.edges(from_position, data=True):
                if out_edge[2][self._KEY_DIRECTION] == direction:
                    return out_edge[1]

        return None

    def wall_neighbors(self, from_position: int) -> List[int]:
        """
        Gets a list of all neighboring walls.

        Raises:
            IndexError: ``from_position`` off board
            KeyError: ``from_position`` illegal values
        """
        if self[from_position]:
            return [n for n in self._graph.neighbors(from_position) if self[n].is_wall]

        return []

    def all_neighbors(self, from_position: int) -> List[int]:
        """
        Gets a list of all neighbors.

        Raises:
            IndexError: ``from_position`` off board
            KeyError: ``from_position`` illegal values
        """

        if self[from_position]:
            return list(self._graph.neighbors(from_position))

        return []

    def shortest_path(self, start_position: int, end_position: int) -> List[int]:
        """
        Calculates shortest path between two positions with all positions having equal
        weight.

        Raises:
            IndexError: ``start_position`` or ``end_position`` off board
            KeyError: ``start_position`` or ``end_position`` illegal values
        """

        if self[start_position] and self[end_position]:
            for edge in self._graph.edges(data=True):
                edge[2]["weight"] = 1

            try:
                return nx.shortest_path(self._graph, start_position, end_position, 1)
            except nx.NetworkXNoPath:
                return []

        return []

    def dijkstra_path(self, start_position: int, end_position: int) -> List[int]:
        """
        Calculates shortest path between two positions not passing through board
        obstacles (walls, other pushers, etc...).

        Raises:
            IndexError: ``start_position`` or ``end_position`` off board
            KeyError: ``start_position`` or ``end_position`` illegal values
        """
        if self[start_position] and self[end_position]:
            for edge in self._graph.edges(data=True):
                edge[2]["weight"] = self.out_edge_weight(edge[1])

            try:
                return nx.dijkstra_path(self._graph, start_position, end_position)
            except nx.NetworkXNoPath:
                return []

        return []

    def find_jump_path(self, start_position: int, end_position: int) -> List[int]:
        """
        Returns:
            List of positions through which pusher must pass when jumping

        Raises:
            IndexError: ``start_position`` or ``end_position`` off board
            KeyError: ``start_position`` or ``end_position`` illegal values
        """
        return self.shortest_path(start_position, end_position)

    def find_move_path(self, start_position: int, end_position: int) -> List[int]:
        """
        Returns:
            List of positions through which pusher must pass when moving without
            pushing boxes

        Raises:
            IndexError: ``start_position`` or ``end_position`` off board
            KeyError: ``start_position`` or ``end_position`` illegal values
        """
        path = self.dijkstra_path(start_position, end_position)

        retv = path[:1]
        for position in path[1:]:
            if self[position].can_put_pusher_or_box:
                retv.append(position)
            else:
                break
        if retv != path:
            return []
        return path

    def positions_path_to_directions_path(
        self, positions_path: Sequence[int]
    ) -> List["Direction"]:
        """
        Converts path expressed as positions to one expressed as :class:`.Direction`.

        Raises:
            IndexError: Any of positions in ``positions_path`` off board
            KeyError: Any of positions in ``positions_path`` are illegal values
        """

        if positions_path:
            self[positions_path[0]]
        else:
            return []

        retv = []

        src_position_index = 0
        for target_position in positions_path[1:]:
            src_position = positions_path[src_position_index]
            src_position_index += 1

            if self[src_position] and self[target_position]:
                for out_edge in self._graph.edges(src_position, data=True):
                    if out_edge[1] == target_position:
                        retv.append(out_edge[2][self._KEY_DIRECTION])

        return retv

    def mark_play_area(self):
        """
        Marks all positions (BoardCells) that are playable (reachable by any box or
        pusher).
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
        self, pusher_position: int, excluded_positions: Optional[Sequence[int]] = None
    ) -> List[int]:
        """
        Returns:
            List of positions that are reachable by pusher standing on ``position``
        """
        return self._reachables(
            root=pusher_position,
            is_obstacle_cb=lambda x: not self[x].can_put_pusher_or_box,
            excluded_positions=excluded_positions,
        )

    def normalized_pusher_position(
        self, pusher_position: int, excluded_positions: Optional[Sequence[int]] = None
    ) -> int:
        """
        Returns:
            Top-left position reachable by pusher
        """
        reachables = self.positions_reachable_by_pusher(
            pusher_position=pusher_position, excluded_positions=excluded_positions
        )
        if reachables:
            return min(reachables)
        else:
            return pusher_position

    def path_destination(
        self, start_position: int, directions_path: Sequence["Direction"]
    ) -> int:
        if not directions_path:
            self[start_position]

        retv = start_position
        for direction in directions_path:
            next_target = self.neighbor(retv, direction)
            if next_target:
                retv = next_target
            else:
                break
        return retv

    def reconfigure_edges(self, tessellation: "Tessellation"):
        """Recreate all edges using ``tessellation``."""
        self.remove_all_edges()
        for source_position in range(self.vertices_count):
            for direction in tessellation.legal_directions:
                neighbor_position = tessellation.neighbor_position(
                    source_position, direction, self.board_width, self.board_height
                )
                if neighbor_position is not None:
                    self.add_edge(source_position, neighbor_position, direction)

    _CurrentReachables = Sequence[int]
    _ToInspectVertices = Sequence[int]
    _ExcludedVertices = Optional[Sequence[int]]
    _AnimationFrameCallback = Callable[
        [int, _CurrentReachables, _ToInspectVertices, _ExcludedVertices], None
    ]

    def _reachables(
        self,
        root: int,
        excluded_positions: Optional[Sequence[int]] = None,
        is_obstacle_cb: Callable[[int], bool] = None,
        add_animation_frame_cb: _AnimationFrameCallback = None,
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
        excluded_positions = (
            set(excluded_positions) if excluded_positions is not None else set()
        )

        if is_obstacle_cb is None:
            is_obstacle_cb = lambda x: not self[x].can_put_pusher_or_box

        reachables = deque()

        if self[root]:
            visited = self.vertices_count * [False]
            visited[root] = True
            to_inspect = deque([root])

            while len(to_inspect) > 0:
                current_position = to_inspect.popleft()

                if (
                    current_position == root
                    or current_position not in excluded_positions
                ):
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

        if root in excluded_positions:
            return [pos for pos in reachables if pos != root]
        else:
            return list(reachables)
