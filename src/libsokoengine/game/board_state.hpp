#ifndef BOARD_STATE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_STATE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <memory>

namespace sokoengine {
namespace game {

///
/// Sample of board state.
///
/// @sa
///   - BoardManager
///   - HashedBoardManager
///
class LIBSOKOENGINE_API BoardState {
public:
  ///
  /// Integer used for situations where board hash has not been calculated.
  ///
  static constexpr zobrist_key_t NO_HASH = 0;

  BoardState(
    const Positions &pushers_positions = Positions(),
    const Positions &boxes_positions   = Positions(),
    zobrist_key_t    zobrist_hash      = NO_HASH
  );
  BoardState(const BoardState &rv);
  BoardState(BoardState &&rv);
  BoardState &operator=(const BoardState &rv);
  BoardState &operator=(BoardState &&rv);
  ~BoardState();

  bool operator==(const BoardState &rv) const;
  bool operator!=(const BoardState &rv) const;

  ///
  /// Positions of pushers sorted by pusher ID.
  ///
  const Positions &pushers_positions() const;
  Positions       &pushers_positions();

  ///
  /// Positions of boxes sorted by pusher ID.
  ///
  const Positions &boxes_positions() const;
  Positions       &boxes_positions();

  ///
  /// Zobrist hash of state.
  ///
  /// @sa HashedBoardManager
  ///
  zobrist_key_t  zobrist_hash() const;
  zobrist_key_t &zobrist_hash();

  ///
  /// Pretty print object
  ///
  std::string str() const;
  ///
  /// Pretty print object
  ///
  std::string repr() const;

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
