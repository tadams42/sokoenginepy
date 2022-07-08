#ifndef OCTOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define OCTOBAN_PUZZLE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "puzzle.hpp"
#include "snapshot.hpp"

namespace sokoengine {
namespace io {

///
/// Snapshot implementation for game::Tessellation::OCTOBAN and
/// game::OctobanTessellation
///
class LIBSOKOENGINE_API OctobanSnapshot : public Snapshot {
public:
  OctobanSnapshot();
  ///
  /// @param moves pusher steps in textual representation.
  ///
  explicit OctobanSnapshot(const std::string &moves);
  OctobanSnapshot(const OctobanSnapshot &rv);
  OctobanSnapshot &operator=(const OctobanSnapshot &rv);
  OctobanSnapshot(OctobanSnapshot &&rv);
  OctobanSnapshot &operator=(OctobanSnapshot &&rv);
  virtual ~OctobanSnapshot();
  virtual unique_ptr_t clone() const override;
};

///
/// Puzzle implementation for game::Tessellation::HEXOBAN and
/// game::OctobanTessellation
///
class LIBSOKOENGINE_API OctobanPuzzle : public Puzzle {
public:
  OctobanPuzzle();
  ///
  /// @param width number of columns
  /// @param height number of rows
  ///
  OctobanPuzzle(board_size_t width, board_size_t height);
  ///
  /// @param board game board in textual representation.
  ///
  explicit OctobanPuzzle(const std::string &board);
  OctobanPuzzle(const OctobanPuzzle &rv);
  OctobanPuzzle &operator=(const OctobanPuzzle &rv);
  OctobanPuzzle(OctobanPuzzle &&rv);
  OctobanPuzzle &operator=(OctobanPuzzle &&rv);
  virtual ~OctobanPuzzle();
  virtual unique_ptr_t clone() const override;

  typedef std::vector<OctobanSnapshot> Snapshots;
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
