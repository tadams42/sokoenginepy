#include "sokoban.hpp"

using namespace std;

namespace sokoengine {
namespace io {

using game::Tessellation;

namespace implementation {

LIBSOKOENGINE_LOCAL const PuzzleResizer &sb_static_resizer() {
  static const PuzzleResizer the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzleParser &sb_static_parser() {
  static const PuzzleParser the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzlePrinter &sb_static_printer() {
  static const PuzzlePrinter the_one;
  return the_one;
}

} // namespace implementation

using namespace implementation;

class LIBSOKOENGINE_LOCAL SokobanPuzzle::PIMPL {
public:
  Snapshots m_snapshots;
};

SokobanPuzzle::SokobanPuzzle() : SokobanPuzzle(0, 0) {}

SokobanPuzzle::SokobanPuzzle(board_size_t width, board_size_t height)
  : Puzzle(Tessellation::SOKOBAN, sb_static_resizer(), sb_static_parser(),
           sb_static_printer(), width, height),
    m_impl(make_unique<PIMPL>()) {}

SokobanPuzzle::SokobanPuzzle(const string &src)
  : Puzzle(Tessellation::SOKOBAN, sb_static_resizer(), sb_static_parser(),
           sb_static_printer(), src),
    m_impl(make_unique<PIMPL>()) {}

SokobanPuzzle::SokobanPuzzle(const SokobanPuzzle &rv)
  : Puzzle(rv), m_impl(make_unique<PIMPL>(*rv.m_impl)) {}

SokobanPuzzle &SokobanPuzzle::operator=(const SokobanPuzzle &rv) {
  if (this != &rv) {
    Puzzle::operator=(rv);
    m_impl = make_unique<PIMPL>(*rv.m_impl);
  }
  return *this;
}

SokobanPuzzle::SokobanPuzzle(SokobanPuzzle &&) = default;

SokobanPuzzle &SokobanPuzzle::operator=(SokobanPuzzle &&) = default;

SokobanPuzzle::~SokobanPuzzle() = default;

SokobanPuzzle::unique_ptr_t SokobanPuzzle::clone() const {
  return make_unique<SokobanPuzzle>(*this);
}

const SokobanPuzzle::Snapshots &SokobanPuzzle::snapshots() const {
  return m_impl->m_snapshots;
}
SokobanPuzzle::Snapshots &SokobanPuzzle::snapshots() { return m_impl->m_snapshots; }

SokobanSnapshot::SokobanSnapshot() : Snapshot(Tessellation::SOKOBAN, "") {}

SokobanSnapshot::SokobanSnapshot(const string &moves_data)
  : Snapshot(Tessellation::SOKOBAN, moves_data) {}

SokobanSnapshot::SokobanSnapshot(const SokobanSnapshot &rv) : Snapshot(rv) {}

SokobanSnapshot &SokobanSnapshot::operator=(const SokobanSnapshot &rv) {
  if (this != &rv) { Snapshot::operator=(rv); }
  return *this;
}

SokobanSnapshot::SokobanSnapshot(SokobanSnapshot &&) = default;

SokobanSnapshot &SokobanSnapshot::operator=(SokobanSnapshot &&) = default;

SokobanSnapshot::~SokobanSnapshot() = default;

SokobanSnapshot::unique_ptr_t SokobanSnapshot::clone() const {
  return make_unique<SokobanSnapshot>(*this);
}

} // namespace io
} // namespace sokoengine
