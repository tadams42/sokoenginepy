#ifndef MOVER_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define MOVER_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"
#include "atomic_move.hpp"

#include <stdexcept>
#include <deque>
#include <memory>

namespace sokoengine {

class VariantBoard;
class Direction;
class HashedBoardState;

///
/// Movement mode of operation.
///
enum class LIBSOKOENGINE_API SolvingMode : char {
  FORWARD,
  REVERSE,
};

///
/// Exception.
///
class LIBSOKOENGINE_API NonPlayableBoardError: public std::runtime_error {
public:
  NonPlayableBoardError();
  virtual ~NonPlayableBoardError();
};

///
/// Exception.
///
class LIBSOKOENGINE_API IllegalMoveError: public std::runtime_error {
public:
  IllegalMoveError(const std::string& mess);
  virtual ~IllegalMoveError();
};

///
/// Implements movement rules on VariantBoard.
///
class LIBSOKOENGINE_API Mover {
public:
  ///
  /// Ordered sequence of AtomicMove.
  ///
  typedef std::deque<AtomicMove> Moves;

  Mover(VariantBoard& board, const SolvingMode& mode=SolvingMode::FORWARD);
  Mover(const Mover& rv);
  Mover& operator=(const Mover& rv);
  Mover(Mover&& rv);
  Mover& operator=(Mover&& rv);
  virtual ~Mover();

  const VariantBoard& board() const;
  SolvingMode solving_mode() const;
  const HashedBoardState& state() const;

  virtual void select_pusher(piece_id_t pusher_id);
  piece_id_t selected_pusher() const;

  virtual void jump(position_t new_position);
  virtual void move(const Direction& direction);

  virtual void undo_last_move();
  virtual const Moves& last_move() const;
  void set_last_move(const Moves& rv);

  bool pulls_boxes() const;
  void set_pulls_boxes(bool value);

protected:
  const VariantBoard& initial_board() const;

private:
  class LIBSOKOENGINE_LOCAL PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace sokoengine

#endif // HEADER_GUARD
