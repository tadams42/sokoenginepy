#include "octoban_board.hpp"
#include "octoban_tessellation.hpp"

using namespace std;

namespace sokoengine {

OctobanBoard::OctobanBoard() : OctobanBoard(0, 0) {}

OctobanBoard::OctobanBoard(board_size_t width, board_size_t height)
    : VariantBoard(Tessellation::OCTOBAN, width, height) {}

OctobanBoard::OctobanBoard(const string &src)
    : VariantBoard(Tessellation::OCTOBAN, src) {}

OctobanBoard::OctobanBoard(const OctobanBoard &rv) : VariantBoard(rv) {}

OctobanBoard &OctobanBoard::operator=(const OctobanBoard &rv) {
  if (this != &rv) {
    VariantBoard::operator=(rv);
  }
  return *this;
}

OctobanBoard::OctobanBoard(OctobanBoard &&) = default;

OctobanBoard &OctobanBoard::operator=(OctobanBoard &&) = default;

OctobanBoard::~OctobanBoard() = default;

OctobanBoard::unique_ptr_t OctobanBoard::create_clone() const {
  return make_unique<OctobanBoard>(*this);
}

} // namespace sokoengine
