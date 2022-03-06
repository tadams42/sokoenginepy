#ifndef HEXOBAN_TESSELLATION_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define HEXOBAN_TESSELLATION_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "tessellation.hpp"

namespace sokoengine {

///
/// Tessellation for Hexoban.
///
class LIBSOKOENGINE_API HexobanTessellation : public Tessellation {
public:
  virtual const Directions &legal_directions() const override;
  virtual position_t neighbor_position(position_t position, const Direction &direction,
                                       board_size_t board_width,
                                       board_size_t board_height) const override;
  virtual AtomicMove char_to_atomic_move(char input_chr) const override;
  virtual char atomic_move_to_char(const AtomicMove &atomic_move) const override;

  virtual std::string str() const override;
  virtual std::string repr() const override;

  virtual const implementation::VariantBoardResizer &resizer() const override;
  virtual const implementation::VariantBoardPrinter &printer() const override;
  virtual const implementation::VariantBoardParser &parser() const override;

protected:
  HexobanTessellation() = default;
  friend class Tessellation;
};

} // namespace sokoengine

#endif // HEADER_GUARD
