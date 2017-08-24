#include "sokoban_board.hpp"
#include "tessellation.hpp"

using namespace std;

namespace sokoengine {

SokobanBoard::SokobanBoard() :
  SokobanBoard(0, 0)
{}

SokobanBoard::SokobanBoard(size_t width, size_t height) :
  VariantBoard(Tessellation::instance_from("sokoban"), width, height)
{}

SokobanBoard::SokobanBoard(const string& src) :
  VariantBoard(Tessellation::instance_from("sokoban"), src)
{}

SokobanBoard::SokobanBoard(const SokobanBoard& rv) :
  VariantBoard(rv)
{}

SokobanBoard& SokobanBoard::operator=(const SokobanBoard& rv) {
  if (this != &rv) {
      VariantBoard::operator=(rv);
  }
  return *this;
}

SokobanBoard::SokobanBoard(SokobanBoard &&) = default;

SokobanBoard& SokobanBoard::operator=(SokobanBoard &&) = default;

SokobanBoard::~SokobanBoard() = default;

SokobanBoard::unique_ptr_t SokobanBoard::create_clone() const {
  return make_unique<SokobanBoard>(*this);
}

} // namespace sokoengine
