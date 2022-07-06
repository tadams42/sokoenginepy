#ifndef SOKOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOKOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle.hpp"
#include "snapshot.hpp"

namespace sokoengine {
namespace io {

///
/// Snapshot implementation for game::Tessellation::SOKOBAN and
/// game::SokobanTessellation
///
class LIBSOKOENGINE_API SokobanSnapshot : public Snapshot {
public:
  SokobanSnapshot();
  ///
  /// @param moves pusher steps in textual representation.
  ///
  explicit SokobanSnapshot(const std::string &moves);
  SokobanSnapshot(const SokobanSnapshot &rv);
  SokobanSnapshot &operator=(const SokobanSnapshot &rv);
  SokobanSnapshot(SokobanSnapshot &&rv);
  SokobanSnapshot &operator=(SokobanSnapshot &&rv);
  virtual ~SokobanSnapshot();
  virtual unique_ptr_t clone() const override;
};

///
/// Puzzle implementation for game::Tessellation::SOKOBAN and
/// game::SokobanTessellation
///
class LIBSOKOENGINE_API SokobanPuzzle : public Puzzle {
public:
  SokobanPuzzle();
  ///
  /// @param width number of columns
  /// @param height number of rows
  ///
  SokobanPuzzle(board_size_t width, board_size_t height);
  ///
  /// @param board game board in textual representation.
  ///
  explicit SokobanPuzzle(const std::string &board);
  SokobanPuzzle(const SokobanPuzzle &rv);
  SokobanPuzzle &operator=(const SokobanPuzzle &rv);
  SokobanPuzzle(SokobanPuzzle &&rv);
  SokobanPuzzle &operator=(SokobanPuzzle &&rv);
  virtual ~SokobanPuzzle();
  virtual unique_ptr_t clone() const override;

  typedef std::vector<SokobanSnapshot> Snapshots;
  const Snapshots                     &snapshots() const;
  Snapshots                           &snapshots();

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace io
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
