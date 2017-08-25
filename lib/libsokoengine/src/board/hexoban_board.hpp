#ifndef HEXOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define HEXOBAN_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "variant_board.hpp"

namespace sokoengine {

///
/// Board space is laid out on vertical hexagons with following coordinate system:
///
/// ![Hexoban coordinates](doc/img/hexoban_coordinates.png)
///
/// Textual representation uses two characters for each hexagon. This allows
/// different encoding schemes.
///
/// |            Scheme 1          |            Scheme 2          |
/// | :--------------------------: |:----------------------------:|
/// | ![Scheme 1][hexoban_scheme1] | ![Scheme 2][hexoban_scheme2] |
///
/// [hexoban_scheme1]:doc/img/hexoban_scheme1.png
/// [hexoban_scheme2]:doc/img/hexoban_scheme2.png
///
/// As long as encoding of single board is consistent, all methods handle any scheme
/// transparently - parsing of board strings 'Just Works (TM)'
///
/// Direction <-> character mapping:
///
/// | Direction::LEFT | Direction::RIGHT | Direction::NORTH_WEST | Direction::SOUTH_WEST | Direction::NORTH_EAST | Direction::SOUTH_EAST |
/// |:----:|:-----:|:----------:|:----------:|:----------:|:----------:|
/// | l, L |  r, R |    u, U    |    d, D    |    n, N    |    s, S    |
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
