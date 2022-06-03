#ifndef OCTOBAN_BOARD_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define OCTOBAN_BOARD_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "variant_board.hpp"

namespace sokoengine {
namespace game {

///
/// Board implementation for Octoban.
///
class LIBSOKOENGINE_API OctobanBoard : public VariantBoard {
public:
  OctobanBoard();
  OctobanBoard(board_size_t width, board_size_t height);
  explicit OctobanBoard(const std::string &src);
  OctobanBoard(const OctobanBoard &rv);
  OctobanBoard &operator=(const OctobanBoard &rv);
  OctobanBoard(OctobanBoard &&rv);
  OctobanBoard &operator=(OctobanBoard &&rv);
  virtual ~OctobanBoard();
  virtual unique_ptr_t create_clone() const override;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
