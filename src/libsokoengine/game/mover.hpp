#ifndef MOVER_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define MOVER_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include "pusher_step.hpp"

#include <deque>
#include <memory>
#include <stdexcept>

namespace sokoengine {
namespace game {

class BoardGraph;
class HashedBoardManager;

///
/// Movement mode of operation.
///
enum class LIBSOKOENGINE_API SolvingMode : uint8_t {
  FORWARD,
  REVERSE,
};

///
/// Exception.
///
class LIBSOKOENGINE_API NonPlayableBoardError : public std::runtime_error {
public:
  NonPlayableBoardError();
  virtual ~NonPlayableBoardError();
};

///
/// Exception.
///
class LIBSOKOENGINE_API IllegalMoveError : public std::runtime_error {
public:
  explicit IllegalMoveError(const std::string &mess);
  virtual ~IllegalMoveError();
};

///
/// Implements movement rules on BoardGraph.
///
class LIBSOKOENGINE_API Mover {
public:
  ///
  /// Ordered sequence of PusherStep.
  ///
  typedef std::deque<PusherStep> Moves;

  explicit Mover(BoardGraph &board, const SolvingMode &mode = SolvingMode::FORWARD);
  Mover(const Mover &) = delete;
  Mover(Mover &&rv);
  Mover &operator=(const Mover &) = delete;
  Mover &operator=(Mover &&rv);
  virtual ~Mover();

  const BoardGraph &board() const;
  SolvingMode solving_mode() const;
  const HashedBoardManager &board_manager() const;

  virtual void select_pusher(piece_id_t pusher_id);
  piece_id_t selected_pusher() const;

  virtual void jump(position_t new_position);
  virtual void move(const Direction &direction);

  virtual void undo_last_move();
  virtual const Moves &last_move() const;
  void set_last_move(const Moves &rv);

  bool pulls_boxes() const;
  void set_pulls_boxes(bool value);

protected:
  const BoardGraph &initial_board() const;

private:
  class LIBSOKOENGINE_LOCAL PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
