from abc import ABCMeta, abstractmethod
from collections import deque

from ... import tessellation as module_tessellation
from ... import utilities
from .graph_type import GraphType


class BoardGraphBase(metaclass=ABCMeta):
    MAX_EDGE_WEIGHT = len(module_tessellation.Direction) + 1
    KEY_CELL = 'cell'
    KEY_DIRECTION = 'direction'

    @abstractmethod
    def __init__(self, number_of_vertices, graph_type):
        assert graph_type in GraphType

    @abstractmethod
    def __getitem__(self, position):
        """Get :class:`.BoardCell` on ``position``

        Returns:
            BoardCell: reference to :class:`.BoardCell`

        Raises:
            IndexError: if there is no vertex with index ``position``
        """
        pass

    @abstractmethod
    def __setitem__(self, position, board_cell):
        """Set :class:`.BoardCell` on ``position``

        Raises:
            IndexError: if there is no vertex with index ``position``
        """

    @abstractmethod
    def __contains__(self, position):
        """Tests if vertex on ``position`` exists.

        Returns:
            bool: True if vertex exists
        """

    @abstractmethod
    def vertices_count(self):
        """Number of vertices in graph.

        Returns:
            int: number of vertices in graph
        """
        pass

    @abstractmethod
    def edges_count(self):
        """Number of edges in graph.

        Returns:
            int: number of edges in graph
        """
        pass

    @abstractmethod
    def has_edge(self, source_vertex, target_vertex, direction):
        """Tests if edge between ``source_vertex`` and ``dest_vertex`` exists

        Args:
            source_vertex (int): position of source vertex
            dest_vertex (int): position of dest vertex
            direction (Direction): direction from source to dest vertex

        Returns:
            bool: True if edge exists
        """
        pass

    @abstractmethod
    def out_edges_count(self, source_vertex, dest_vertex):
        """Number of out-edges from ``source_vertex`` to ``dest_vertex``

        Args:
            source_vertex (int): position of source vertex
            dest_vertex (int): position of dest vertex

        Returns:
            int: Number of out-edges

        Raises:
            IndexError: if there is no vertex with index of either
                ``source_vertex`` or ``dest_vertex``
        """
        pass

    @abstractmethod
    def reconfigure_edges(self, width, height, tessellation):
        """Recreate all edges using ``tessellation``.

        Args:
            width (int): board width
            height (int): board height
            tessellation (TessellationBase): tessellation instance to use for
                edges calculation
        """
        pass

    def out_edge_weight(self, target_position):
        """Calculates weight of single edge depending on contents of its
        target vertex.

        Args:
            target_position (int): target vertex index

        Raises:
            IndexError: if there is no vertex with index of ``target_position``
        """
        target_cell = self[target_position]

        weight = 1
        if target_cell.is_wall or target_cell.has_box or target_cell.has_pusher:
            weight = self.MAX_EDGE_WEIGHT

        return weight

    @abstractmethod
    def calculate_edge_weights(self):
        """Assigns weights to all edges."""
        pass

    def reachables(
        self, root, excluded_positions=None, is_obstacle_callable=None,
        add_animation_frame_hook=None
    ):
        """Calculates all positions reachable from ``root``.

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
        visited = self.vertices_count() * [False]
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
                    current_position=current_position, reachables=reachables,
                    to_inspect=to_inspect, excluded=excluded_positions
                )

        if root in excluded_positions:
            return [pos for pos in reachables if pos != root]
        else:
            return list(reachables)

    @abstractmethod
    def neighbor(self, from_position, direction):
        """Calculates neighbor vertex index in ``direction``

        Args:
            from_position (int): source vertex index
            direction (Direction): target vertex direction

        Returns:
            int: target vertex index or None

        Raises:
            IndexError: if there is no vertex with index of ``from_position``
        """
        pass

    @abstractmethod
    def wall_neighbors(self, from_position):
        """Calculates indexes of all neighbor wall vertices.

        Args:
            from_position (int): source vertex index

        Returns:
            list: indexes of all neighboring vertices that have wall on them.

        Raises:
            IndexError: if there is no vertex with index of ``from_position``
        """
        pass

    @abstractmethod
    def all_neighbors(self, from_position):
        """Calculates indexes of all neighboring vertices.

        Args:
            from_position (int): source vertex index.

        Returns:
            list: indexes of all neighboring vertices.

        Raises:
            IndexError: if there is no vertex with index of ``from_position``
        """
        pass

    @abstractmethod
    def shortest_path(self, start_position, end_position):
        """Calculates shortest path between two vertices.

        Assumes all vertices having same weight.

        Args:
            start_position (int): source vertex index
            end_position (int): target vertex index

        Returns:
            list: indexes of all vertices in calculated path.

        Raises:
            IndexError: if there is no vertex with index of ``start_position``
        """
        pass

    @abstractmethod
    def dijkstra_path(self, start_position, end_position):
        """Calculates shortest path between two vertices not passing through
        obstacles.

        Uses edge weights to mark obstacles before path calculation.

        Args:
            start_position (int): source vertex index
            end_position (int): target vertex index

        Returns:
            list: indexes of all vertices in calculated path.

        Raises:
            IndexError: if there is no vertex with index of either
                ``start_position`` or ``end_position``
        """
        pass

    @abstractmethod
    def position_path_to_direction_path(self, position_path):
        """Converts path expressed as vertices' indexes to one expressed as
        :class:`.Direction`

        Args:
            position_path (list): list of indexes obrained from either
                :meth:`.shortest_path` or :meth:`.dijkstra_path`.

        Returns:
            dict: describing start vertex index and path consisting of
            :class:`.Direction`::

                {
                    'source_position': 42,
                    'path': [
                        Direction.LEFT, Direction.UP, Direction.RIGHT,
                        Direction.DOWN
                    ]
                }
        """
        pass


class BoardGraphBaseInheritableDocstrings(
    type(BoardGraphBase), utilities.InheritableDocstrings
):
    pass
