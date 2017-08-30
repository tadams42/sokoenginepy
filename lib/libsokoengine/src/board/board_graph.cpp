#include "board_graph.hpp"
#include "board_cell.hpp"

#include <algorithm>
#include <boost/foreach.hpp>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/dijkstra_shortest_paths.hpp>
#include <boost/graph/breadth_first_search.hpp>

using namespace std;
using namespace boost;
using namespace boost::graph;

namespace sokoengine {

namespace implementation {

  struct GraphEdgePropertyT {
    GraphEdgePropertyT() : weight(1), direction(Direction::LEFT.pack()) {}
    BoardGraph::weight_t weight;
    Direction::packed_t direction;
  };

  //
  // Notes: Trioban needs to store parallel edges
  //   => we must store edges in sequence, not associative container.
  //   => we must keep track when adding edges not to add duplicate ones (although parallel are allowed)
  //   => longer graph construction/rebuilding times
  //   => doesn't impact gameplay/movement (which is performed on already constructed graph)
  // Generally there is no edge adding or removal once graph is constructed (thus,
  // no speed improvement in choosing listS instead of vecS).
  //
  typedef boost::adjacency_list<
    boost::vecS,             // OutEdgeList
    boost::vecS,             // VertexList
    boost::directedS,        // Directed
    BoardCell,               // VertexProperties
    GraphEdgePropertyT,      // EdgeProperties
    boost::no_property,      // GraphProperties
    boost::vecS              // EdgeList
  > GraphT;

  typedef GraphT::vertex_descriptor vertex_descriptor;
  typedef GraphT::edge_descriptor edge_descriptor;
  typedef GraphT::vertex_iterator vertex_iterator;
  typedef GraphT::out_edge_iterator out_edge_iterator;
} // namespace implementation

using namespace implementation;

const BoardGraph::weight_t BoardGraph::_MAX_EDGE_WEIGHT;

class LIBSOKOENGINE_LOCAL BoardGraph::PIMPL {
public:
  typedef std::function<bool (position_t)> IsObstacleFunctor;
  GraphT m_graph;
  GraphType m_graph_type;

  /// Cached values of some of graph properties
  size_t m_number_of_vertices;

  PIMPL(size_t number_of_vertices, const GraphType& graph_type) :
    m_graph(number_of_vertices), m_graph_type(graph_type),
    m_number_of_vertices(0)
  {
    m_number_of_vertices = num_vertices(m_graph);
  }

  PIMPL(const PIMPL& rv) = default;
  PIMPL& operator=(const PIMPL& rv) = default;
  PIMPL(PIMPL&& rv) = default;
  PIMPL& operator=(PIMPL&& rv) = default;

  const BoardCell& cell_at(position_t position) const {
    return const_cast<PIMPL*>(this)->cell_at(position);
  }

  BoardCell& cell_at(position_t position) {
    if (!contains(position)) throw out_of_range("Board index out of range!");
    return m_graph[position];
  }

  bool contains(position_t position) const {
    return position < m_number_of_vertices;
  }

  BoardGraph::weight_t out_edge_weight(position_t target_position) const {
    const BoardCell& target_cell = cell_at(target_position);
    weight_t weight = 1;
    if (
      target_cell.is_wall() || target_cell.has_box() || target_cell.has_pusher()
    )
      weight = _MAX_EDGE_WEIGHT;

    return weight;
  }

  void set_weights_to_edges() {
    BOOST_FOREACH(const vertex_descriptor& v, vertices(m_graph))
      BOOST_FOREACH(const edge_descriptor& e, out_edges(v, m_graph))
        m_graph[e].weight = out_edge_weight(boost::target(e, m_graph));
  }

  Positions reachables(
    position_t root, const Positions& excluded, IsObstacleFunctor is_obstacle
  ) const {
    if (!contains(root))
      throw out_of_range("Starting position is off board!");

    Positions reachables;

    auto is_excluded = [&] (const Positions& lp, position_t lv) {
      return any_of(
        lp.cbegin(), lp.cend(), [&lv](position_t rv){ return lv == rv; }
      );
    };

    vector<bool> visited(m_number_of_vertices, false);
    visited[root] = true;

    typedef deque<position_t> PositionsQueue;
    PositionsQueue to_inspect;
    to_inspect.push_back(root);

    while(!to_inspect.empty()) {
      position_t current_position = to_inspect.front();
      to_inspect.pop_front();

      if(current_position == root || !is_excluded(excluded, current_position))
        reachables.push_back(current_position);

      BOOST_FOREACH(const edge_descriptor& e, out_edges(current_position, m_graph)) {
        position_t neighbor = get(vertex_index, m_graph, boost::target(e, m_graph));
        if (visited[neighbor] == false) {
          if (!is_obstacle(neighbor)) to_inspect.push_back(neighbor);
          visited[neighbor] = true;
        }
      }
    }
    return reachables;
  }
};

BoardGraph::BoardGraph(size_t number_of_vertices, const GraphType& graph_type) :
  m_impl(std::make_unique<PIMPL>(number_of_vertices, graph_type))
{}

BoardGraph::BoardGraph(const BoardGraph& rv) :
  m_impl(std::make_unique<PIMPL>(*rv.m_impl))
{}

BoardGraph& BoardGraph::operator=(const BoardGraph& rv) {
  if (this != &rv) m_impl = std::make_unique<PIMPL>(*rv.m_impl);
  return *this;
}

BoardGraph::BoardGraph(BoardGraph &&) = default;

BoardGraph& BoardGraph::operator=(BoardGraph &&) = default;

BoardGraph::~BoardGraph() = default;

const BoardCell& BoardGraph::cell_at(position_t position) const {
  return m_impl->cell_at(position);
}

BoardCell& BoardGraph::cell_at(position_t position) {
  return m_impl->cell_at(position);
}

const BoardCell& BoardGraph::cell(position_t position) const {
  return m_impl->m_graph[position];
}

BoardCell& BoardGraph::cell(position_t position) {
  return m_impl->m_graph[position];
}

const BoardCell BoardGraph::operator[] (position_t position) const {
  return m_impl->m_graph[position];
}

BoardCell& BoardGraph::operator[] (position_t position) {
  return m_impl->m_graph[position];
}

bool BoardGraph::contains(position_t position) const {
  return m_impl->contains(position);
}

size_t BoardGraph::vertices_count() const {
  return m_impl->m_number_of_vertices;
}

size_t BoardGraph::edges_count() const { return num_edges(m_impl->m_graph); }

bool BoardGraph::has_edge(
  position_t source_vertex, position_t dest_vertex, const Direction& direction
) const {
  if (!contains(source_vertex) || !contains(dest_vertex)) return false;

  const auto edges = out_edges(source_vertex, m_impl->m_graph);
  char d = direction.pack();
  return edges.second != find_if(
    edges.first, edges.second,
    [&] (const edge_descriptor& e) {
      return m_impl->m_graph[e].direction == d;
    }
  );
}

size_t BoardGraph::out_edges_count(
  position_t source_vertex, position_t target_vertex
) const {
  if (!contains(source_vertex) || !contains(target_vertex)) return 0;
  size_t retv = 0;
  BOOST_FOREACH(const edge_descriptor& e, out_edges(source_vertex, m_impl->m_graph))
    if (target(e, m_impl->m_graph) == target_vertex) retv += 1;
  return retv;
}

void BoardGraph::remove_all_edges() {
  BOOST_FOREACH(const vertex_descriptor& v, vertices(m_impl->m_graph))
    clear_vertex(v, m_impl->m_graph);
}

void BoardGraph::add_edge(
  position_t source_vertex, position_t neighbor_vertex, const Direction& direction
) {
  if (!contains(source_vertex) || !contains(neighbor_vertex)) {
    throw out_of_range("Board index out of range!");
  }

  bool should_add;
  if (m_impl->m_graph_type == GraphType::DIRECTED_MULTI)
    should_add = true;
  else
    should_add = !has_edge(source_vertex, neighbor_vertex, direction);

  if (should_add) {
    GraphEdgePropertyT e;
    e.direction = direction.pack();
    boost::add_edge(source_vertex, neighbor_vertex, e, m_impl->m_graph);
  }
}

BoardGraph::weight_t BoardGraph::out_edge_weight(position_t target_position) const {
  return m_impl->out_edge_weight(target_position);
}

position_t BoardGraph::neighbor(
  position_t from_position, const Direction& direction
) const {
  vertex_descriptor v = vertex(from_position, m_impl->m_graph);
  const auto edges = out_edges(v, m_impl->m_graph);
  char d = direction.pack();
  auto edge = find_if(
    edges.first, edges.second,
    [&] (const edge_descriptor& e) {
      return m_impl->m_graph[e].direction == d;
    }
  );
  if (edge != edges.second)
    return get(
      boost::vertex_index, m_impl->m_graph,
      boost::target(*edge, m_impl->m_graph)
    );
  return NULL_POSITION;
}

position_t BoardGraph::neighbor_at(
  position_t from_position, const Direction& direction
) const {
  if (!contains(from_position)) throw out_of_range("Board index out of range!");
  return neighbor(from_position, direction);
}

Positions BoardGraph::wall_neighbors(position_t from_position) const {
  if (!contains(from_position)) throw out_of_range("Board index out of range!");

  Positions retv;
  BOOST_FOREACH(
    const edge_descriptor& edge, out_edges(from_position, m_impl->m_graph)
  )
    if (m_impl->m_graph[boost::target(edge, m_impl->m_graph)].is_wall())
      retv.push_back(
        get(
          boost::vertex_index, m_impl->m_graph,
          boost::target(edge, m_impl->m_graph)
        )
      );

  return retv;
}

Positions BoardGraph::all_neighbors(position_t from_position) const {
  if (!contains(from_position)) throw out_of_range("Board index out of range!");

  Positions retv;
  BOOST_FOREACH(
    const edge_descriptor& edge, out_edges(from_position, m_impl->m_graph)
  )
    retv.push_back(
      get(
        boost::vertex_index, m_impl->m_graph,
        boost::target(edge, m_impl->m_graph)
      )
    );

  return retv;
}

Positions BoardGraph::shortest_path(
  position_t start_position, position_t end_position
) const {
  if (!contains(start_position) || !contains(end_position))
    throw out_of_range("Board index out of range!");

  deque<vertex_descriptor> predecesors(m_impl->m_number_of_vertices);
  auto predecessors_map = make_iterator_property_map(
    predecesors.begin(), get(boost::vertex_index, m_impl->m_graph)
  );

  vertex_descriptor start = vertex(start_position, m_impl->m_graph);
  vertex_descriptor end = vertex(end_position, m_impl->m_graph);

  breadth_first_search(
    m_impl->m_graph, start,
    visitor(
      make_bfs_visitor(record_predecessors(predecessors_map, on_tree_edge()))
    )
  );

  // Backtracking to source
  Positions path;
  // Start by setting 'u' to the destination node's predecessor
  predecessors_map[start] = start;
  vertex_descriptor u = predecessors_map[end];
  vertex_descriptor v = end;
  for(;
    // Keep tracking the path until we get to the source
    u != v;
    // Set the current vertex to the current predecessor, and the
    // predecessor to one level up
    v = u, u = predecessors_map[v]
  )
    path.push_back(v);
  path.push_back(start_position);
  reverse(path.begin(), path.end());
  return path;
}

Positions BoardGraph::dijkstra_path(
  position_t start_position, position_t end_position
) const {
  if (!contains(start_position) || !contains(end_position))
    throw out_of_range("Board index out of range!");

  const_cast<BoardGraph*>(this)->m_impl->set_weights_to_edges();

  deque<double> distances(m_impl->m_number_of_vertices);
  deque<vertex_descriptor> predecesors(m_impl->m_number_of_vertices);

  auto weightmap = get(&GraphEdgePropertyT::weight, m_impl->m_graph);
  auto distances_map = make_iterator_property_map(
    distances.begin(), get(boost::vertex_index, m_impl->m_graph)
  );
  auto predecessors_map = make_iterator_property_map(
    predecesors.begin(), get(boost::vertex_index, m_impl->m_graph)
  );

  vertex_descriptor start = vertex(start_position, m_impl->m_graph);
  vertex_descriptor end = vertex(end_position, m_impl->m_graph); // destination

  dijkstra_shortest_paths(
    m_impl->m_graph, start,
    weight_map(weightmap).distance_map(distances_map).
    predecessor_map(predecessors_map)
  );

  // Backtracking to source
  Positions path;
  // Start by setting 'u' to the destination node's predecessor
  predecessors_map[start] = start;
  vertex_descriptor u = predecessors_map[end];
  vertex_descriptor v = end;
  for(;
    // Keep tracking the path until we get to the source
    u != v;
    // Set the current vertex to the current predecessor, and the
    // predecessor to one level up
    v = u, u = predecessors_map[v]
  )
    path.push_back(v);
  path.push_back(start_position);
  reverse(path.begin(), path.end());
  return path;
}

Positions BoardGraph::find_move_path(
  position_t start_position, position_t end_position
) const {
  Positions path = dijkstra_path(start_position, end_position);

  Positions retv;

  auto i = path.cbegin();
  auto end = path.cend();

  if (i != end) {
    retv.push_back(*i);
    i++;
  }

  for(; i != end; i++) {
    if (cell(*i).can_put_pusher_or_box()) retv.push_back(*i);
    else break;
  }

  if (retv != path) return Positions();
  return path;
}

Positions BoardGraph::find_jump_path(
  position_t start_position, position_t end_position
) const {
  return shortest_path(start_position, end_position);
}

Directions BoardGraph::positions_path_to_directions_path(
  const Positions& positions_path
) const {
  position_t src_vertex_index = 0;

  if (
    positions_path.size() > 0 &&
    !contains(positions_path[src_vertex_index])
  )
    throw out_of_range("Board index out of range!");

  Directions retv;

  if (positions_path.size() <= 1) return retv;

  auto i = positions_path.begin(); i++;
  for(; i != positions_path.end(); ++i) {
    position_t src_vertex = positions_path[src_vertex_index];
    position_t target_vertex = *i;
    src_vertex_index += 1;

    if (!contains(src_vertex) || !contains(target_vertex))
      throw out_of_range("Board index out of range!");

    BOOST_FOREACH(
      const edge_descriptor& edge, out_edges(src_vertex, m_impl->m_graph)
    )
      if (boost::target(edge, m_impl->m_graph) == target_vertex)
        retv.push_back(
          Direction::unpack(m_impl->m_graph[edge].direction)
        );
  }

  return retv;
}

void BoardGraph::mark_play_area() {
  Positions piece_positions;
  size_t vertice_count = vertices_count();

  for(position_t i = 0; i < vertice_count; ++i) {
    if (cell(i).has_box() || cell(i).has_pusher()) {
      cell(i).set_is_in_playable_area(true);
      piece_positions.push_back(i);
    } else {
      cell(i).set_is_in_playable_area(false);
    }
  }

  PIMPL::IsObstacleFunctor is_obstacle = [&] (position_t pos) {
    return cell(pos).is_wall();
  };

  for(auto piece_position : piece_positions) {
    Positions reachables_pos = m_impl->reachables(
      piece_position, piece_positions, is_obstacle
    );
    for(auto reachable_position : reachables_pos) {
      cell(reachable_position).set_is_in_playable_area(true);
    }
  }
}

Positions BoardGraph::positions_reachable_by_pusher(
  position_t pusher_position, const Positions& excluded_positions
) const {
  PIMPL::IsObstacleFunctor is_obstacle = [&] (position_t pos) {
    return !cell(pos).can_put_pusher_or_box();
  };

  return m_impl->reachables(pusher_position, excluded_positions, is_obstacle);
}

position_t BoardGraph::normalized_pusher_position(
  position_t pusher_position, const Positions& excluded_positions
) const {
  Positions reachables_pos = positions_reachable_by_pusher(
    pusher_position, excluded_positions
  );
  if (reachables_pos.size() > 0)
    return *min_element(reachables_pos.cbegin(), reachables_pos.cend());
  else return pusher_position;
}

position_t BoardGraph::path_destination(
  position_t start_position, const Directions& directions_path
) const {
  if (!contains(start_position))
    throw out_of_range("Starting position is off board!");

  position_t retv = start_position, next_target;
  for (const Direction& direction : directions_path) {
    next_target = neighbor_at(retv, direction);
    if (next_target != NULL_POSITION) {
      retv = next_target;
    } else {
      break;
    }
  }
  return retv;
}

} // namespace sokoengine
