#ifndef TESSELLATION_BASE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TESSELLATION_BASE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "common_types.hpp"

namespace sokoengine {

class LIBSOKOENGINE_API Direction;
class LIBSOKOENGINE_API AtomicMove;

class LIBSOKOENGINE_API TessellationBase {
public:
  virtual ~TessellationBase() = 0;

  bool operator== (const TessellationBase& rv) const;
  bool operator!= (const TessellationBase& rv) const;

  virtual const Directions& legal_directions() const = 0;
  virtual position_t neighbor_position(
    position_t position, const Direction& direction, size_t board_width,
    size_t board_height
  ) const = 0;
  virtual AtomicMove char_to_atomic_move (char input_chr) const = 0;
  virtual char atomic_move_to_char (const AtomicMove& atomic_move) const = 0;
  virtual GraphType graph_type() const { return GraphType::DIRECTED; }

  virtual CellOrientation cell_orientation(
    position_t position, size_t board_width, size_t board_height
  ) const {
    return CellOrientation::DEFAULT;
  }

  virtual std::string str() const = 0;
  virtual std::string repr() const = 0;
};

///
/// Converts 2D board position to 1D board position
///
constexpr position_t INDEX(position_t x, position_t y, size_t board_width) {
  return y * board_width + x;
}

///
/// Calculates x-axis position from 1D board position
///
constexpr position_t X(position_t index, size_t board_width) {
  return board_width == 0 ? 0 : index % board_width;
}

///
/// Calculates y-axis position from 1D board position
///
constexpr position_t Y(position_t index, size_t board_width) {
  return board_width == 0 ? 0 : index / board_width;
}

///
/// Alias for Y()
///
constexpr position_t ROW(position_t index, size_t board_width) {
  return Y(index, board_width);
}

///
/// Alias for X()
///
constexpr position_t COLUMN(position_t index, size_t board_width) {
  return X(index, board_width);
}

constexpr bool ON_BOARD(
  position_t x, position_t y, size_t board_width, size_t board_height
) {
  return x >= 0 && y >= 0 && x < board_width && y < board_height;
}

constexpr bool ON_BOARD(position_t pos, size_t board_width, size_t board_height) {
  return
    pos >= 0 &&
    ON_BOARD(
      X(pos, board_width),
      Y(pos, board_width),
      board_width,
      board_height
    );
}

template<class ExceptionT, class MapT>
const typename MapT::mapped_type& find_in_map_or_throw(
  const MapT& map, const typename MapT::key_type& key,
  const std::string& exception_message = ""
) {
  auto map_iter = map.find(key);
  if (map_iter == map.end()) {
    throw ExceptionT(exception_message);
  }
  return map_iter->second;
}

} // namespace sokoengine

#endif // HEADER_GUARD
