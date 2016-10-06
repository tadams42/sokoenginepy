"""
BoardGraph implementation using NetworkX which is slower but is pure Python,
doesn't depend on external binaries and is easily installable via pip

This is default and fall back implementation used in sokoenginepy.
"""

import networkx as nx

from ...board import BoardCell
from .board_graph_base import BoardGraphBase, GraphType


class BoardGraphNetworkx(BoardGraphBase):

    def __init__(self, number_of_vertices, graph_type):
        super().__init__(number_of_vertices, graph_type)

        if graph_type == GraphType.DIRECTED:
            self._graph = nx.DiGraph()
        else:
            self._graph = nx.MultiDiGraph()

        for vertice in range(0, number_of_vertices):
            self._graph.add_node(vertice, cell=BoardCell())

    def __getitem__(self, position):
        return self._graph.node[position]['cell']

    def __setitem__(self, position, board_cell):
        self._graph.node[position]['cell'] = board_cell

    def __contains__(self, position):
        return position in self._graph

    def vertices_count(self):
        return self._graph.number_of_nodes()

    def edges_count(self):
        return self._graph.number_of_edges()

    def has_edge(self, source_vertice, target_vertice, direction):
        """
        Checks if there is edge between source_vertice and target_vertice in
        given
        direction
        """
        retv = False

        for out_edge in self._graph.out_edges_iter(source_vertice, data=True):
            # edge: (source, target, data_dict)
            retv = retv or (
                out_edge[1] == target_vertice and
                out_edge[2]['direction'] == direction
            )

        return retv

    def out_edges_count(self, source_vertice, target_vertice):
        return len(self._graph[source_vertice][target_vertice])

    def reconfigure_edges(self, width, height, tessellation):
        """
        Uses tessellation object to create all edges in graph.
        """
        self._graph.remove_edges_from(self._graph.edges())
        for source_vertice in self._graph.nodes_iter():
            for direction in tessellation.legal_directions:
                neighbor_vertice = tessellation.neighbor_position(
                    source_vertice,
                    direction,
                    board_width=width,
                    board_height=height
                )
                if neighbor_vertice is not None:
                    self._graph.add_edge(
                        source_vertice, neighbor_vertice, direction=direction
                    )

    def calculate_edge_weights(self):
        """
        Calculates and sets weights to all edges in board graph.
        """
        for edge in self._graph.edges_iter(data=True):
            edge[2]['weight'] = self.out_edge_weight(edge[1])

    def neighbor(self, from_position, direction):
        for out_edge in self._graph.out_edges_iter(from_position, data=True):
            # edge: (source, target, data_dict)
            if out_edge[2]['direction'] == direction:
                return out_edge[1]
        return None

    def wall_neighbors(self, from_position):
        return [
            n for n in self._graph.neighbors_iter(from_position)
            if self[n].is_wall
        ]

    def all_neighbors(self, from_position):
        return self._graph.neighbors(from_position)

    def shortest_path(self, start_position, end_position):
        try:
            return nx.shortest_path(
                self._graph, start_position, end_position, 1
            )
        except nx.NetworkXNoPath:
            return []

    def dijkstra_path(self, start_position, end_position):
        self.calculate_edge_weights()
        try:
            return nx.dijkstra_path(self._graph, start_position, end_position)
        except nx.NetworkXNoPath:
            return []

    def position_path_to_direction_path(self, position_path):
        retv = []
        src_vertice_index = 0
        for target_vertice in position_path[1:]:
            src_vertice = position_path[src_vertice_index]
            src_vertice_index += 1

            for out_edge in self._graph.out_edges_iter(src_vertice, data=True):
                if out_edge[1] == target_vertice:
                    retv.append(out_edge[2]['direction'])

        return {
            'source_position': position_path[0] if position_path else None,
            'path': retv
        }
