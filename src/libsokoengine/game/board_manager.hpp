#ifndef BOARD_MANAGER_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_MANAGER_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <map>
#include <memory>
#include <stdexcept>

namespace sokoengine {
namespace game {

class BoardGraph;
class BoardState;

class LIBSOKOENGINE_API CellAlreadyOccupiedError : public std::invalid_argument {
public:
  explicit CellAlreadyOccupiedError(const std::string &mess);
  virtual ~CellAlreadyOccupiedError();
};

class LIBSOKOENGINE_API BoxGoalSwitchError : public std::invalid_argument {
public:
  explicit BoxGoalSwitchError(const std::string &mess);
  virtual ~BoxGoalSwitchError();
};

///
/// Selectors for PieceNotFoundError constructor
///
enum class LIBSOKOENGINE_API Selectors : int8_t { BOXES, GOALS, PUSHERS };

class LIBSOKOENGINE_API PieceNotFoundError : public std::invalid_argument {
public:
  PieceNotFoundError(Selectors piece, long id);
  PieceNotFoundError(Selectors piece, long position, char ignored);
  virtual ~PieceNotFoundError();
};

///
/// Memoizes, tracks and updates positions of all pieces.
///
/// - assigns and maintains piece IDs
/// - manages Sokoban+ piece IDs
/// - moves pieces while preserving their IDs
/// - checks if board is solved
///
/// BoardManager implements efficient means to inspect positions of pushers, boxes
/// and goals. To be able to do that, pieces must be uniquely identified.
/// BoardManager assigns unique numerical ID to each individual piece. This ID can
/// then be used to refer to that piece in various contexts.
///
/// How are piece IDs assigned? Start scanning game board from top left corner, going
/// row by row, from left to the right.  First encountered box will get `box.id =
/// Config::DEFAULT_ID`, second one `box.id = Config::DEFAULT_ID + 1`, etc... Same
/// goes for pushers and goals.
///
/// @image html assigning_ids.png
///
/// BoardManager also ensures that piece IDs remain unchanged when pieces are moved
/// on board. This is best illustrated by example. Let's construct a board with 2
/// boxes.
///
/// ```cpp
///   string data = string() +
///     "######\n" +
///     "#    #\n" +
///     "# $  #\n" +
///     "#  $.#\n" +
///     "#@ . #\n" +
///     "######\n";
///
///   SokobanPuzzle puzzle(data);
///   BoardGraph board(puzzle);
///   Mover mover(board);
///   BoardManager manager(board);
///
///   std::cout << '{';
///   for (auto p : manager.boxes_positions()) {
///     std::cout << p.first << ": " << p.second << ", ";
///   }
///   std::cout << '}' << std::endl;
///
///   // {1: 14, 2: 21, }
/// ```
///
/// We can edit the board (simulating movement of box ID 2) directly, without using
/// the manager. If we attach manager to that board after edit, we get expected but
/// wrong ID assigned to the box we'd just "moved":
///
/// ```cpp
///   board[21] = BoardCell(' ');
///   board[9] = BoardCell('$');
///
///   manager = BoardManager(board);
///
///   std::cout << manager.board().to_board_str(false) << std::endl;
///
///   std::cout << '{';
///   for (auto p : manager.boxes_positions()) {
///     std::cout << p.first << ": " << p.second << ", ";
///   }
///   std::cout << '}' << std::endl;
///
///   // ######
///   // #  $ #
///   // # $  #
///   // #   .#
///   // #@ . #
///   // ######
///   //
///   // {1: 9, 2: 14, }
/// ```
///
/// Moving box through manager (via move_box_from()) would've preserved ID of moved
/// box. Same goes for pushers.
///
/// | Initial board                  | Box edited without manager     | Box moved
/// through manager      | | ------------------------------ |
/// ------------------------------ | ------------------------------ | |
/// ![](movement_vs_transfer1.png) | ![](movement_vs_transfer2.png) |
/// ![](movement_vs_transfer3.png) |
///
/// @note
/// Movement methods in BoardManager only implement board updates. They don't
/// implement full game logic. For game logic see Mover.
///
/// @sa
///   - Mover
///   - SokobanPlus
///   - BoardState
///
class LIBSOKOENGINE_API BoardManager {
public:
  ///
  /// @param board board to manage
  /// @param boxorder Sokoban+ data (see SokobanPlus)
  /// @param goalorder Sokoban+ data (see SokobanPlus)
  ///
  explicit BoardManager(
    BoardGraph        &board,
    const std::string &boxorder  = "",
    const std::string &goalorder = ""
  );
  BoardManager(const BoardManager &)            = delete;
  BoardManager &operator=(const BoardManager &) = delete;
  BoardManager(BoardManager &&rv);
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

  // --------------------------------------------------------------------------
  // Pushers
  // --------------------------------------------------------------------------

  board_size_t       pushers_count() const;
  piece_ids_vector_t pushers_ids() const;
  ///
  /// Mapping of pushers' IDs to the corresponding board positions, ie.
  ///
  ///    {1: 42, 2: 24}
  ///
  positions_by_id_t pushers_positions() const;
  ///
  /// @throws PieceNotFoundError No pusher with ID `pusher_id`
  ///
  position_t pusher_position(piece_id_t pusher_id) const;
  ///
  /// @throws PieceNotFoundError No pusher on `position`
  ///
  piece_id_t pusher_id_on(position_t position) const;
  bool       has_pusher(piece_id_t pusher_id) const;
  bool       has_pusher_on(position_t position) const;
  ///
  /// Updates board state and board cells with changed pusher position.
  ///
  /// @throws PieceNotFoundError there is no pusher on `old_position`
  /// @throws CellAlreadyOccupiedError there is an obstacle (wall/box/another pusher)
  /// on
  ///         `to_new_position`
  /// @throws InvalidPositionError `old_position` or `to_new_position` is of board
  ///
  void move_pusher_from(position_t old_position, position_t to_new_position);
  ///
  /// Updates board state and board cells with changed pusher position.
  ///
  /// @throws PieceNotFoundError there is no pusher on `old_position`
  /// @throws CellAlreadyOccupiedError there is an obstacle (wall/box/another pusher)
  /// on
  ///         `to_new_position`
  /// @throws InvalidPositionError `to_new_position` is of board
  ///
  /// @note
  /// Allows placing a pusher onto position occupied by box. This is for cases when we
  /// switch box/goals positions in reverse solving mode. In this situation it is
  /// legal for pusher to end up standing on top of the box. Game rules say that for
  /// these situations, first move(s) must be jumps.
  ///
  /// @warning
  /// It doesn't verify if `to_new_position` is valid on-board position.
  ///
  void move_pusher(piece_id_t pusher_id, position_t to_new_position);

  // --------------------------------------------------------------------------
  // Boxes
  // --------------------------------------------------------------------------

  board_size_t       boxes_count() const;
  piece_ids_vector_t boxes_ids() const;
  ///
  /// Mapping of boxes' IDs to the corresponding board positions, ie.
  ///
  ///    {1: 42, 2: 24}
  ///
  positions_by_id_t boxes_positions() const;
  ///
  /// @throws PieceNotFoundError No box with ID `box_id`
  ///
  position_t box_position(piece_id_t box_id) const;
  ///
  /// @throws PieceNotFoundError No box on `position`
  ///
  piece_id_t box_id_on(position_t position) const;
  bool       has_box(piece_id_t box_id) const;
  bool       has_box_on(position_t position) const;
  ///
  /// Updates board state and board cells with changed box position.
  ///
  /// @throws PieceNotFoundError there is no box on `old_position`
  /// @throws CellAlreadyOccupiedError there is an obstacle (wall/box/pusher) on
  ///         `to_new_position`
  /// @throws InvalidPositionError `old_position` or `to_new_position` is of board
  ///
  void move_box_from(position_t old_position, position_t to_new_position);
  ///
  /// Updates board state and board cells with changed box position.
  ///
  /// @throws PieceNotFoundError there is no pusher on `old_position`
  /// @throws CellAlreadyOccupiedError there is an obstacle (wall/box/pusher) on
  ///         `to_new_position`
  /// @throws InvalidPositionError `to_new_position` is of board
  ///
  void move_box(piece_id_t box_id, position_t to_new_position);

  // --------------------------------------------------------------------------
  // Goals
  // --------------------------------------------------------------------------

  board_size_t       goals_count() const;
  piece_ids_vector_t goals_ids() const;
  ///
  /// Mapping of goals' IDs to the corresponding board positions, ie.
  ///
  ///    {1: 42, 2: 24}
  ///
  positions_by_id_t goals_positions() const;
  ///
  /// @throws PieceNotFoundError No goal with ID `goal_id`
  ///
  position_t goal_position(piece_id_t goal_id) const;
  ///
  /// @throws PieceNotFoundError No goal on `position`
  ///
  piece_id_t goal_id_on(position_t position) const;
  bool       has_goal(piece_id_t goal_id) const;
  bool       has_goal_on(position_t position) const;

  // --------------------------------------------------------------------------
  // Sokoban+
  // --------------------------------------------------------------------------

  ///
  /// Get Sokoban+ ID for box.
  ///
  /// @returns
  /// If Sokoban+ is enabled returns Sokoban+ ID of a box. If not, returns
  /// DEFAULT_PLUS_ID
  ///
  /// @throws PieceNotFoundError No box with ID `box_id`, but only if i Sokoban+ is
  /// enabled
  ///
  /// @sa SokobanPlus::box_plus_id()
  ///
  piece_id_t box_plus_id(piece_id_t box_id) const;
  ///
  /// Get Sokoban+ ID for goal.
  ///
  /// @returns
  /// If Sokoban+ is enabled returns Sokoban+ ID of a goal. If not, returns
  /// DEFAULT_PLUS_ID
  ///
  /// @throws PieceNotFoundError No goal with ID `goal_id`, but only if i Sokoban+ is
  /// enabled
  ///
  /// @sa SokobanPlus::goal_plus_id()
  ///
  piece_id_t goal_plus_id(piece_id_t goal_id) const;
  ///
  /// @sa SokobanPlus::boxorder()
  ///
  std::string boxorder() const;
  ///
  /// @sa SokobanPlus::goalorder()
  ///
  std::string goalorder() const;
  ///
  /// If `rv` is different from existing `boxorder`, disables Sokoban+ and sets
  /// boxorder to new value.
  ///
  /// @sa SokobanPlus::set_boxorder()
  ///
  virtual void set_boxorder(const std::string &rv);
  ///
  /// If `rv` is different from existing `goalorder`, disables Sokoban+ and sets
  /// goalorder to new value.
  ///
  /// @sa SokobanPlus::set_goalorder()
  ///
  virtual void set_goalorder(const std::string &rv);

  ///
  /// Validates current set of Sokoban+ rules.
  ///
  /// @sa enable_sokoban_plus()
  ///
  bool is_sokoban_plus_valid() const;

  ///
  /// Are Sokoban+ rule enabled for current game?
  ///
  /// @sa enable_sokoban_plus()
  ///
  bool is_sokoban_plus_enabled() const;

  ///
  /// Enables using Sokoban+ rules for this board.
  ///
  /// Enabling these, changes victory condition for given board (return value of
  /// is_solved() ).
  ///
  /// @sa SokobanPlus.enable()
  ///
  /// @throws SokobanPlusDataError Trying to enable invalid Sokoban+
  ///
  virtual void enable_sokoban_plus();

  ///
  /// Disables using Sokoban+ rules for this board.
  ///
  /// Disabling these, changes victory condition for given board (return value of
  /// is_solved() ).
  ///
  /// @sa SokobanPlus.disable()
  ///
  virtual void disable_sokoban_plus();

  // --------------------------------------------------------------------------
  // Board state
  // --------------------------------------------------------------------------

  const BoardGraph &board() const;
  const Positions  &walls_positions() const;

  ///
  /// All boxes configurations that are solution to board.
  ///
  typedef std::vector<BoardState> solutions_vector_t;

  ///
  /// All configurations of boxes that result in solved board.
  ///
  /// Result depends on is_sokoban_plus_enabled()
  ///
  solutions_vector_t solutions() const;

  ///
  /// Checks for game victory.
  ///
  /// 1. `Classic` victory is any board position in which each box is positioned on
  /// top
  ///    of each goal
  /// 2. `Sokoban+` victory is board position where each box is positioned on top of
  ///    each goal with the same Sokoban+ ID as that box
  ///
  /// Result depends on is_sokoban_plus_enabled().
  ///
  virtual bool is_solved() const;

  ///
  /// Switches positions of boxes and goals pairs. This is used by Mover in
  /// SolvingMode::REVERSE.
  ///
  /// @throws BoxGoalSwitchError: when board can't be switched. These kinds of boards
  /// are usually also not is_playable()
  ///
  virtual void switch_boxes_and_goals();

  ///
  /// Checks minimal requirements for board to be playable.
  ///
  bool is_playable() const;

  ///
  /// Pretty print object
  ///
  virtual std::string str() const;

  ///
  /// Snapshots current board state.
  ///
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
