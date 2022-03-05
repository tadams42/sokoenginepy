#include "trioban_board.hpp"
#include "trioban_tessellation.hpp"

using namespace std;

namespace sokoengine {

TriobanBoard::TriobanBoard() : TriobanBoard(0, 0) {}

TriobanBoard::TriobanBoard(board_size_t width, board_size_t height)
    : VariantBoard(Tessellation::TRIOBAN, width, height) {}

TriobanBoard::TriobanBoard(const string &src)
    : VariantBoard(Tessellation::TRIOBAN, src) {}

TriobanBoard::TriobanBoard(const TriobanBoard &rv) : VariantBoard(rv) {}

TriobanBoard &TriobanBoard::operator=(const TriobanBoard &rv) {
  if (this != &rv) {
    VariantBoard::operator=(rv);
  }
  return *this;
}

TriobanBoard::TriobanBoard(TriobanBoard &&) = default;

TriobanBoard &TriobanBoard::operator=(TriobanBoard &&) = default;

TriobanBoard::~TriobanBoard() = default;

TriobanBoard::unique_ptr_t TriobanBoard::create_clone() const {
  return make_unique<TriobanBoard>(*this);
}

} // namespace sokoengine
