#ifndef BOARD_GRAPH_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_GRAPH_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "config.hpp"

#include <memory>
#include <stdexcept>

namespace sokoengine {

namespace io {
class Puzzle;
} // namespace io

namespace game {

class BoardCell;

class LIBSOKOENGINE_API BoardSizeExceededError : public std::runtime_error {
public:
  explicit BoardSizeExceededError(const std::string &mess);
  virtual ~BoardSizeExceededError();
};

///
/// Board graph implementation (using Boost::Graph under the hood).
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
  ///
  /// Same as to_board_str() but with hardcoded defaults.
  ///
  std::string str() const;

  bool contains(position_t position) const;
  board_size_t vertices_count() const;
  board_size_t size() const;
  board_size_t edges_count() const;
  board_size_t board_width() const;
  board_size_t board_height() const;

  bool has_edge(position_t src, position_t dst, const Direction &direction) const;

  ///
  /// Number of out-edges from `src` to `dst`.
  ///
  /// @returns
  /// Zero when no out edges exist or or any of positions is out of board position.
  ///
  board_size_t out_edges_count(position_t src, position_t dst) const;
  void remove_all_edges();

  ///
  /// Adds edges between two existing positions.
  ///
  /// @throws std::out_of_range when either source_position or neighbor_position is off
  ///         board
  ///
  void add_edge(position_t src, position_t dst, const Direction &direction);

  ///
  /// Calculates edge weight based on BoardCell in `target_position`.
  ///
  /// @throws std::out_of_range when target_position is off board
  ///
  weight_t out_edge_weight(position_t target_position) const;

  ///
  /// Neighbor position in `direction`.
  ///
  /// @returns Target position or Config::NO_POS
  ///
  /// @warning Doesn't validate `src`
  ///
  position_t neighbor(position_t src, const Direction &direction) const;

  ///
  /// Neighbor position in `direction`.
  ///
  /// @returns Target position or Config::NO_POS
  ///
  /// @throws std::out_of_range when `src` is off board
  ///
  position_t neighbor_at(position_t src, const Direction &direction) const;

  Positions wall_neighbors(position_t src) const;
  Positions all_neighbors(position_t src) const;

  ///
  /// Calculates shortest path between two positions with all positions having equal
  /// weight.
  ///
  /// @throws std::out_of_range when src or dst are off board
  ///
  Positions shortest_path(position_t src, position_t dst) const;
  ///
  /// Calculates shortest path between two positions not passing through board obstacles
  /// (walls, other pushers, etc...).
  ///
  /// @throws std::out_of_range when src or dst are off board
  ///
  Positions dijkstra_path(position_t src, position_t dst) const;
  ///
  /// Finds list of positions through which pusher must pass when moving without pushing
  /// boxes
  ///
  /// @throws std::out_of_range when src or dst are off board
  ///
  Positions find_move_path(position_t src, position_t dst) const;
  ///
  /// Finds list of positions through which pusher must pass when jumping
  ///
  /// @throws std::out_of_range when src or dst are off board
  ///
  Positions find_jump_path(position_t src, position_t dst) const;
  ///
  /// Converts path expressed as positions to one expressed as :class:`.Direction`.
  ///
  /// @throws std::Any of positions in `positions` off board
  ///
  Directions positions_path_to_directions_path(const Positions &positions_path) const;
  ///
  /// Finds all positions that are reachable by pusher standing on `pusher_position`.
  ///
  Positions positions_reachable_by_pusher(
    position_t pusher_position,
    const Positions &excluded_positions = Positions()) const;

  ///
  /// Finds top-left position reachable by pusher without pushing any boxes.
  ///
  position_t
  normalized_pusher_position(position_t pusher_position,
                             const Positions &excluded_positions = Positions()) const;
  ///
  /// Sets flag on all BoardCell in graph that are playable: reachable by any
  /// box or any pusher.
  ///
  void mark_play_area();

  ///
  /// Given movement path ``directions``, calculates position at the end of tha
  /// movement.
  ///
  position_t path_destination(position_t src, const Directions &directions_path) const;

  ///
  /// Resets all graph edges using board's tessellation.
  ///
  void reconfigure_edges();

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
