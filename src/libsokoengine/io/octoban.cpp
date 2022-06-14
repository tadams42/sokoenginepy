#include "octoban.hpp"

using namespace std;

namespace sokoengine {
namespace io {

using game::Tessellation;

namespace implementation {

LIBSOKOENGINE_LOCAL const PuzzleResizer &ob_static_resizer() {
  static const PuzzleResizer the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzleParser &ob_static_parser() {
  static const PuzzleParser the_one;
  return the_one;
}

LIBSOKOENGINE_LOCAL const PuzzlePrinter &ob_static_printer() {
  static const PuzzlePrinter the_one;
  return the_one;
}

} // namespace implementation

using namespace implementation;

class LIBSOKOENGINE_LOCAL OctobanPuzzle::PIMPL {
public:
  Snapshots m_snapshots;
};

OctobanPuzzle::OctobanPuzzle() : OctobanPuzzle(0, 0) {}

OctobanPuzzle::OctobanPuzzle(board_size_t width, board_size_t height)
  : Puzzle(Tessellation::OCTOBAN, ob_static_resizer(), ob_static_parser(),
           ob_static_printer(), width, height),
    m_impl(make_unique<PIMPL>()) {}

OctobanPuzzle::OctobanPuzzle(const string &src)
  : Puzzle(Tessellation::OCTOBAN, ob_static_resizer(), ob_static_parser(),
           ob_static_printer(), src),
    m_impl(make_unique<PIMPL>()) {}

OctobanPuzzle::OctobanPuzzle(const OctobanPuzzle &rv)
  : Puzzle(rv), m_impl(make_unique<PIMPL>(*rv.m_impl)) {}

OctobanPuzzle &OctobanPuzzle::operator=(const OctobanPuzzle &rv) {
  if (this != &rv) {
    Puzzle::operator=(rv);
    m_impl = make_unique<PIMPL>(*rv.m_impl);
  }
  return *this;
}

OctobanPuzzle::OctobanPuzzle(OctobanPuzzle &&) = default;

OctobanPuzzle &OctobanPuzzle::operator=(OctobanPuzzle &&) = default;

OctobanPuzzle::~OctobanPuzzle() = default;

OctobanPuzzle::unique_ptr_t OctobanPuzzle::clone() const {
  return make_unique<OctobanPuzzle>(*this);
}

const OctobanPuzzle::Snapshots &OctobanPuzzle::snapshots() const {
  return m_impl->m_snapshots;
}
OctobanPuzzle::Snapshots &OctobanPuzzle::snapshots() { return m_impl->m_snapshots; }

OctobanSnapshot::OctobanSnapshot() : Snapshot(Tessellation::OCTOBAN, "") {}

OctobanSnapshot::OctobanSnapshot(const string &moves_data)
  : Snapshot(Tessellation::OCTOBAN, moves_data) {}

OctobanSnapshot::OctobanSnapshot(const OctobanSnapshot &rv) : Snapshot(rv) {}

OctobanSnapshot &OctobanSnapshot::operator=(const OctobanSnapshot &rv) {
  if (this != &rv) { Snapshot::operator=(rv); }
  return *this;
}

OctobanSnapshot::OctobanSnapshot(OctobanSnapshot &&) = default;

OctobanSnapshot &OctobanSnapshot::operator=(OctobanSnapshot &&) = default;

OctobanSnapshot::~OctobanSnapshot() = default;

OctobanSnapshot::unique_ptr_t OctobanSnapshot::clone() const {
  return make_unique<OctobanSnapshot>(*this);
}

} // namespace io
} // namespace sokoengine
