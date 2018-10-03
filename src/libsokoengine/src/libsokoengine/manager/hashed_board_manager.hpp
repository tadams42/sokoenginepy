#ifndef HASHED_BOARD_MANAGER_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define HASHED_BOARD_MANAGER_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "board_manager.hpp"

#include <set>

namespace sokoengine {

///
/// Implements Zobrist hashing of BoardManager
///
class LIBSOKOENGINE_API HashedBoardManager : public BoardManager
{
public:
  explicit HashedBoardManager(
    VariantBoard& board, const std::string& boxorder="",
    const std::string& goalorder=""
  );
  HashedBoardManager(const HashedBoardManager&) = delete;
  HashedBoardManager(HashedBoardManager&& rv);
  HashedBoardManager& operator=(const HashedBoardManager&) = delete;
  HashedBoardManager& operator=(HashedBoardManager&& rv);
  virtual ~HashedBoardManager();

  bool operator==(const HashedBoardManager& rv) const;
  bool operator!=(const HashedBoardManager& rv) const;

  zobrist_key_t boxes_layout_hash() const;
  zobrist_key_t boxes_and_pushers_layout_hash() const;
  zobrist_key_t external_position_hash(const positions_by_id_t& boxes_positions) const;

  virtual void set_boxorder(const std::string& rv) override;
  virtual void set_goalorder(const std::string& rv) override;

  virtual void enable_sokoban_plus() override;
  virtual void disable_sokoban_plus() override;

  virtual void switch_boxes_and_goals() override;
  virtual BoardState state() const override;

  virtual bool is_solved() const override;

  ///
  /// Hashes of all solution box configurations.
  ///
  typedef std::set<zobrist_key_t> solutions_hashes_t;
  const solutions_hashes_t& solutions_hashes() const;

  virtual std::string str() const override;
  virtual std::string repr() const override;

protected:
  virtual void pusher_moved(position_t old_position, position_t to_new_position) override;
  virtual void box_moved(position_t old_position, position_t to_new_position) override;

private:
  class LIBSOKOENGINE_LOCAL PIMPL;
  std::unique_ptr<PIMPL>    m_impl;
};

} // namespace sokoengine

#endif // HEADER_GUARD
