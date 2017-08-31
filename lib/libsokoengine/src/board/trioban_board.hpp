#ifndef TRIOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TRIOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "variant_board.hpp"

namespace sokoengine {

///
/// Board implementation for Trioban.
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
