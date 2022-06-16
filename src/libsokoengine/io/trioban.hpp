#ifndef TRIOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TRIOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle.hpp"
#include "snapshot.hpp"

namespace sokoengine {
namespace io {

///
/// Snapshot implementation for Trioban
///
class LIBSOKOENGINE_API TriobanSnapshot : public Snapshot {
public:
  TriobanSnapshot();
  explicit TriobanSnapshot(const std::string &moves_data);
  TriobanSnapshot(const TriobanSnapshot &rv);
  TriobanSnapshot &operator=(const TriobanSnapshot &rv);
  TriobanSnapshot(TriobanSnapshot &&rv);
  TriobanSnapshot &operator=(TriobanSnapshot &&rv);
  virtual ~TriobanSnapshot();
  virtual unique_ptr_t clone() const override;
};

///
/// Board implementation for Trioban.
///
class LIBSOKOENGINE_API TriobanPuzzle : public Puzzle {
public:
  TriobanPuzzle();
  TriobanPuzzle(board_size_t width, board_size_t height);
  explicit TriobanPuzzle(const std::string &src);
  TriobanPuzzle(const TriobanPuzzle &rv);
  TriobanPuzzle &operator=(const TriobanPuzzle &rv);
  TriobanPuzzle(TriobanPuzzle &&rv);
  TriobanPuzzle &operator=(TriobanPuzzle &&rv);
  virtual ~TriobanPuzzle();
  virtual unique_ptr_t clone() const override;

  typedef std::vector<TriobanSnapshot> Snapshots;
  const Snapshots &snapshots() const;
  Snapshots &snapshots();

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
