#ifndef BOARD_STATE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_STATE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"
#include "direction.hpp"

#include <memory>
#include <vector>

namespace sokoengine {
namespace game {

///
/// Ordered collection of board positions usually describing continuous board
/// path.
///
typedef std::vector<position_t> Positions;

///
/// Ordered collection of Directions usually describing continuous board path.
///
typedef std::vector<Direction> Directions;

constexpr static const zobrist_key_t UNKNOWN_ZOBRIST_HASH = 0;

///
/// State snapshot.
///
class LIBSOKOENGINE_API BoardState {
public:
  BoardState(const Positions &pushers_positions = Positions(),
             const Positions &boxes_positions = Positions(),
             zobrist_key_t zobrist_hash = UNKNOWN_ZOBRIST_HASH);
  BoardState(const BoardState &rv);
  BoardState(BoardState &&rv);
  BoardState &operator=(const BoardState &rv);
  BoardState &operator=(BoardState &&rv);
  ~BoardState();

  bool operator==(const BoardState &rv) const;
  bool operator!=(const BoardState &rv) const;

  const Positions &pushers_positions() const;
  Positions &pushers_positions();

  const Positions &boxes_positions() const;
  Positions &boxes_positions();

  zobrist_key_t zobrist_hash() const;
  zobrist_key_t &zobrist_hash();

  std::string str() const;
  std::string repr() const;

private:
  class LIBSOKOENGINE_LOCAL PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
