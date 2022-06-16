#ifndef BOARD_MANAGER_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_MANAGER_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "config.hpp"

#include <map>
#include <stdexcept>
#include <memory>

namespace sokoengine {
namespace game {

class BoardGraph;
class BoardState;

///
/// @exception
///
class LIBSOKOENGINE_API CellAlreadyOccupiedError : public std::runtime_error {
public:
  explicit CellAlreadyOccupiedError(const std::string &mess);
  virtual ~CellAlreadyOccupiedError();
};

///
/// @exception
///
class LIBSOKOENGINE_API BoxGoalSwitchError : public std::runtime_error {
public:
  explicit BoxGoalSwitchError(const std::string &mess);
  virtual ~BoxGoalSwitchError();
};

///
/// Pieces' position, ID and Sokoban+ tracking.
/// Fast piece access.
///
class LIBSOKOENGINE_API BoardManager {
public:
  explicit BoardManager(BoardGraph &board, const std::string &boxorder = "",
                        const std::string &goalorder = "");
  BoardManager(const BoardManager &) = delete;
  BoardManager(BoardManager &&rv);
  BoardManager &operator=(const BoardManager &) = delete;
  BoardManager &operator=(BoardManager &&rv);
  virtual ~BoardManager();

  bool operator==(const BoardManager &rv) const;
  bool operator!=(const BoardManager &rv) const;

  ///
  /// Collection of piece IDs
  ///
  typedef std::vector<piece_id_t> piece_ids_vector_t;
  ///
  /// Mapping between piece's ID and its position
  ///
  typedef std::map<piece_id_t, position_t> positions_by_id_t;

  const BoardGraph &board() const;

  board_size_t pushers_count() const;
  piece_ids_vector_t pushers_ids() const;
  positions_by_id_t pushers_positions() const;
  position_t pusher_position(piece_id_t pusher_id) const;
  piece_id_t pusher_id_on(position_t position) const;
  bool has_pusher(piece_id_t pusher_id) const;
  bool has_pusher_on(position_t position) const;
  void move_pusher_from(position_t old_position, position_t to_new_position);
  void move_pusher(piece_id_t pusher_id, position_t to_new_position);

  board_size_t boxes_count() const;
  piece_ids_vector_t boxes_ids() const;
  positions_by_id_t boxes_positions() const;
  position_t box_position(piece_id_t box_id) const;
  piece_id_t box_id_on(position_t position) const;
  bool has_box(piece_id_t box_id) const;
  bool has_box_on(position_t position) const;
  void move_box_from(position_t old_position, position_t to_new_position);
  void move_box(piece_id_t box_id, position_t to_new_position);

  board_size_t goals_count() const;
  piece_ids_vector_t goals_ids() const;
  positions_by_id_t goals_positions() const;
  position_t goal_position(piece_id_t goal_id) const;
  piece_id_t goal_id_on(position_t position) const;
  bool has_goal(piece_id_t goal_id) const;
  bool has_goal_on(position_t position) const;

  const Positions &walls_positions() const;

  piece_id_t box_plus_id(piece_id_t box_id) const;
  piece_id_t goal_plus_id(piece_id_t goal_id) const;

  std::string boxorder() const;
  std::string goalorder() const;
  virtual void set_boxorder(const std::string &rv);
  virtual void set_goalorder(const std::string &rv);

  bool is_sokoban_plus_valid() const;
  bool is_sokoban_plus_enabled() const;
  virtual void enable_sokoban_plus();
  virtual void disable_sokoban_plus();

  ///
  /// All boxes configurations that are solution to board.
  ///
  typedef std::vector<BoardState> solutions_vector_t;
  solutions_vector_t solutions() const;

  virtual bool is_solved() const;
  virtual void switch_boxes_and_goals();
  bool is_playable() const;

  virtual std::string str() const;

  virtual BoardState state() const;

protected:
  virtual void pusher_moved(position_t old_position, position_t to_new_position);
  virtual void box_moved(position_t old_position, position_t to_new_position);

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
