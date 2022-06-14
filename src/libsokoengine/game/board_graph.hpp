#ifndef BOARD_GRAPH_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_GRAPH_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "config.hpp"

#include <stdexcept>
#include <memory>

namespace sokoengine {

namespace io {
class Puzzle;
} // namespace io

namespace game {

class BoardCell;

///
/// @exception
///
class LIBSOKOENGINE_API BoardSizeExceededError : public std::runtime_error {
public:
  explicit BoardSizeExceededError(const std::string &mess);
  virtual ~BoardSizeExceededError();
};


///
/// Board graph implementation.
///
class LIBSOKOENGINE_API BoardGraph {
public:
  ///
  /// Edge weight type
  ///
  typedef uint8_t weight_t;

  explicit BoardGraph(const io::Puzzle &puzzle);
  BoardGraph(const BoardGraph &rv);
  BoardGraph &operator=(const BoardGraph &rv);
  BoardGraph(BoardGraph &&rv);
  BoardGraph &operator=(BoardGraph &&rv);
  virtual ~BoardGraph();

  const BoardCell &cell_at(position_t position) const;
  BoardCell &cell_at(position_t position);
  const BoardCell &cell(position_t position) const;
  BoardCell &cell(position_t position);
  const BoardCell &operator[](position_t position) const;
  BoardCell &operator[](position_t position);

  Tessellation tessellation() const;

  ///
  /// Formatted string representation of board.
  ///
  std::string to_board_str(bool use_visible_floor = false,
                           bool rle_encode = false) const;
  std::string str() const;

  bool contains(position_t position) const;
  board_size_t vertices_count() const;
  board_size_t size() const;
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

  void reconfigure_edges();

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
