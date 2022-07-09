#include "board_graph.hpp"

#include "board_cell.hpp"
#include "board_state.hpp"
#include "pusher_step.hpp"
#include "puzzle.hpp"
#include "tessellation.hpp"

#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/breadth_first_search.hpp>
#include <boost/graph/dijkstra_shortest_paths.hpp>

using sokoengine::io::CellOrientation;
using sokoengine::io::Puzzle;
using std::deque;
using std::make_unique;
using std::out_of_range;
using std::range_error;
using std::string;
using std::tie;
using std::to_string;
using std::vector;

namespace sokoengine {
namespace game {

InvalidPositionError::InvalidPositionError(long position)
  : out_of_range("Board position " + to_string(position) + " is out of range!") {}

InvalidPositionError::~InvalidPositionError() = default;

namespace implementation {

typedef uint8_t edge_weight_t;

struct graph_edge_property_t {
  graph_edge_property_t()
    : weight(1)
    , direction(Direction::LEFT) {}

  edge_weight_t weight;
  Direction     direction;
};

//
// Notes: Trioban needs to store parallel edges
//   => we must store edges in sequence, not associative container.
//   => we must keep track when adding edges not to add duplicate ones (although
//   parallel are allowed)
//   => longer graph construction/rebuilding times
//   => doesn't impact gameplay/movement (which is performed on already constructed
//   graph)
// Generally there is no edge adding or removal once graph is constructed (thus,
// no speed improvement in choosing listS instead of vecS).
//
typedef boost::adjacency_list<
  boost::vecS,           // OutEdgeList
  boost::vecS,           // VertexList
  boost::directedS,      // Directed
  BoardCell,             // VertexProperties
  graph_edge_property_t, // EdgeProperties
  boost::no_property,    // GraphProperties
  boost::vecS>           // EdgeList
  graph_t;

typedef graph_t::vertex_descriptor vertex_descriptor_t;
typedef graph_t::edge_descriptor   edge_descriptor_t;
typedef graph_t::vertex_iterator   vertex_iterator_t;
typedef graph_t::out_edge_iterator out_edge_iterator_t;
typedef graph_t::in_edge_iterator  in_edge_iterator_t;

} // namespace implementation

using implementation::edge_descriptor_t;
using implementation::edge_weight_t;
using implementation::in_edge_iterator_t;
using implementation::out_edge_iterator_t;
using implementation::vertex_descriptor_t;
using implementation::vertex_iterator_t;

class LIBSOKOENGINE_LOCAL BoardGraph::PIMPL {
  bool has_edge(position_t u, position_t v, const Direction &direction) const {
    //
    // False if
    //
    // - edge doesn't exist
    // - `src` or `dst` is off board position
    //
    if (!contains(u) || !contains(v))
      return false;

    out_edge_iterator_t e_i, e_iend;
    tie(e_i, e_iend) = boost::out_edges(u, m_graph);
    return e_iend != find_if(e_i, e_iend, [&](const edge_descriptor_t &e) {
             return m_graph[e].direction == direction;
           });
  }

  static constexpr edge_weight_t MAX_EDGE_WEIGHT = 100;

  edge_weight_t out_edge_weight(position_t v) const {
    const BoardCell &target_cell = m_graph[v];
    edge_weight_t    weight      = 1;
    if (target_cell.is_wall() || target_cell.has_box() || target_cell.has_pusher())
      weight = MAX_EDGE_WEIGHT;
    return weight;
  }

  void remove_all_edges() {
    vertex_iterator_t v_i, v_iend;
    for (tie(v_i, v_iend) = boost::vertices(m_graph); v_i != v_iend; ++v_i) {
      boost::clear_vertex(*v_i, m_graph);
    }
  }

  board_size_t out_edges_count(position_t u, position_t v) const {
    is_valid_or_throw(u);
    is_valid_or_throw(v);

    board_size_t        retv = 0;
    out_edge_iterator_t e_i, e_iend;
    tie(e_i, e_iend) = boost::out_edges(u, m_graph);
    for (; e_i != e_iend; ++e_i) {
      if (boost::target(*e_i, m_graph) == v)
        retv += 1;
    }
    return retv;
  }

public:
  typedef std::function<bool(position_t)> IsObstacleFunctor;
  implementation::graph_t                 m_graph;
  Tessellation                            m_tessellation;
  board_size_t                            m_board_width;
  board_size_t                            m_board_height;

  PIMPL(board_size_t width, board_size_t height, const Tessellation &tessellation)
    : m_graph(width * height)
    , m_tessellation(tessellation)
    , m_board_width(width)
    , m_board_height(height) {
    if (width > Config::MAX_WIDTH)
      throw range_error(
        "Puzzle width " + to_string(width) + "must be <= Config.MAX_WIDTH!"
      );
    if (height > Config::MAX_HEIGHT)
      throw range_error(
        "Puzzle height " + to_string(height) + "must be <= Config.MAX_HEIGHT!"
      );
  }

  board_size_t vertices_count() const { return m_board_width * m_board_height; }

  bool contains(position_t v) const { return v < vertices_count(); }

  void is_valid_or_throw(position_t v) const {
    if (!contains(v))
      throw InvalidPositionError(v);
  }

  void set_weights_to_edges() {
    vertex_iterator_t v_i, v_iend;
    for (tie(v_i, v_iend) = boost::vertices(m_graph); v_i != v_iend; ++v_i) {
      out_edge_iterator_t e_i, e_iend;
      for (tie(e_i, e_iend) = boost::out_edges(*v_i, m_graph); e_i != e_iend; ++e_i) {
        m_graph[*e_i].weight = out_edge_weight(boost::target(*e_i, m_graph));
      }
    }
  }

  Positions reachables(
    position_t root, const Positions &excluded, IsObstacleFunctor is_obstacle
  ) const {
    Positions reachables;

    auto is_excluded = [&](const Positions &lp, position_t lv) {
      return any_of(lp.cbegin(), lp.cend(), [&lv](position_t rv) {
        return lv == rv;
      });
    };

    vector<bool> visited(vertices_count(), false);
    visited[root] = true;

    typedef deque<position_t> PositionsQueue;
    PositionsQueue            to_inspect;
    to_inspect.push_back(root);

    while (!to_inspect.empty()) {
      position_t current_position = to_inspect.front();
      to_inspect.pop_front();

      if (current_position == root || !is_excluded(excluded, current_position))
        reachables.push_back(current_position);

      out_edge_iterator_t e_i, e_iend;
      tie(e_i, e_iend) = boost::out_edges(current_position, m_graph);
      for (; e_i != e_iend; ++e_i) {
        position_t neighbor =
          get(boost::vertex_index, m_graph, boost::target(*e_i, m_graph));
        if (visited[neighbor] == false) {
          if (!is_obstacle(neighbor))
            to_inspect.push_back(neighbor);
          visited[neighbor] = true;
        }
      }
    }
    return reachables;
  }

  void reconfigure_edges() {
    remove_all_edges();

    const BaseTessellation &tessellation = BaseTessellation::instance(m_tessellation);
    GraphType               graph_type   = tessellation.graph_type();

    board_size_t size = vertices_count();
    for (board_size_t u = 0; u < size; ++u) {
      for (const Direction &direction : tessellation.legal_directions()) {
        position_t v =
          tessellation.neighbor_position(u, direction, m_board_width, m_board_height);
        if (v != Config::NO_POS) {
          bool should_add;
          if (graph_type == GraphType::DIRECTED_MULTI) {
            should_add = true;
          } else {
            should_add = !has_edge(u, v, direction);
          }
          if (should_add) {
            implementation::graph_edge_property_t e;
            e.direction = direction;
            boost::add_edge(u, v, e, m_graph);
          }
        }
      }
    }
  }
};

BoardGraph::BoardGraph(const Puzzle &puzzle)
  : m_impl(make_unique<PIMPL>(puzzle.width(), puzzle.height(), puzzle.tessellation())) {
  board_size_t s = puzzle.size();
  for (position_t pos = 0; pos < s; ++pos) {
    m_impl->m_graph[pos] = BoardCell(puzzle[pos]);
  }
  m_impl->reconfigure_edges();
}

BoardGraph::BoardGraph(const BoardGraph &rv)
  : m_impl(make_unique<PIMPL>(*rv.m_impl)) {}

BoardGraph &BoardGraph::operator=(const BoardGraph &rv) {
  if (this != &rv)
    m_impl = make_unique<PIMPL>(*rv.m_impl);
  return *this;
}

BoardGraph::BoardGraph(BoardGraph &&) = default;

BoardGraph &BoardGraph::operator=(BoardGraph &&) = default;

BoardGraph::~BoardGraph() = default;

const BoardCell &BoardGraph::cell_at(position_t position) const {
  return const_cast<BoardGraph *>(this)->cell_at(position);
}

BoardCell &BoardGraph::cell_at(position_t position) {
  m_impl->is_valid_or_throw(position);
  return m_impl->m_graph[position];
}

const BoardCell &BoardGraph::cell(position_t position) const {
  return m_impl->m_graph[position];
}

BoardCell &BoardGraph::cell(position_t position) { return m_impl->m_graph[position]; }

const BoardCell &BoardGraph::operator[](position_t position) const {
  return m_impl->m_graph[position];
}

BoardCell &BoardGraph::operator[](position_t position) {
  return m_impl->m_graph[position];
}

Tessellation BoardGraph::tessellation() const { return m_impl->m_tessellation; }

CellOrientation BoardGraph::cell_orientation(position_t position) const {
  return BaseTessellation::instance(m_impl->m_tessellation)
    .cell_orientation(position, m_impl->m_board_width, m_impl->m_board_height);
}

string BoardGraph::to_board_str(bool use_visible_floor, bool rle_encode) const {
  Puzzle::unique_ptr_t puzzle = Puzzle::instance_from(
    m_impl->m_tessellation, m_impl->m_board_width, m_impl->m_board_height
  );

  for (position_t pos = 0; pos < size(); pos++) {
    puzzle->set(pos, (*this)[pos].str());
  }

  return puzzle->to_board_str(use_visible_floor, rle_encode);
}

string BoardGraph::str() const { return to_board_str(false); }

bool BoardGraph::contains(position_t position) const {
  return m_impl->contains(position);
}

board_size_t BoardGraph::size() const { return m_impl->vertices_count(); }

board_size_t BoardGraph::edges_count() const { return num_edges(m_impl->m_graph); }

board_size_t BoardGraph::board_width() const { return m_impl->m_board_width; }

board_size_t BoardGraph::board_height() const { return m_impl->m_board_height; }

Edges BoardGraph::out_edges(position_t src) const {
  m_impl->is_valid_or_throw(src);

  Edges retv;

  out_edge_iterator_t e_i, e_iend;
  tie(e_i, e_iend) = boost::out_edges(src, m_impl->m_graph);
  for (; e_i != e_iend; ++e_i) {
    retv.emplace_back(
      src, boost::target(*e_i, m_impl->m_graph), m_impl->m_graph[*e_i].direction
      // , m_impl->m_graph[*e_i].weight
    );
  }

  return retv;
}

position_t
BoardGraph::neighbor(position_t from_position, const Direction &direction) const {
  vertex_descriptor_t v     = boost::vertex(from_position, m_impl->m_graph);
  const auto          edges = boost::out_edges(v, m_impl->m_graph);
  auto edge = find_if(edges.first, edges.second, [&](const edge_descriptor_t &e) {
    return m_impl->m_graph[e].direction == direction;
  });
  if (edge != edges.second)
    return get(
      boost::vertex_index, m_impl->m_graph, boost::target(*edge, m_impl->m_graph)
    );
  return Config::NO_POS;
}

position_t
BoardGraph::neighbor_at(position_t from_position, const Direction &direction) const {
  m_impl->is_valid_or_throw(from_position);
  return neighbor(from_position, direction);
}

Positions BoardGraph::wall_neighbors(position_t from_position) const {
  m_impl->is_valid_or_throw(from_position);

  Positions retv;

  auto index = boost::get(boost::vertex_index, m_impl->m_graph);

  out_edge_iterator_t e_i, e_iend;
  tie(e_i, e_iend) = boost::out_edges(from_position, m_impl->m_graph);

  for (; e_i != e_iend; ++e_i) {
    const BoardCell &c = m_impl->m_graph[boost::source(*e_i, m_impl->m_graph)];
    if (c.is_wall())
      retv.push_back(index[boost::target(*e_i, m_impl->m_graph)]);
  }

  return retv;
}

Directions BoardGraph::wall_neighbor_directions(position_t src) const {
  m_impl->is_valid_or_throw(src);

  Directions retv;

  out_edge_iterator_t e_i, e_iend;
  tie(e_i, e_iend) = boost::out_edges(src, m_impl->m_graph);

  for (; e_i != e_iend; ++e_i) {
    const BoardCell &c = m_impl->m_graph[boost::target(*e_i, m_impl->m_graph)];
    if (c.is_wall())
      retv.push_back(m_impl->m_graph[*e_i].direction);
  }

  return retv;
}

Positions BoardGraph::all_neighbors(position_t from_position) const {
  m_impl->is_valid_or_throw(from_position);

  Positions retv;

  out_edge_iterator_t e_i, e_iend;
  tie(e_i, e_iend) = boost::out_edges(from_position, m_impl->m_graph);
  for (; e_i != e_iend; ++e_i) {
    retv.push_back(
      get(boost::vertex_index, m_impl->m_graph, boost::target(*e_i, m_impl->m_graph))
    );
  }

  return retv;
}

Positions
BoardGraph::shortest_path(position_t start_position, position_t end_position) const {
  m_impl->is_valid_or_throw(start_position);
  m_impl->is_valid_or_throw(end_position);

  deque<vertex_descriptor_t> predecesors(m_impl->vertices_count());
  auto                       predecessors_map = make_iterator_property_map(
    predecesors.begin(), get(boost::vertex_index, m_impl->m_graph)
  );

  vertex_descriptor_t start = vertex(start_position, m_impl->m_graph);
  vertex_descriptor_t end   = vertex(end_position, m_impl->m_graph);

  breadth_first_search(
    m_impl->m_graph,
    start,
    visitor(
      make_bfs_visitor(record_predecessors(predecessors_map, boost::on_tree_edge()))
    )
  );

  // Backtracking to source
  Positions path;
  // Start by setting 'u' to the destination node's predecessor
  predecessors_map[start] = start;
  vertex_descriptor_t u   = predecessors_map[end];
  vertex_descriptor_t v   = end;
  for (;
       // Keep tracking the path until we get to the source
       u != v;
       // Set the current position to the current predecessor, and the
       // predecessor to one level up
       v = u,
       u = predecessors_map[v])
    path.push_back(v);
  path.push_back(start_position);
  reverse(path.begin(), path.end());
  return path;
}

Positions
BoardGraph::dijkstra_path(position_t start_position, position_t end_position) const {
  m_impl->is_valid_or_throw(start_position);
  m_impl->is_valid_or_throw(end_position);

  const_cast<BoardGraph *>(this)->m_impl->set_weights_to_edges();

  deque<double>              distances(m_impl->vertices_count());
  deque<vertex_descriptor_t> predecesors(m_impl->vertices_count());

  auto weightmap = get(&implementation::graph_edge_property_t::weight, m_impl->m_graph);
  auto distances_map = make_iterator_property_map(
    distances.begin(), get(boost::vertex_index, m_impl->m_graph)
  );
  auto predecessors_map = make_iterator_property_map(
    predecesors.begin(), get(boost::vertex_index, m_impl->m_graph)
  );

  vertex_descriptor_t start = vertex(start_position, m_impl->m_graph);
  vertex_descriptor_t end   = vertex(end_position, m_impl->m_graph); // destination

  boost::dijkstra_shortest_paths(
    m_impl->m_graph,
    start,
    boost::weight_map(weightmap)
      .distance_map(distances_map)
      .predecessor_map(predecessors_map)
  );

  // Backtracking to source
  Positions path;
  // Start by setting 'u' to the destination node's predecessor
  predecessors_map[start] = start;
  vertex_descriptor_t u   = predecessors_map[end];
  vertex_descriptor_t v   = end;
  for (;
       // Keep tracking the path until we get to the source
       u != v;
       // Set the current position to the current predecessor, and the
       // predecessor to one level up
       v = u,
       u = predecessors_map[v])
    path.push_back(v);
  path.push_back(start_position);
  reverse(path.begin(), path.end());
  return path;
}

Positions
BoardGraph::find_move_path(position_t start_position, position_t end_position) const {
  Positions path = dijkstra_path(start_position, end_position);

  Positions retv;

  auto i   = path.cbegin();
  auto end = path.cend();

  if (i != end) {
    retv.push_back(*i);
    i++;
  }

  for (; i != end; i++) {
    if (cell(*i).can_put_pusher_or_box())
      retv.push_back(*i);
    else
      break;
  }

  if (retv != path)
    return Positions();
  return path;
}

Positions
BoardGraph::find_jump_path(position_t start_position, position_t end_position) const {
  return shortest_path(start_position, end_position);
}

Directions BoardGraph::positions_path_to_directions_path(const Positions &positions_path
) const {
  position_t src_vertex_index = 0;

  if (positions_path.size() > 0)
    m_impl->is_valid_or_throw(positions_path[src_vertex_index]);

  Directions retv;

  if (positions_path.size() <= 1)
    return retv;

  auto i = positions_path.begin();
  i++;
  for (; i != positions_path.end(); ++i) {
    position_t src_position    = positions_path[src_vertex_index];
    position_t target_position = *i;
    src_vertex_index += 1;

    m_impl->is_valid_or_throw(src_position);
    m_impl->is_valid_or_throw(target_position);

    out_edge_iterator_t e_i, e_iend;
    tie(e_i, e_iend) = boost::out_edges(src_position, m_impl->m_graph);
    for (; e_i != e_iend; ++e_i) {
      if (boost::target(*e_i, m_impl->m_graph) == target_position)
        retv.push_back(m_impl->m_graph[*e_i].direction);
    }
  }

  return retv;
}

position_t BoardGraph::path_destination(
  position_t start_position, const Directions &directions_path
) const {
  m_impl->is_valid_or_throw(start_position);

  position_t retv = start_position, next_target;
  for (const Direction &direction : directions_path) {
    next_target = neighbor_at(retv, direction);
    if (next_target == Config::NO_POS) {
      break;
    } else {
      retv = next_target;
    }
  }
  return retv;
}

Positions BoardGraph::positions_reachable_by_pusher(
  position_t pusher_position, const Positions &excluded_positions
) const {
  m_impl->is_valid_or_throw(pusher_position);

  PIMPL::IsObstacleFunctor is_obstacle = [&](position_t pos) {
    return !cell(pos).can_put_pusher_or_box();
  };

  return m_impl->reachables(pusher_position, excluded_positions, is_obstacle);
}

position_t BoardGraph::normalized_pusher_position(
  position_t pusher_position, const Positions &excluded_positions
) const {
  Positions reachables_pos =
    positions_reachable_by_pusher(pusher_position, excluded_positions);
  if (reachables_pos.size() > 0)
    return *min_element(reachables_pos.cbegin(), reachables_pos.cend());
  return pusher_position;
}

void BoardGraph::mark_play_area() {
  Positions    piece_positions;
  board_size_t vertice_count = m_impl->vertices_count();

  for (position_t i = 0; i < vertice_count; ++i) {
    if (cell(i).has_box() || cell(i).has_pusher()) {
      cell(i).set_is_in_playable_area(true);
      piece_positions.push_back(i);
    } else {
      cell(i).set_is_in_playable_area(false);
    }
  }

  PIMPL::IsObstacleFunctor is_obstacle = [&](position_t pos) {
    return cell(pos).is_wall();
  };

  for (auto piece_position : piece_positions) {
    Positions reachables_pos =
      m_impl->reachables(piece_position, piece_positions, is_obstacle);
    for (auto reachable_position : reachables_pos) {
      cell(reachable_position).set_is_in_playable_area(true);
    }
  }
}

Edge::Edge(position_t u, position_t v, Direction direction)
  : u(u)
  , v(v)
  , direction(direction) {}

bool Edge::operator==(const Edge &rv) const {
  return u == rv.u && v == rv.v && direction == rv.direction;
}

bool Edge::operator!=(const Edge &rv) const { return !(*this == rv); }

string Edge::repr() const {
  return (
    string("Edge(") + "u=" + to_string(u) + ", " + "v=" + to_string(v) + ", "
    + "direction=" + implementation::direction_str(direction) + ")"
  );
}

string Edge::str() const { return repr(); }

} // namespace game
} // namespace sokoengine
