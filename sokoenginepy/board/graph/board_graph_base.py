from abc import ABC, abstractmethod
from collections import deque
from enum import IntEnum

from ... import tessellation as module_tessellation


class GraphType(IntEnum):
    DIRECTED = 0
    DIRECTED_MULTI = 1


class BoardGraphBase(ABC):
    MAX_EDGE_WEIGHT = len(module_tessellation.Direction) + 1
    KEY_CELL = 'cell'
    KEY_DIRECTION = 'direction'

    @abstractmethod
    def __init__(self, number_of_vertices, graph_type):
        assert graph_type in GraphType

    @abstractmethod
    def __getitem__(self, position):
        pass

    @abstractmethod
    def __setitem__(self, position, board_cell):
        pass

    @abstractmethod
    def __contains__(self, position):
        pass

    @abstractmethod
    def vertices_count(self):
        pass

    @abstractmethod
    def edges_count(self):
        pass

    @abstractmethod
    def has_edge(self, source_vertex, target_vertex, direction):
        pass

    @abstractmethod
    def out_edges_count(self, source_vertex, dest_vertex):
        pass

    @abstractmethod
    def reconfigure_edges(self, width, height, tessellation):
        pass

    def out_edge_weight(self, target_position):
        """
        Calculates weight of single edge depending on contents of its vertices.
        """
        target_cell = self[target_position]

        weight = 1
        if target_cell.is_wall or target_cell.has_box or target_cell.has_pusher:
            weight = self.MAX_EDGE_WEIGHT

        return weight

    @abstractmethod
    def calculate_edge_weights(self):
        pass

    def reachables(
        self, root, excluded_positions=None, is_obstacle_callable=None,
        add_animation_frame_hook=None
    ):
        """
        Returns list of all positions reachable from root

        excluded_positions - these positions will be marked as unreachable
            without calculating their status
        is_obstacle_callable - callable that checks if given position on graph
            is obstacle
        add_animation_frame_hook - if not None, this callable will be called
            after each step oof search. Useful for visualization of algorithm
            and debugging
        """
        visited = self.vertices_count() * [False]
        visited[root] = True
        reachables = deque()
        to_inspect = deque([root])
        if not excluded_positions:
            excluded_positions = []

        if is_obstacle_callable is None:
            is_obstacle_callable = (lambda x: not self[x].can_put_pusher_or_box)

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

    @abstractmethod
    def neighbor(self, from_position, direction):
        pass

    @abstractmethod
    def wall_neighbors(self, from_position):
        pass

    @abstractmethod
    def all_neighbors(self, from_position):
        pass

    @abstractmethod
    def shortest_path(self, start_position, end_position):
        pass

    @abstractmethod
    def dijkstra_path(self, start_position, end_position):
        pass

    @abstractmethod
    def position_path_to_direction_path(self, position_path):
        pass
