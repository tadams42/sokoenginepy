#ifndef SOKOBAN_BOARD_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOKOBAN_BOARD_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "variant_board.hpp"

namespace sokoengine {
namespace game {

///
/// Board implementation for Sokoban.
///
class LIBSOKOENGINE_API SokobanBoard : public VariantBoard {
public:
  SokobanBoard();
  SokobanBoard(board_size_t width, board_size_t height);
  explicit SokobanBoard(const std::string &src);
  SokobanBoard(const SokobanBoard &rv);
  SokobanBoard &operator=(const SokobanBoard &rv);
  SokobanBoard(SokobanBoard &&rv);
  SokobanBoard &operator=(SokobanBoard &&rv);
  virtual ~SokobanBoard();
  virtual unique_ptr_t create_clone() const override;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
