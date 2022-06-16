#ifndef HASHED_BOARD_MANAGER_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define HASHED_BOARD_MANAGER_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "board_manager.hpp"

#include <set>

namespace sokoengine {
namespace game {

///
/// Implements Zobrist hashing of BoardManager
///
class LIBSOKOENGINE_API HashedBoardManager : public BoardManager {
public:
  explicit HashedBoardManager(BoardGraph &board, const std::string &boxorder = "",
                              const std::string &goalorder = "");
  HashedBoardManager(const HashedBoardManager &) = delete;
  HashedBoardManager(HashedBoardManager &&rv);
  HashedBoardManager &operator=(const HashedBoardManager &) = delete;
  HashedBoardManager &operator=(HashedBoardManager &&rv);
  virtual ~HashedBoardManager();

  bool operator==(const HashedBoardManager &rv) const;
  bool operator!=(const HashedBoardManager &rv) const;

  zobrist_key_t state_hash() const;
  zobrist_key_t initial_state_hash() const;
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
  virtual void pusher_moved(position_t old_position,
                            position_t to_new_position) override;
  virtual void box_moved(position_t old_position, position_t to_new_position) override;

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
