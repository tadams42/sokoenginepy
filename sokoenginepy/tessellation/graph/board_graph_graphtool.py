"""
BoardGraph implementation using graph-tool.
graph-tool is blazingly fast graph library but it depends on number of external
binaries, it is not normally installable via pip and thus not readily available
for easy and painless installation.

If graph-tool is detected as installed, this implementation is used. If not,
NetworkX implementation is used
"""

# import graph_tool.all as gt
from graph_tool import Graph
from graph_tool.topology import shortest_path

from ...board import BoardCell
from .board_graph_base import BoardGraphBase, GraphType


class BoardGraphGraphtool(BoardGraphBase):

    def __init__(self, number_of_vertices, graph_type):
        super().__init__(number_of_vertices, graph_type)
        # Graph tool creates directed multigraph by default.
        self._graph = Graph()
        self._graph.add_vertex(number_of_vertices)
        self._graph.vertex_properties["cell"] = self._graph.new_vertex_property(
            "object", number_of_vertices * [BoardCell()]
        )
        self._graph.edge_properties["direction"
                                   ] = self._graph.new_edge_property("object")
        self._graph.edge_properties["weight"
                                   ] = self._graph.new_edge_property("int")

    def __getitem__(self, position):
        return self._graph.vp.cell[self._graph.vertex(position)]

    def __setitem__(self, position, board_cell):
        self._graph.vp.cell[self._graph.vertex(position)] = board_cell

    def __contains__(self, position):
        return position in range(0, self.vertices_count())

    def vertices_count(self):
        return self._graph.num_vertices()

    def edges_count(self):
        return self._graph.num_edges()

    def has_edge(self, source_vertice, target_vertice, direction):
        for e in self._graph.vertex(source_vertice).out_edges():
            if (
                int(e.target()) == target_vertice and
                self._graph.ep.direction[e] == direction
            ):
                return True
        return False

    def out_edges_count(self, source_vertice, target_vertice):
        return len([
            1 for e in self._graph.vertex(source_vertice).out_edges()
            if int(e.target()) == target_vertice
        ])

    def reconfigure_edges(self, width, height, tessellation):
        """
        Uses tessellation object to create all edges in graph.
        """
        self._graph.clear_edges()
        for source_vertice in self._graph.vertices():
            for direction in tessellation.legal_directions:
                neighbor_vertice = tessellation.neighbor_position(
                    int(source_vertice),
                    direction,
                    board_width=width,
                    board_height=height
                )
                if neighbor_vertice is not None:
                    e = self._graph.add_edge(
                        source_vertice, neighbor_vertice, add_missing=False
                    )
                    self._graph.ep.direction[e] = direction

    # TODO: Faster version?
    # def reconfigure_edges(self, width, height, tessellation):
    #     """
    #     Uses tessellation object to create all edges in graph.
    #     """
    #     self._graph.clear_edges()
    #     edges_to_add = []
    #     directions_to_add = dict()
    #     for source_vertice in self._graph.vertices():
    #         for direction in tessellation.legal_directions:
    #             neighbor_vertice = tessellation.neighbor_position(
    #                 int(source_vertice), direction,
    #                 board_width=width, board_height=height
    #             )
    #             if neighbor_vertice is not None:
    #                 edge = (int(source_vertice), neighbor_vertice,)

    #                 edges_to_add.append(edge)

    #                 if edge not in directions_to_add:
    #                     directions_to_add[edge] = deque()

    #                 directions_to_add[edge].append(direction)

    #     self._graph.add_edge_list(edges_to_add) if edges_to_add else None

    #     for e in edges_to_add:
    #         e_descriptors = self._graph.edge(
    #             s = self._graph.vertex(e[0]),
    #             t = self._graph.vertex(e[1]),
    #             all_edges = True
    #         )

    #         for e_descriptor in e_descriptors:
    #             if len(directions_to_add[e]) > 0:
    #                 self._graph.ep.direction[e_descriptor] = directions_to_add[e][0]
    #                 directions_to_add[e].popleft()

    def calculate_edge_weights(self):
        for e in self._graph.edges():
            self._graph.ep.weight[e] = self.out_edge_weight(int(e.target()))

    def neighbor(self, from_position, direction):
        try:
            for e in self._graph.vertex(from_position).out_edges():
                if self._graph.ep.direction[e] == direction:
                    return int(e.target())
        except ValueError as e:
            raise IndexError(e.args)

        return None

    def wall_neighbors(self, from_position):
        return [
            int(n) for n in self._graph.vertex(from_position).out_neighbours()
            if self[int(n)].is_wall
        ]

    def all_neighbors(self, from_position):
        return [
            int(n) for n in self._graph.vertex(from_position).out_neighbours()
        ]

    def shortest_path(self, start_position, end_position):
        try:
            return [
                int(v)
                for v in shortest_path(
                    g=self._graph,
                    source=self._graph.vertex(start_position),
                    target=self._graph.vertex(end_position),
                )[0]
            ]
        except ValueError:
            return []

    def dijkstra_path(self, start_position, end_position):
        try:
            self.calculate_edge_weights()
            return [
                int(v)
                for v in shortest_path(
                    g=self._graph,
                    source=self._graph.vertex(start_position),
                    target=self._graph.vertex(end_position),
                    weights=self._graph.ep.weight,
                )[0]
            ]
        except ValueError:
            return []

    def position_path_to_direction_path(self, position_path):
        retv = []
        src_vertice_index = 0
        for target_vertice in position_path[1:]:
            source_vertice = position_path[src_vertice_index]
            src_vertice_index += 1

            for out_edge in self._graph.vertex(source_vertice).out_edges():
                if int(out_edge.target()) == target_vertice:
                    retv.append(self._graph.ep.direction[out_edge])

        return {
            'source_position': position_path[0] if position_path else None,
            'path': retv
        }
