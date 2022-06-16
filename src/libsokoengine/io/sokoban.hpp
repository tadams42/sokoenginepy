#ifndef SOKOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOKOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle.hpp"
#include "snapshot.hpp"

namespace sokoengine {
namespace io {

///
/// Snapshot implementation for Sokoban
///
class LIBSOKOENGINE_API SokobanSnapshot : public Snapshot {
public:
  SokobanSnapshot();
  explicit SokobanSnapshot(const std::string &moves_data);
  SokobanSnapshot(const SokobanSnapshot &rv);
  SokobanSnapshot &operator=(const SokobanSnapshot &rv);
  SokobanSnapshot(SokobanSnapshot &&rv);
  SokobanSnapshot &operator=(SokobanSnapshot &&rv);
  virtual ~SokobanSnapshot();
  virtual unique_ptr_t clone() const override;
};

///
/// Board implementation for Sokoban.
///
class LIBSOKOENGINE_API SokobanPuzzle : public Puzzle {
public:
  SokobanPuzzle();
  SokobanPuzzle(board_size_t width, board_size_t height);
  explicit SokobanPuzzle(const std::string &src);
  SokobanPuzzle(const SokobanPuzzle &rv);
  SokobanPuzzle &operator=(const SokobanPuzzle &rv);
  SokobanPuzzle(SokobanPuzzle &&rv);
  SokobanPuzzle &operator=(SokobanPuzzle &&rv);
  virtual ~SokobanPuzzle();
  virtual unique_ptr_t clone() const override;

  typedef std::vector<SokobanSnapshot> Snapshots;
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
