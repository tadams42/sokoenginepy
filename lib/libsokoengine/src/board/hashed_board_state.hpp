#ifndef HASHED_BOARD_STATE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define HASHED_BOARD_STATE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "board_state.hpp"

#include <set>

namespace sokoengine {

///
/// Zobrist key storage.
///
typedef uint64_t zobrist_key_t;

///
/// Implements Zobrist hashing of BoardState
///
class LIBSOKOENGINE_API HashedBoardState : public BoardState
{
public:
  HashedBoardState(VariantBoard &board);
  HashedBoardState(const HashedBoardState &rv);
  HashedBoardState &operator=(const HashedBoardState &rv);
  HashedBoardState(HashedBoardState &&rv);
  HashedBoardState &operator=(HashedBoardState &&rv);
  virtual ~HashedBoardState();

  bool operator==(const HashedBoardState &rv) const;
  bool operator!=(const HashedBoardState &rv) const;

  zobrist_key_t boxes_layout_hash() const;
  zobrist_key_t boxes_and_pushers_layout_hash() const;
  zobrist_key_t external_position_hash(const positions_by_id_t& boxes_positions) const;

  virtual void set_boxorder(const std::string& rv) override;
  virtual void set_goalorder(const std::string& rv) override;

  virtual void enable_sokoban_plus() override;
  virtual void disable_sokoban_plus() override;

  virtual void switch_boxes_and_goals() override;

  bool is_solved() const;

  ///
  /// Hashes of all soulution box configurations.
  ///
  typedef std::set<zobrist_key_t> solution_hashes_t;
  const solution_hashes_t& solution_hashes() const;

  static std::string to_str(const solution_hashes_t& v);
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
