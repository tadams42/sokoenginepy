#ifndef MOVER_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define MOVER_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <memory>
#include <stdexcept>

namespace sokoengine {
namespace game {

class BoardGraph;
class HashedBoardManager;
class PusherStep;

///
/// Movement mode of operation.
///
enum class LIBSOKOENGINE_API SolvingMode : uint8_t {
  ///
  /// Forward solving mode
  ///
  /// - pusher is allowed to push single box at the time
  /// - pusher can't pull boxes
  /// - pusher can't jump over boxes or walls
  ///
  FORWARD,

  ///
  /// Reverse solving mode
  ///
  /// - pusher is allowed to pull single box at the time
  ///   - if position allows pull that pull is optional (pusher is allowed to move
  ///     without pull even if pull is possible).
  ///   - default behavior is to always pull boxes but that can be changed any time
  ///     through `Mover.pulls_boxes`
  /// - pusher can't push boxes
  /// - pusher is allowed to jump over boxes and walls
  ///   - jumps are allowed only before first pull is done
  /// - board starts in solved state: positions of boxes and goals are switched
  /// - when boxes and goals are switched, pusher might end up "standing on box".
  ///   In this situation, fist move in game must be jump.
  ///
  REVERSE,
};

class LIBSOKOENGINE_API NonPlayableBoardError : public std::invalid_argument {
public:
  NonPlayableBoardError();
  virtual ~NonPlayableBoardError();
};

class LIBSOKOENGINE_API IllegalMoveError : public std::invalid_argument {
public:
  explicit IllegalMoveError(const std::string &mess);
  virtual ~IllegalMoveError();
};

///
/// Ordered sequence of PusherStep.
///
typedef std::vector<PusherStep> PusherSteps;

///
/// Implements game rules (on-board movement). Supports forward and reverse game
/// solving mode.
///
/// **History management**
///
/// Mover only stores last performed move in history and it doesn't offer redo. Failed
/// moves, undo and non-moves (ie. selecting already selected pusher or jumping on
/// same position pusher is already standing on) clear undo history.
///
class LIBSOKOENGINE_API Mover {
public:
  ///
  /// @throws NonPlayableBoardError when attaching mover to non playable board (see
  ///         BoardManager::is_playable)
  ///
  explicit Mover(BoardGraph &board, SolvingMode mode = SolvingMode::FORWARD);
  Mover(const Mover &) = delete;
  Mover(Mover &&rv);
  Mover &operator=(const Mover &) = delete;
  Mover &operator=(Mover &&rv);
  virtual ~Mover();

  const BoardGraph         &board() const;
  SolvingMode               solving_mode() const;
  const HashedBoardManager &board_manager() const;

  ///
  /// ID of pusher that will perform next move.
  ///
  piece_id_t selected_pusher() const;

  ///
  /// Selects pusher that will perform next move. If this pusher is already selected,
  /// does nothing.
  ///
  /// From current position, generates sequence of steps needed to select pusher_id
  /// and stores them into last_move(). Sets internal selected pusher_id to newly
  /// selected pusher
  ///
  /// Mover initially always selects Config::DEFAULT_ID. This means that for
  /// single-pusher boards, single pusher is always automatically selected and this
  /// method doesn't need to be called.
  ///
  /// @throws PieceNotFoundError no pusher wih ``pusher_id``
  ///
  virtual void select_pusher(piece_id_t pusher_id);

  ///
  /// Currently selected pusher jumps to `new_position`.
  ///
  /// Fails if:
  ///
  /// - Mover is in SolvingMode::FORWARD mode
  /// - pusher can't be dropped on `new_position`
  /// - first pull had been made
  ///
  /// @throws IllegalMoveError for illegal moves
  /// @throws InvalidPositionError `new_position` is off board
  ///
  virtual void jump(position_t new_position);

  ///
  /// Moves currently selected pusher in direction.
  ///
  /// In SolvingMode::FORWARD mode, pushes the box in front of pusher (if there
  /// is one).
  ///
  /// In SolvingMode::REVERSE mode pulls box together with pusher (if there is
  /// one and if pulls_boxes() is `true`).
  ///
  /// @throws IllegalMoveError for illegal jumps
  ///
  virtual void move(const Direction &direction);

  ///
  /// Sequence of PusherStep that contains most recent movement.
  ///
  /// Whenever Mover performs any movement or pusher selection, it puts resulting
  /// PusherStep into this sequence in order pusher steps happened.
  ///
  /// This is useful for movement animation in GUI. After Mover performs movement, GUI
  /// has enough information to know what was performed and to choose which animations
  /// to render for that.
  ///
  /// It is also possible to set this to some external sequence of moves. In that
  /// case, calling undo_last_move() will cause Mover to try to undo that external
  /// sequence of pusher steps.
  ///
  /// Example:
  ///
  /// ```cpp
  /// include <sokoengine.hpp>
  /// #include <iostream>
  ///
  /// using namespace sokoengine::game;
  /// using namespace sokoengine::io;
  /// using namespace std;
  ///
  /// int main() {
  ///   string data =
  ///     string() +
  ///     "    #####\n" +
  ///     "    #  @#\n" +
  ///     "    #$  #\n" +
  ///     "  ###  $##\n" +
  ///     "  #  $ $ #\n" +
  ///     "### # ## #   ######\n" +
  ///     "#   # ## #####  ..#\n" +
  ///     "# $  $          ..#\n" +
  ///     "##### ### #@##  ..#\n" +
  ///     "    #     #########\n" +
  ///     "    #######\n"
  ///   ;
  ///
  ///   SokobanPuzzle puzzle(data);
  ///   BoardGraph board(puzzle);
  ///   Mover mover(board);
  ///
  ///   PusherSteps last_move {PusherStep(Direction::UP),
  ///   PusherStep(Direction::RIGHT)}; mover.set_last_move(last_move);
  ///   mover.undo_last_move();
  ///
  ///   cout << mover.board().to_board_str(false) << endl;
  ///   //    #####
  ///   //    #   #
  ///   //    #$@ #
  ///   //  ###  $##
  ///   //  #  $ $ #
  ///   // ### # ## #   ######
  ///   // #   # ## #####  ..#
  ///   // # $  $          ..#
  ///   // ##### ### #@##  ..#
  ///   //     #     #########
  ///   //     #######
  ///
  ///   cout << '{' << endl;
  ///   for (auto step : mover.last_move()) { cout << "    " << step.repr() << ',' <<
  ///   endl; } cout << '}' << endl;
  ///   // {
  ///   //     PusherStep(Direction.LEFT)
  ///   //     PusherStep(Direction.DOWN)
  ///   // }
  ///
  ///   return 0;
  /// }
  /// ```
  ///
  /// @warning
  /// Subsequent movement overwrites this, meaning that Mover can only undo last move
  /// performed (it doesn't keep whole history of movement, only the last performed
  /// move).
  ///
  virtual const PusherSteps &last_move() const;
  void                       set_last_move(const PusherSteps &rv);

  ///
  /// Takes sequence of moves stored in last_move() and tries to undo it.
  ///
  /// @throws IllegalMoveError
  ///
  virtual void undo_last_move();

  ///
  /// Select behavior in SolvingMode::REVERSE mode when pusher is moving away from
  /// box.
  ///
  void set_pulls_boxes(bool value);
  bool pulls_boxes() const;

protected:
  const BoardGraph &initial_board() const;

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
