#ifndef TESSELLATION_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define TESSELLATION_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "board_graph.hpp"
#include "sokoengine_config.hpp"

#include <stdexcept>

namespace sokoengine {

///
/// Special property of BoardCell that is needed in some tessellations and that
/// depends on cell position.
///
enum class LIBSOKOENGINE_API CellOrientation : int {
  DEFAULT = 0,
  TRIANGLE_DOWN = 1,
  OCTAGON = 2
};

///
/// Exception.
///
class LIBSOKOENGINE_API UnknownTessellationError : public std::invalid_argument {
public:
  explicit UnknownTessellationError(const std::string &mess);
  virtual ~UnknownTessellationError();
};

namespace implementation {
class LIBSOKOENGINE_LOCAL VariantBoardResizer;
class LIBSOKOENGINE_LOCAL VariantBoardParser;
class LIBSOKOENGINE_LOCAL VariantBoardPrinter;
} // namespace implementation

class LIBSOKOENGINE_API AtomicMove;
class LIBSOKOENGINE_API SokobanTessellation;
class LIBSOKOENGINE_API HexobanTessellation;
class LIBSOKOENGINE_API TriobanTessellation;
class LIBSOKOENGINE_API OctobanTessellation;

///
/// Base class for tessellations.
///
class LIBSOKOENGINE_API Tessellation {
public:
  static const SokobanTessellation &SOKOBAN;
  static const HexobanTessellation &HEXOBAN;
  static const OctobanTessellation &OCTOBAN;
  static const TriobanTessellation &TRIOBAN;

  virtual ~Tessellation() = 0;

  static const Tessellation &instance_from(const std::string &name);

  bool operator==(const Tessellation &rv) const;
  bool operator!=(const Tessellation &rv) const;

  virtual const Directions &legal_directions() const = 0;
  virtual position_t neighbor_position(position_t position, const Direction &direction,
                                       board_size_t board_width,
                                       board_size_t board_height) const = 0;
  virtual AtomicMove char_to_atomic_move(char input_chr) const = 0;
  virtual char atomic_move_to_char(const AtomicMove &atomic_move) const = 0;
  virtual GraphType graph_type() const;

  virtual CellOrientation cell_orientation(position_t position,
                                           board_size_t board_width,
                                           board_size_t board_height) const;
  virtual const implementation::VariantBoardResizer &resizer() const;
  virtual const implementation::VariantBoardPrinter &printer() const;
  virtual const implementation::VariantBoardParser &parser() const;

  virtual std::string str() const = 0;
  virtual std::string repr() const = 0;

protected:
  Tessellation() = default;
};

///
/// Converts 2D board position to 1D board position
///
constexpr position_t index_1d(position_t x, position_t y, board_size_t board_width) {
  return y * board_width + x;
}

///
/// Calculates x-axis position from 1D board position
///
constexpr position_t X(position_t index, board_size_t board_width) {
  return board_width == 0 ? 0 : index % board_width;
}

///
/// Calculates y-axis position from 1D board position
///
constexpr position_t Y(position_t index, board_size_t board_width) {
  return board_width == 0 ? 0 : index / board_width;
}

///
/// Alias for Y()
///
constexpr position_t ROW(position_t index, board_size_t board_width) {
  return Y(index, board_width);
}

///
/// Alias for X()
///
constexpr position_t COLUMN(position_t index, board_size_t board_width) {
  return X(index, board_width);
}

///
/// Is position on given board?
///
constexpr bool ON_BOARD(position_t x, position_t y, board_size_t board_width,
                        board_size_t board_height) {
  return x < board_width && y < board_height;
}

///
/// Is position on given board?
///
constexpr bool ON_BOARD(position_t pos, board_size_t board_width,
                        board_size_t board_height) {
  return ON_BOARD(X(pos, board_width), Y(pos, board_width), board_width, board_height);
}

namespace implementation {

template <class ExceptionT, class MapT>
const typename MapT::mapped_type &
find_in_map_or_throw(const MapT &map, const typename MapT::key_type &key,
                     const std::string &exception_message = "") {
  auto map_iter = map.find(key);
  if (map_iter == map.end()) {
    throw ExceptionT(exception_message);
  }
  return map_iter->second;
}

} // namespace implementation

} // namespace sokoengine

#endif // HEADER_GUARD
