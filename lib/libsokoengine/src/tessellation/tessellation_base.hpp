#ifndef TESSELLATION_BASE_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TESSELLATION_BASE_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"
#include "board_graph.hpp"

#include <stdexcept>

namespace sokoengine {

class LIBSOKOENGINE_API AtomicMove;

enum class LIBSOKOENGINE_API CellOrientation : int {
  DEFAULT = 0,
  TRIANGLE_DOWN = 1,
  OCTAGON = 2
};

namespace implementation {
  class LIBSOKOENGINE_LOCAL VariantBoardResizer;
  class LIBSOKOENGINE_LOCAL VariantBoardParser;
  class LIBSOKOENGINE_LOCAL VariantBoardPrinter;
}

class LIBSOKOENGINE_API UnknownDirectionError: public std::invalid_argument {
public:
  UnknownDirectionError(const std::string& mess);
  virtual ~UnknownDirectionError();
};

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

  virtual const implementation::VariantBoardResizer& resizer() const;
  virtual const implementation::VariantBoardPrinter& printer() const;
  virtual const implementation::VariantBoardParser& parser() const;

  virtual std::string str() const = 0;
  virtual std::string repr() const = 0;
};

///
/// Converts 2D board position to 1D board position
///
constexpr position_t index_1d(position_t x, position_t y, size_t board_width) {
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
