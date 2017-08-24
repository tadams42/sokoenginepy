#include "octoban_board.hpp"
#include "tessellation.hpp"

using namespace std;

namespace sokoengine {

OctobanBoard::OctobanBoard() :
  OctobanBoard(0, 0)
{}

OctobanBoard::OctobanBoard(size_t width, size_t height) :
  VariantBoard(Tessellation::instance_from("octoban"), width, height)
{}

OctobanBoard::OctobanBoard(const string& src) :
  VariantBoard(Tessellation::instance_from("octoban"), src)
{}

OctobanBoard::OctobanBoard(const OctobanBoard& rv) :
  VariantBoard(rv)
{}

OctobanBoard& OctobanBoard::operator=(const OctobanBoard& rv) {
  if (this != &rv) {
      VariantBoard::operator=(rv);
  }
  return *this;
}

OctobanBoard::OctobanBoard(OctobanBoard &&) = default;

OctobanBoard& OctobanBoard::operator=(OctobanBoard &&) = default;

OctobanBoard::~OctobanBoard() = default;

OctobanBoard::unique_ptr_t OctobanBoard::create_clone() const {
  return make_unique<OctobanBoard>(*this);
}

} // namespace sokoengine
