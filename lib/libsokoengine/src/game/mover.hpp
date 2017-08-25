#ifndef MOVER_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define MOVER_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"
#include "atomic_move.hpp"

#include <stdexcept>
#include <deque>
#include <memory>

namespace sokoengine {

class LIBSOKOENGINE_API VariantBoard;
class LIBSOKOENGINE_API Direction;
class LIBSOKOENGINE_API HashedBoardState;

enum class LIBSOKOENGINE_API SolvingMode : char {
  FORWARD,
  REVERSE,
};

class LIBSOKOENGINE_API NonPlayableBoardError: public std::runtime_error {
public:
  NonPlayableBoardError();
  virtual ~NonPlayableBoardError();
};

class LIBSOKOENGINE_API IllegalMoveError: public std::runtime_error {
public:
  IllegalMoveError(const std::string& mess);
  virtual ~IllegalMoveError();
};

class LIBSOKOENGINE_API Mover {
public:
  typedef std::deque<AtomicMove> Moves;

  Mover(VariantBoard& board, SolvingMode mode=SolvingMode::FORWARD);
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
