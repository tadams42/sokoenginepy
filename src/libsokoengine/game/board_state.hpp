#ifndef BOARD_STATE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define BOARD_STATE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
/// @file

#include "numeric_types.hpp"

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
    const positions_t &pushers_positions = positions_t(),
    const positions_t &boxes_positions   = positions_t(),
    zobrist_key_t      zobrist_hash      = NO_HASH
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
  const positions_t &pushers_positions() const;
  positions_t       &pushers_positions();

  ///
  /// Positions of boxes sorted by pusher ID.
  ///
  const positions_t &boxes_positions() const;
  positions_t       &boxes_positions();

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

using game::BoardState;

} // namespace sokoengine

#endif // HEADER_GUARD
