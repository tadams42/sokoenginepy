from collections import deque
from enum import IntEnum

import networkx as nx


class GraphType(IntEnum):
    DIRECTED = 0
    DIRECTED_MULTI = 1


class BoardGraph:
    """
    Board graph implementation using NetworkX.

    NetworkX is pure Python graph library, doesn't depend on external binaries
    and is easily installable via pip.

    This is default and fall back graph implementation for sokoenginepy.
    """

    _KEY_CELL = 'cell'
    _KEY_DIRECTION = 'direction'
    _MAX_EDGE_WEIGHT = 100  # must be > len(Direction)

    def __init__(self, board_width, board_height, graph_type):
        from ..board import BoardCell

        self._board_width = board_width
        self._board_height = board_height

        if graph_type == GraphType.DIRECTED:
            self._graph = nx.DiGraph()
        else:
            self._graph = nx.MultiDiGraph()

        for vertex in range(0, self.board_width * self.board_height):
            self._graph.add_node(vertex, **{self._KEY_CELL: BoardCell()})

    @property
    def board_width(self):
        return self._board_width

    @property
    def board_height(self):
        return self._board_height

    def __getitem__(self, position):
        """Get :class:`.BoardCell` on ``position``

        Returns:
            BoardCell: reference to :class:`.BoardCell`

        Raises:
            IndexError: if there is no vertex with index ``position``
        """
        try:
            return self._graph.node[position][self._KEY_CELL]
        except KeyError as e:
            raise IndexError(str(e))
        except nx.NetworkXError as e:
            raise IndexError(str(e))

    def __setitem__(self, position, board_cell):
        """Set :class:`.BoardCell` on ``position``

        Raises:
            IndexError: if there is no vertex with index ``position``
        """
        try:
            self._graph.node[position][self._KEY_CELL] = board_cell
        except KeyError as e:
            raise IndexError(str(e))
        except nx.NetworkXError as e:
            raise IndexError(str(e))

    def __contains__(self, position):
        """Tests if vertex on ``position`` exists.

        Returns:
            bool: True if vertex exists
        """
        return position in self._graph

    @property
    def vertices_count(self):
        """Number of vertices in graph.

        Returns:
            int: number of vertices in graph
        """
        return self._graph.number_of_nodes()

    @property
    def edges_count(self):
        """Number of edges in graph.

        Returns:
            int: number of edges in graph
        """
        return self._graph.number_of_edges()

    def has_edge(self, source_vertex, target_vertex, direction):
        """
        Tests if edge between ``source_vertex`` and ``dest_vertex`` exists.

        Args:
            source_vertex (int): position of source vertex
            dest_vertex (int): position of dest vertex
            direction (Direction): direction from source to dest vertex

        Returns:
            bool: True if edge exists. False if edge doesn't exist or one or
                  both verrtices are off board.
        """
        retv = False
        for out_edge in self.out_edges(source_vertex):
            retv = retv or (
                out_edge[1] == target_vertex
                and out_edge[2][self._KEY_DIRECTION] == direction
            )
            if retv:
                break

        return retv

    def out_edges(self, source_vertex):
        try:
            retv = tuple(
                # edge: (source, target, data_dict)
                # out_edge[2][self._KEY_DIRECTION]
                out_edge
                for out_edge in
                self._graph.out_edges_iter(source_vertex, data=True)
            )
        except nx.NetworkXError:
            retv = tuple()

        return retv

    def out_edges_count(self, source_vertex, target_vertex):
        """
        Number of out-edges from ``source_vertex`` to ``dest_vertex``

        Args:
            source_vertex (int): position of source vertex
            dest_vertex (int): position of dest vertex

        Returns:
            int: Number of out-edges
        """
        try:
            retv = len(self._graph[source_vertex][target_vertex])
        except KeyError:
            retv = 0

        return retv

    def remove_all_edges(self):
        self._graph.remove_edges_from(self._graph.edges())

    def add_edge(self, source_vertex, neighbor_vertex, direction):
        if source_vertex not in self or neighbor_vertex not in self:
            raise IndexError("Board index out of range!")

        self._graph.add_edge(
            source_vertex, neighbor_vertex, direction=direction
        )

    def out_edge_weight(self, target_position):
        """
        Calculates weight of single edge depending on contents of its
        target vertex.

        Args:
            target_position (int): target vertex index

        Raises:
            IndexError: if ``target_position`` is off board.
        """
        target_cell = self[target_position]

        weight = 1
        if target_cell and (
            target_cell.is_wall or target_cell.has_box
            or target_cell.has_pusher
        ):
            weight = self._MAX_EDGE_WEIGHT

        return weight

    def _reachables(
        self,
        root,
        excluded_positions=None,
        is_obstacle_callable=None,
        add_animation_frame_hook=None
    ):
        """
        Calculates all positions reachable from ``root``.

        Args:
            root (int): initial position for search
            excluded_positions (list): these positions will be marked as
               unreachable without calculating their status
            is_obstacle_callable (bool): callable that checks if given position
                on graph is obstacle
            add_animation_frame_hook (callable): if not None, this callable will
                be called after each step of search. Useful for visualization of
                algorithm and debugging

        Returns:
            list: board positions reachable from ``root``

        Raises:
            IndexError: if there is no vertex with index of ``root``
        """
        if root not in self:
            raise IndexError('Starting position is off board!')

        visited = self.vertices_count * [False]
        visited[root] = True
        reachables = deque()
        to_inspect = deque([root])
        if not excluded_positions:
            excluded_positions = []

        if is_obstacle_callable is None:
            is_obstacle_callable = lambda x: not self[x].can_put_pusher_or_box

        while len(to_inspect) > 0:
            current_position = to_inspect.popleft()

            if (current_position == root or
                    current_position not in excluded_positions):
                reachables.append(current_position)

            for neighbor in self.all_neighbors(current_position):
                if not visited[neighbor]:
                    if not is_obstacle_callable(neighbor):
                        to_inspect.append(neighbor)
                    visited[neighbor] = True

            if add_animation_frame_hook is not None:
                add_animation_frame_hook(
                    current_position=current_position,
                    reachables=reachables,
                    to_inspect=to_inspect,
                    excluded=excluded_positions
                )

        if root in excluded_positions:
            return [pos for pos in reachables if pos != root]
        else:
            return list(reachables)

    def neighbor(self, from_position, direction):
        """
        Calculates neighbor vertex index in ``direction``

        Args:
            from_position (int): source vertex index
            direction (Direction): target vertex direction

        Returns:
            int: target vertex index or None

        Raises:
            IndexError: if there is no vertex with index of ``from_position``
        """
        try:
            for out_edge in self._graph.out_edges_iter(
                from_position, data=True
            ):
                # edge: (source, target, data_dict)
                if out_edge[2][self._KEY_DIRECTION] == direction:
                    return out_edge[1]
        except nx.NetworkXError as e:
            raise IndexError(str(e))

        return None

    def wall_neighbors(self, from_position):
        """
        Calculates indexes of all neighbor wall vertices.

        Args:
            from_position (int): source vertex index

        Returns:
            list: indexes of all neighboring vertices that have wall on them.

        Raises:
            IndexError: if there is no vertex with index of ``from_position``
        """
        try:
            return [
                n for n in self._graph.neighbors_iter(from_position)
                if self[n].is_wall
            ]
        except nx.NetworkXError as e:
            raise IndexError(str(e))

    def all_neighbors(self, from_position):
        """
        Calculates indexes of all neighboring vertices.

        Args:
            from_position (int): source vertex index.

        Returns:
            list: indexes of all neighboring vertices.

        Raises:
            IndexError: if there is no vertex with index of ``from_position``
        """
        try:
            return self._graph.neighbors(from_position)
        except nx.NetworkXError as e:
            raise IndexError(str(e))

    def shortest_path(self, start_position, end_position):
        """
        Calculates shortest path between two vertices with all vertices having
        equal weight.

        Args:
            start_position (int): source vertex index
            end_position (int): target vertex index

        Returns:
            list: indexes of all vertices in calculated path.

        Raises:
            IndexError: if any of indexes are off board
        """
        if start_position not in self or end_position not in self:
            raise IndexError('Board index out of range!')

        for edge in self._graph.edges_iter(data=True):
            edge[2]['weight'] = 1

        try:
            return nx.shortest_path(
                self._graph, start_position, end_position, 1
            )
        except nx.NetworkXNoPath:
            return []

    def dijkstra_path(self, start_position, end_position):
        """
        Calculates shortest path between two vertices not passing through
        obstacles.

        Args:
            start_position (int): source vertex index
            end_position (int): target vertex index

        Returns:
            list: indexes of all vertices in calculated path.

        Raises:
            IndexError: if any of indexes are off board
        """
        if start_position not in self or end_position not in self:
            raise IndexError('Board index out of range!')

        for edge in self._graph.edges_iter(data=True):
            edge[2]['weight'] = self.out_edge_weight(edge[1])

        try:
            return nx.dijkstra_path(self._graph, start_position, end_position)
        except nx.NetworkXNoPath:
            return []

    def find_jump_path(self, start_position, end_position):
        """
        Returns:
            list: of positions through which pusher must pass when jumping

        Raises:
            IndexError: if any of indexes are off board
        """
        return self.shortest_path(start_position, end_position)

    def find_move_path(self, start_position, end_position):
        """
        Returns:
            list: of positions through which pusher must pass when moving
            without pushing boxes

        Raises:
            IndexError: if any of indexes are off board
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

    def positions_path_to_directions_path(self, positions_path):
        """
        Converts path expressed as vertices' indexes to one expressed as
        :class:`.Direction`

        Args:
            positions_path (list): list of integer positions

        Returns:
            list: of :class:`.Direction` instances
        """
        src_vertex_index = 0

        if positions_path and positions_path[src_vertex_index] not in self:
            raise IndexError('Board index out of range!')

        retv = []

        for target_vertex in positions_path[1:]:
            src_vertex = positions_path[src_vertex_index]
            src_vertex_index += 1

            if src_vertex not in self or target_vertex not in self:
                raise IndexError('Board index out of range!')

            for out_edge in self._graph.out_edges_iter(src_vertex, data=True):
                if out_edge[1] == target_vertex:
                    retv.append(out_edge[2][self._KEY_DIRECTION])

        return retv

    def mark_play_area(self):
        """
        Marks all vertices (BoardCells) that are playable (reachable by any box
        or pusher).
        """
        piece_positions = []
        for vertex in range(0, self.vertices_count):
            if self[vertex].has_box or self[vertex].has_pusher:
                self[vertex].is_in_playable_area = True
                piece_positions.append(vertex)
            else:
                self[vertex].is_in_playable_area = False

        def is_obstacle(vertex):
            return self[vertex].is_wall

        for piece_position in piece_positions:
            reachables = self._reachables(
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

        return self._reachables(
            root=pusher_position,
            is_obstacle_callable=is_obstacle,
            excluded_positions=excluded_positions
        )

    def normalized_pusher_position(
        self, pusher_position, excluded_positions=None
    ):
        """
        Returns:
            int: Top-left position reachable by pusher
        """
        reachables = self.positions_reachable_by_pusher(
            pusher_position=pusher_position,
            excluded_positions=excluded_positions
        )
        if reachables:
            return min(reachables)
        else:
            return pusher_position

    def path_destination(self, start_position, directions_path):
        if start_position not in self:
            raise IndexError('Board index out of range')

        retv = start_position
        for direction in directions_path:
            next_target = self.neighbor(retv, direction)
            if next_target:
                retv = next_target
            else:
                break
        return retv

    def reconfigure_edges(self, tessellation):
        """Recreate all edges using ``tessellation``.

        Args:
            width (int): board width
            height (int): board height
            tessellation (TessellationBase): tessellation instance to use for
                edges calculation
        """
        self.remove_all_edges()
        for source_vertex in range(self.vertices_count):
            for direction in tessellation.legal_directions:
                neighbor_vertex = tessellation.neighbor_position(
                    source_vertex, direction, self.board_width,
                    self.board_height
                )
                if neighbor_vertex is not None:
                    self.add_edge(
                        source_vertex, neighbor_vertex, direction
                    )
