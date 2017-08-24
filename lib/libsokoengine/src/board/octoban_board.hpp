#ifndef OCTOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define OCTOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "variant_board.hpp"

namespace sokoengine {

///
/// Board space is laid out on alternating squares and octagons with
/// origin of coordinate system being octagon. Tessellation allows all
/// 8 directions of movement from Direction and depending on current
/// pusher position some of these directions do not result in successful
/// move.
///
/// Direction <-> character mapping:
///
/// |  Direction::UP  | Direction::NORTH_EAST | Direction::RIGHT | Direction::SOUTH_EAST | Direction::DOWN | Direction::SOUTH_WEST | Direction::LEFT | Direction::NORTH_WEST |
/// |:----:|:----------:|:-----:|:----------:|:----:|:----------:|:----:|:----------:|
/// | u, U |    n, N    |  r, R |    e, E    | d, D |    s, S    | l, L |    w, W    |
///
class LIBSOKOENGINE_API OctobanBoard : public VariantBoard {
public:
  OctobanBoard();
  OctobanBoard(size_t width, size_t height);
  explicit OctobanBoard(const std::string& src);
  OctobanBoard(const OctobanBoard& rv);
  OctobanBoard& operator=(const OctobanBoard& rv);
  OctobanBoard(OctobanBoard&& rv);
  OctobanBoard& operator=(OctobanBoard&& rv);
  virtual ~OctobanBoard();
  virtual unique_ptr_t create_clone() const override;
};

} // namespace sokoengine

#endif // HEADER_GUARD
