#include "trioban.hpp"

using namespace std;

namespace sokoengine {
namespace io {

using game::Tessellation;

namespace implementation {

LIBSOKOENGINE_LOCAL const PuzzleResizer &tb_static_resizer() {
  static const PuzzleResizer the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzleParser &tb_static_parser() {
  static const PuzzleParser the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzlePrinter &tb_static_printer() {
  static const PuzzlePrinter the_one;
  return the_one;
}

} // namespace implementation

using namespace implementation;

class LIBSOKOENGINE_LOCAL TriobanPuzzle::PIMPL {
public:
  Snapshots m_snapshots;
};

TriobanPuzzle::TriobanPuzzle() : TriobanPuzzle(0, 0) {}

TriobanPuzzle::TriobanPuzzle(board_size_t width, board_size_t height)
  : Puzzle(Tessellation::TRIOBAN, tb_static_resizer(), tb_static_parser(),
           tb_static_printer(), width, height),
    m_impl(make_unique<PIMPL>()) {}

TriobanPuzzle::TriobanPuzzle(const string &src)
  : Puzzle(Tessellation::TRIOBAN, tb_static_resizer(), tb_static_parser(),
           tb_static_printer(), src),
    m_impl(make_unique<PIMPL>()) {}

TriobanPuzzle::TriobanPuzzle(const TriobanPuzzle &rv)
  : Puzzle(rv), m_impl(make_unique<PIMPL>(*rv.m_impl)) {}

TriobanPuzzle &TriobanPuzzle::operator=(const TriobanPuzzle &rv) {
  if (this != &rv) {
    Puzzle::operator=(rv);
    m_impl = make_unique<PIMPL>(*rv.m_impl);
  }
  return *this;
}

TriobanPuzzle::TriobanPuzzle(TriobanPuzzle &&) = default;

TriobanPuzzle &TriobanPuzzle::operator=(TriobanPuzzle &&) = default;

TriobanPuzzle::~TriobanPuzzle() = default;

TriobanPuzzle::unique_ptr_t TriobanPuzzle::clone() const {
  return make_unique<TriobanPuzzle>(*this);
}

const TriobanPuzzle::Snapshots &TriobanPuzzle::snapshots() const {
  return m_impl->m_snapshots;
}
TriobanPuzzle::Snapshots &TriobanPuzzle::snapshots() { return m_impl->m_snapshots; }

TriobanSnapshot::TriobanSnapshot() : Snapshot(Tessellation::TRIOBAN, "") {}

TriobanSnapshot::TriobanSnapshot(const string &moves_data)
  : Snapshot(Tessellation::TRIOBAN, moves_data) {}

TriobanSnapshot::TriobanSnapshot(const TriobanSnapshot &rv) : Snapshot(rv) {}

TriobanSnapshot &TriobanSnapshot::operator=(const TriobanSnapshot &rv) {
  if (this != &rv) { Snapshot::operator=(rv); }
  return *this;
}

TriobanSnapshot::TriobanSnapshot(TriobanSnapshot &&) = default;

TriobanSnapshot &TriobanSnapshot::operator=(TriobanSnapshot &&) = default;

TriobanSnapshot::~TriobanSnapshot() = default;

TriobanSnapshot::unique_ptr_t TriobanSnapshot::clone() const {
  return make_unique<TriobanSnapshot>(*this);
}

} // namespace io
} // namespace sokoengine
