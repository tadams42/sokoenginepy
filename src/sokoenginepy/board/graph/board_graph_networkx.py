import networkx as nx

from ..board_cell import BoardCell
from .board_graph_base import (BoardGraphBase,
                               BoardGraphBaseInheritableDocstrings)
from .graph_type import GraphType


class BoardGraphNetworkx(
    BoardGraphBase, metaclass=BoardGraphBaseInheritableDocstrings
):
    """Board graph implementation using NetworkX.

    NetworkX is pure Python graph library, doesn't depend on external binaries
    and is easily installable via pip.

    This is default and fall back graph implementation for sokoenginepy.
    """

    def __init__(self, number_of_vertices, graph_type):
        super().__init__(number_of_vertices, graph_type)

        if graph_type == GraphType.DIRECTED:
            self._graph = nx.DiGraph()
        else:
            self._graph = nx.MultiDiGraph()

        for vertex in range(0, number_of_vertices):
            self._graph.add_node(vertex, cell=BoardCell())

    @copy_ancestor_docstring
    def __getitem__(self, position):
        return self._graph.node[position][self.KEY_CELL]

    @copy_ancestor_docstring
    def __setitem__(self, position, board_cell):
        self._graph.node[position][self.KEY_CELL] = board_cell

    @copy_ancestor_docstring
    def __contains__(self, position):
        return position in self._graph

    @copy_ancestor_docstring
    def vertices_count(self):
        return self._graph.number_of_nodes()

    @copy_ancestor_docstring
    def edges_count(self):
        return self._graph.number_of_edges()

    @copy_ancestor_docstring
    def has_edge(self, source_vertex, target_vertex, direction):
        retv = False

        for out_edge in self._graph.out_edges_iter(source_vertex, data=True):
            # edge: (source, target, data_dict)
            retv = retv or (
                out_edge[1] == target_vertex and
                out_edge[2][self.KEY_DIRECTION] == direction
            )

        return retv

    @copy_ancestor_docstring
    def out_edges_count(self, source_vertex, target_vertex):
        return len(self._graph[source_vertex][target_vertex])

    @copy_ancestor_docstring
    def reconfigure_edges(self, width, height, tessellation):
        self._graph.remove_edges_from(self._graph.edges())
        for source_vertex in self._graph.nodes_iter():
            for direction in tessellation.legal_directions:
                neighbor_vertex = tessellation.neighbor_position(
                    source_vertex, direction, board_width=width,
                    board_height=height
                )
                if neighbor_vertex is not None:
                    self._graph.add_edge(
                        source_vertex, neighbor_vertex, direction=direction
                    )

    @copy_ancestor_docstring
    def calculate_edge_weights(self):
        for edge in self._graph.edges_iter(data=True):
            edge[2]['weight'] = self.out_edge_weight(edge[1])

    @copy_ancestor_docstring
    def neighbor(self, from_position, direction):
        for out_edge in self._graph.out_edges_iter(from_position, data=True):
            # edge: (source, target, data_dict)
            if out_edge[2][self.KEY_DIRECTION] == direction:
                return out_edge[1]
        return None

    @copy_ancestor_docstring
    def wall_neighbors(self, from_position):
        return [
            n for n in self._graph.neighbors_iter(from_position)
            if self[n].is_wall
        ]

    @copy_ancestor_docstring
    def all_neighbors(self, from_position):
        return self._graph.neighbors(from_position)

    @copy_ancestor_docstring
    def shortest_path(self, start_position, end_position):
        try:
            return nx.shortest_path(
                self._graph, start_position, end_position, 1
            )
        except nx.NetworkXNoPath:
            return []

    @copy_ancestor_docstring
    def dijkstra_path(self, start_position, end_position):
        self.calculate_edge_weights()
        try:
            return nx.dijkstra_path(self._graph, start_position, end_position)
        except nx.NetworkXNoPath:
            return []

    @copy_ancestor_docstring
    def position_path_to_direction_path(self, position_path):
        retv = []
        src_vertex_index = 0
        for target_vertex in position_path[1:]:
            src_vertex = position_path[src_vertex_index]
            src_vertex_index += 1

            for out_edge in self._graph.out_edges_iter(src_vertex, data=True):
                if out_edge[1] == target_vertex:
                    retv.append(out_edge[2][self.KEY_DIRECTION])

        return {
            'source_position': position_path[0] if position_path else None,
            'path': retv
        }
