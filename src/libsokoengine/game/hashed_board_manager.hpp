#ifndef HASHED_BOARD_MANAGER_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define HASHED_BOARD_MANAGER_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "board_manager.hpp"

#include <set>

namespace sokoengine {
namespace game {

///
/// Board manager that also manages Zobrist hashing.
///
/// Adds Zobrist hashing on top of BoardManager and keeps it up to date when
/// pieces are moved.
///
/// Zobrist hash is 64b integer hash derived from positions of all boxes and pushers
/// on board.
///
/// This hash is "resistant" to moving board pieces. Moving one pusher and box will
/// change board hash. Undoing that move will return hash to previous value.
///
/// This kind of hash is reliable way for identifying board positions. Sokoban solvers
/// might need this to operate.
///
/// When hashing, boxes with same Sokoban+ ID are treated as equal meaning that if two
/// of these boxes switch position, hash will not change. This also means that for the
/// same board, hash is different when Sokoban+ is enabled from the one when it is
/// disabled.
///
/// Pushers are all treated equal, meaning that if two pushers switch position, hash
/// will not change
///
/// @note
/// - enabling/disabling Sokoban+ rehashes the board state
/// - moving pieces doesn't need to re-hash whole board, it updates hash incrementally
/// - undoing piece movement also updates hash incrementally with additional feature
///   that returning to previous board state will return to previous hash value
///
class LIBSOKOENGINE_API HashedBoardManager : public BoardManager {
public:
  explicit HashedBoardManager(
    BoardGraph        &board,
    const std::string &boxorder  = "",
    const std::string &goalorder = ""
  );
  HashedBoardManager(const HashedBoardManager &) = delete;
  HashedBoardManager(HashedBoardManager &&rv);
  HashedBoardManager &operator=(const HashedBoardManager &) = delete;
  HashedBoardManager &operator=(HashedBoardManager &&rv);
  virtual ~HashedBoardManager();

  bool operator==(const HashedBoardManager &rv) const;
  bool operator!=(const HashedBoardManager &rv) const;

  ///
  /// Zobrist hash of current board state.
  ///
  zobrist_key_t state_hash() const;

  ///
  /// Zobrist hash of initial board state (before any movement happened).
  ///
  zobrist_key_t initial_state_hash() const;

  ///
  /// Calculates Zobrist hash of given `board_state` as if that `board_state` was
  /// applied to initial `board` (to board where no movement happened).
  ///
  /// `board_state` must meet following requirement:
  ///
  /// ```cpp
  /// board_state.boxes_positions().size() == this->boxes_count()
  /// && board_state.boxes_positions().size() == this->goals_count()
  /// ```
  ///
  /// @returns value of hash or BoardState::NO_HASH if it can't be calculated
  ///
  zobrist_key_t external_state_hash(BoardState &board_state) const;

  virtual void set_boxorder(const std::string &rv) override;
  virtual void set_goalorder(const std::string &rv) override;

  virtual void enable_sokoban_plus() override;
  virtual void disable_sokoban_plus() override;

  virtual BoardState state() const override;

  virtual bool is_solved() const override;

  ///
  /// Hashes of all solution box configurations.
  ///
  typedef std::set<zobrist_key_t> solutions_hashes_t;

  const solutions_hashes_t &solutions_hashes() const;

  virtual std::string str() const override;

protected:
  virtual void
  pusher_moved(position_t old_position, position_t to_new_position) override;
  virtual void box_moved(position_t old_position, position_t to_new_position) override;

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
