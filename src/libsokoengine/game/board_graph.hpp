#ifndef BOARD_GRAPH_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_GRAPH_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <memory>
#include <stdexcept>

namespace sokoengine {

namespace io {
class Puzzle;
} // namespace io

namespace game {

class BoardCell;

class LIBSOKOENGINE_API InvalidPositionError : public std::out_of_range {
public:
  InvalidPositionError(long position);
  virtual ~InvalidPositionError();
};

struct LIBSOKOENGINE_API Edge {
public:
  position_t u;
  position_t v;
  Direction  direction;

  explicit Edge(
    position_t u         = Config::NO_POS,
    position_t v         = Config::NO_POS,
    Direction  direction = Direction::LEFT
  );

  bool operator==(const Edge &rv) const;
  bool operator!=(const Edge &rv) const;

  std::string str() const;
  std::string repr() const;
};

typedef std::vector<Edge> Edges;

///
/// Board graph implementation (using Boost::Graph under the hood).
///
class LIBSOKOENGINE_API BoardGraph {
public:
  ///
  /// @throws std::range_error when puzzle width is greater than Config::MAX_WIDTH
  ///         or puzzle.height() is greater than Config::MAX_HEIGHT
  ///
  explicit BoardGraph(const io::Puzzle &puzzle);
  BoardGraph(const BoardGraph &rv);
  BoardGraph &operator=(const BoardGraph &rv);
  BoardGraph(BoardGraph &&rv);
  BoardGraph &operator=(BoardGraph &&rv);
  virtual ~BoardGraph();

  ///
  /// @throws InvalidPositionError when `position` is off board
  ///
  const BoardCell &cell_at(position_t position) const;
  ///
  /// @throws InvalidPositionError when `position` is off board
  ///
  BoardCell &cell_at(position_t position);

  ///
  /// @warning Doesn't validate if `src` is on board position.
  ///
  const BoardCell &cell(position_t position) const;

  ///
  /// @warning Doesn't validate if `src` is on board position.
  ///
  BoardCell &cell(position_t position);

  ///
  /// @warning Doesn't validate if `src` is on board position.
  ///
  const BoardCell &operator[](position_t position) const;

  ///
  /// @warning Doesn't validate if `src` is on board position.
  ///
  BoardCell &operator[](position_t position);

  Tessellation        tessellation() const;
  io::CellOrientation cell_orientation(position_t position) const;

  ///
  /// Formatted string representation of board.
  ///
  std::string
  to_board_str(bool use_visible_floor = false, bool rle_encode = false) const;

  ///
  /// Same as to_board_str() but with hardcoded defaults.
  ///
  std::string str() const;

  bool         contains(position_t position) const;
  board_size_t size() const;
  board_size_t edges_count() const;
  board_size_t board_width() const;
  board_size_t board_height() const;

  ///
  /// Edges inspector, for debugging purposes
  ///
  /// @throws InvalidPositionError when `src` is off board
  ///
  Edges out_edges(position_t src) const;

  ///
  /// Neighbor position in `direction`.
  ///
  /// @returns Target position or Config::NO_POS
  ///
  /// @warning Doesn't validate if `src` is on board position.
  ///
  position_t neighbor(position_t src, const Direction &direction) const;

  ///
  /// Neighbor position in `direction`.
  ///
  /// @returns Target position or Config::NO_POS
  ///
  /// @throws InvalidPositionError when `src` is off board
  ///
  position_t neighbor_at(position_t src, const Direction &direction) const;

  ///
  /// @throws InvalidPositionError when `src` is off board
  ///
  Positions wall_neighbors(position_t src) const;

  ///
  /// @throws InvalidPositionError when `src` is off board
  ///
  Directions wall_neighbor_directions(position_t src) const;

  ///
  /// @throws InvalidPositionError when `src` is off board
  ///
  Positions all_neighbors(position_t src) const;

  ///
  /// Calculates shortest path between two positions with all positions having equal
  /// weight.
  ///
  /// @throws InvalidPositionError when `src` or `dst` are off board
  ///
  Positions shortest_path(position_t src, position_t dst) const;

  ///
  /// Calculates shortest path between two positions not passing through board
  /// obstacles (walls, boxes, other pushers, etc...).
  ///
  /// @throws InvalidPositionError when `src` or `dst` are off board
  ///
  Positions dijkstra_path(position_t src, position_t dst) const;

  ///
  /// Finds list of positions through which pusher must pass when moving without
  /// pushing boxes
  ///
  /// @throws InvalidPositionError when `src` or `dst` are off board
  ///
  Positions find_move_path(position_t src, position_t dst) const;

  ///
  /// Finds list of positions through which pusher must pass when jumping
  ///
  /// @throws InvalidPositionError when `src` or `dst` are off board
  ///
  Positions find_jump_path(position_t src, position_t dst) const;

  ///
  /// Converts path expressed as positions to one expressed as :class:`.Direction`.
  ///
  /// @throws InvalidPositionError Any position in `positions` is off board
  ///
  Directions positions_path_to_directions_path(const Positions &positions) const;

  ///
  /// Given movement path `directions`, calculates target position at the end of that
  /// movement.
  ///
  /// If any direction in `directions` would've lead off board, stops the search and
  /// returns position reached up to that point.
  ///
  /// @throws InvalidPositionError when `src` is off board
  ///
  position_t path_destination(position_t src, const Directions &directions) const;

  ///
  /// Finds all positions that are reachable by pusher standing on `pusher_position`.
  ///
  /// Doesn't require that ``pusher_position`` actually has pusher.
  ///
  /// @throws InvalidPositionError when `pusher_position` is off board. Doesn't throw
  /// if
  ///         any position in `excluded_positions` is off board; it simply ignores
  ///         those
  ///
  Positions positions_reachable_by_pusher(
    position_t pusher_position, const Positions &excluded_positions = Positions()
  ) const;

  ///
  /// Finds top-left position reachable by pusher without pushing any boxes.
  ///
  /// Doesn't require that ``pusher_position`` actually has pusher.
  ///
  /// @throws InvalidPositionError when `pusher_position` is off board. Doesn't throw
  /// if
  ///         any position in `excluded_positions` is off board; it simply ignores
  ///         those
  ///
  position_t normalized_pusher_position(
    position_t pusher_position, const Positions &excluded_positions = Positions()
  ) const;

  ///
  /// Sets flag on all BoardCell in graph that are playable: reachable by any box or
  /// any pusher.
  ///
  void mark_play_area();

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
