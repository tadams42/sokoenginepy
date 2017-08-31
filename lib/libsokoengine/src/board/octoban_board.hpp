#ifndef OCTOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define OCTOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "variant_board.hpp"

namespace sokoengine {

///
/// Board implementation for Octoban.
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
