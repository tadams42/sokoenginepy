#ifndef TRIOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TRIOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "variant_board.hpp"

namespace sokoengine {

///
/// Board is laid out on alternating triangles with origin triangle poiting up.
/// Direction <-> character mapping:
///
/// | Direction::LEFT | Direction::RIGHT | Direction::NORTH_EAST | Direction::NORTH_WEST | Direction::SOUTH_EAST | Direction::SOUTH_WEST |
/// |:----:|:-----:|:----------:|:----------:|:----------:|:----------:|
/// | l, L |  r, R |    n, N    |    u, U    |    d, D    |    s, S    |
///
/// Depending on current pusher position, some moves are not allowed:
///
/// ![Trioban movement](doc/img/trioban_am.png)
///
class LIBSOKOENGINE_API TriobanBoard : public VariantBoard {
public:
  TriobanBoard();
  TriobanBoard(size_t width, size_t height);
  explicit TriobanBoard(const std::string& src);
  TriobanBoard(const TriobanBoard& rv);
  TriobanBoard& operator=(const TriobanBoard& rv);
  TriobanBoard(TriobanBoard&& rv);
  TriobanBoard& operator=(TriobanBoard&& rv);
  virtual ~TriobanBoard();
  virtual unique_ptr_t create_clone() const override;
};

} // namespace sokoengine

#endif // HEADER_GUARD
