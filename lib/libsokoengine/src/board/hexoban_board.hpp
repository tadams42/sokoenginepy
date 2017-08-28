#ifndef HEXOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define HEXOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "variant_board.hpp"

namespace sokoengine {

///
/// Board implementation for Hexoban.
///
class LIBSOKOENGINE_API HexobanBoard : public VariantBoard {
public:
  HexobanBoard();
  HexobanBoard(size_t width, size_t height);
  explicit HexobanBoard(const std::string& src);
  HexobanBoard(const HexobanBoard& rv);
  HexobanBoard& operator=(const HexobanBoard& rv);
  HexobanBoard(HexobanBoard&& rv);
  HexobanBoard& operator=(HexobanBoard&& rv);
  virtual ~HexobanBoard();
  virtual unique_ptr_t create_clone() const override;
};

namespace implementation {

class LIBSOKOENGINE_LOCAL HexobanBoardResizer : public VariantBoardResizer {
public:
  virtual ~HexobanBoardResizer() = default;

  virtual void add_row_top(VariantBoard& board, bool reconfigure_edges) const override;

  virtual void remove_row_top(VariantBoard& board, bool reconfigure_edges) const override;
  virtual void remove_row_bottom(VariantBoard& board, bool reconfigure_edges) const override;

  virtual void reverse_columns(VariantBoard& board, bool reconfigure_edges) const override;
};

class LIBSOKOENGINE_LOCAL HexobanBoardParser : public VariantBoardParser {
public:
  virtual ~HexobanBoardParser() = default;
  virtual StringList parse(const std::string& board_str) const override;
};

class LIBSOKOENGINE_LOCAL HexobanBoardPrinter : public VariantBoardPrinter {
public:
  virtual ~HexobanBoardPrinter() = default;
  virtual std::string print(
    const VariantBoard& board, bool use_visible_floor=false,
    bool rle_encode=false
  ) const override;
};

} // namespace implementation

} // namespace sokoengine

#endif // HEADER_GUARD
