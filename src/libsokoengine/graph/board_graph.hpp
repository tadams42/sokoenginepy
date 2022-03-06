#ifndef BOARD_GRAPH_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_GRAPH_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "direction.hpp"
#include "sokoengine_config.hpp"

#include <memory>
#include <vector>

namespace sokoengine {

class BoardCell;
class Tessellation;

///
/// Exception.
///
class LIBSOKOENGINE_API BoardSizeExceededError : public std::runtime_error {
public:
  BoardSizeExceededError(const std::string &mess);
  virtual ~BoardSizeExceededError();
};

///
/// Type of graph
///
enum class LIBSOKOENGINE_API GraphType : int { DIRECTED = 0, DIRECTED_MULTI = 1 };

///
/// Ordered collection of board positions usually describing continuous board
/// path.
///
typedef std::vector<position_t> Positions;

///
/// Ordered collection of Directions usually describing continuous board path.
///
typedef std::vector<Direction> Directions;

///
/// Board graph implementation.
///
class LIBSOKOENGINE_API BoardGraph {
public:
  ///
  /// Edge weight type
  ///
  typedef unsigned char weight_t;

  explicit BoardGraph(board_size_t board_width = 0, board_size_t board_height = 0,
                      const GraphType &graph_type = GraphType::DIRECTED);
  BoardGraph(const BoardGraph &rv);
  BoardGraph &operator=(const BoardGraph &rv);
  BoardGraph(BoardGraph &&rv);
  BoardGraph &operator=(BoardGraph &&rv);
  virtual ~BoardGraph();

  const BoardCell &cell_at(position_t position) const;
  BoardCell &cell_at(position_t position);
  const BoardCell &cell(position_t position) const;
  BoardCell &cell(position_t position);
  const BoardCell operator[](position_t position) const;
  BoardCell &operator[](position_t position);

  bool contains(position_t position) const;
  board_size_t vertices_count() const;
  board_size_t edges_count() const;
  board_size_t board_width() const;
  board_size_t board_height() const;

  bool has_edge(position_t source_position, position_t dest_position,
                const Direction &direction) const;
  board_size_t out_edges_count(position_t source_position,
                               position_t target_position) const;
  void remove_all_edges();
  void add_edge(position_t source_position, position_t neighbor_position,
                const Direction &direction);
  weight_t out_edge_weight(position_t target_position) const;

  position_t neighbor(position_t from_position, const Direction &direction) const;
  position_t neighbor_at(position_t from_position, const Direction &direction) const;
  Positions wall_neighbors(position_t from_position) const;
  Positions all_neighbors(position_t from_position) const;
  Positions shortest_path(position_t start_position, position_t end_position) const;
  Positions dijkstra_path(position_t start_position, position_t end_position) const;
  Positions find_move_path(position_t start_position, position_t end_position) const;
  Positions find_jump_path(position_t start_position, position_t end_position) const;

  Directions positions_path_to_directions_path(const Positions &positions_path) const;
  Positions positions_reachable_by_pusher(
    position_t pusher_position,
    const Positions &excluded_positions = Positions()) const;
  position_t
  normalized_pusher_position(position_t pusher_position,
                             const Positions &excluded_positions = Positions()) const;
  void mark_play_area();
  position_t path_destination(position_t start_position,
                              const Directions &directions_path) const;

  void reconfigure_edges(const Tessellation &tessellation);

private:
  class LIBSOKOENGINE_LOCAL PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace sokoengine

#endif // HEADER_GUARD
