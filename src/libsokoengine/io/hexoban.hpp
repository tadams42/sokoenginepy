#ifndef HEXOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define HEXOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle.hpp"
#include "snapshot.hpp"

namespace sokoengine {
namespace io {

///
/// Snapshot implementation for Hexoban
///
class LIBSOKOENGINE_API HexobanSnapshot : public Snapshot {
public:
  HexobanSnapshot();
  explicit HexobanSnapshot(const std::string &moves_data);
  HexobanSnapshot(const HexobanSnapshot &rv);
  HexobanSnapshot &operator=(const HexobanSnapshot &rv);
  HexobanSnapshot(HexobanSnapshot &&rv);
  HexobanSnapshot &operator=(HexobanSnapshot &&rv);
  virtual ~HexobanSnapshot();
  virtual unique_ptr_t clone() const override;
};

///
/// Board implementation for Hexoban.
///
class LIBSOKOENGINE_API HexobanPuzzle : public Puzzle {
public:
  HexobanPuzzle();
  HexobanPuzzle(board_size_t width, board_size_t height);
  explicit HexobanPuzzle(const std::string &src);
  HexobanPuzzle(const HexobanPuzzle &rv);
  HexobanPuzzle &operator=(const HexobanPuzzle &rv);
  HexobanPuzzle(HexobanPuzzle &&rv);
  HexobanPuzzle &operator=(HexobanPuzzle &&rv);
  virtual ~HexobanPuzzle();
  virtual unique_ptr_t clone() const override;

  typedef std::vector<HexobanSnapshot> Snapshots;
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
