#ifndef VARIANT_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define VARIANT_BOARD_HPP_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"
#include "board_graph.hpp"
#include "tessellation.hpp"
#include "text_utils.hpp"

#include <memory>

namespace sokoengine {

class BoardCell;
class Tessellation;

namespace implementation {
  class LIBSOKOENGINE_LOCAL VariantBoardResizer;
  class LIBSOKOENGINE_LOCAL HexobanBoardResizer;
}

///
/// Base class for boards.
///
class LIBSOKOENGINE_API VariantBoard {
public:
  ///
  /// Pointer to VariantBoard
  ///
  typedef std::unique_ptr<VariantBoard> unique_ptr_t;

  static unique_ptr_t instance_from(
    const Tessellation& tessellation, size_t board_width,
    size_t board_height
  );
  static unique_ptr_t instance_from(
    const std::string& tessellation_name, size_t board_width,
    size_t board_height
  );
  static unique_ptr_t instance_from(
    const Tessellation& tessellation, const std::string& board_str
  );
  static unique_ptr_t instance_from(
    const std::string& tessellation_name, const std::string& board_str
  );

  static bool is_board_string(const std::string& the_line);
  static StringList parse_board_string(const std::string& the_line);

  VariantBoard(
    const Tessellation& tessellation,
    size_t board_width=0, size_t board_height=0
  );
  VariantBoard(
    const Tessellation& tessellation, const std::string& board_str=""
  );

  virtual ~VariantBoard();
  virtual unique_ptr_t create_clone() const = 0;

  const Tessellation& tessellation() const;

  bool operator==(const VariantBoard& rv) const;
  bool operator!=(const VariantBoard& rv) const;

  const BoardCell& cell_at(position_t position) const;
  BoardCell& cell_at(position_t position);
  const BoardCell& cell(position_t position) const;
  BoardCell& cell(position_t position);
  const BoardCell operator[] (position_t position) const;
  BoardCell& operator[] (position_t position);

  bool contains(position_t position) const;

  std::string to_str(
    bool use_visible_floor=false, bool rle_encode=false
  ) const;
  std::string str() const;
  std::string repr() const;

  size_t width() const;
  size_t height() const;
  size_t size() const;

  position_t neighbor(position_t from_position, const Direction& direction) const;
  position_t neighbor_at(position_t from_position, const Direction& direction) const;
  Positions wall_neighbors(position_t from_position) const;
  Positions all_neighbors(position_t from_position) const;

  void clear();
  void mark_play_area();
  Positions positions_reachable_by_pusher(
    position_t pusher_position,
    const Positions& excluded_positions=Positions()
  ) const;
  position_t normalized_pusher_position(
    position_t pusher_position,
    const Positions& excluded_positions=Positions()
  ) const;
  position_t path_destination(
    position_t start_position, const Directions& directions_path
  ) const;
  Positions find_jump_path(position_t start_position, position_t end_position) const;
  Positions find_move_path(position_t start_position, position_t end_position) const;
  CellOrientation cell_orientation(position_t position) const;
  Directions positions_path_to_directions_path(
    const Positions& positions_path
  ) const;

  void add_row_top();
  void add_row_bottom();
  void add_column_left();
  void add_column_right();

  void remove_row_top();
  void remove_row_bottom();
  void remove_column_left();
  void remove_column_right();

  void trim_left();
  void trim_right();
  void trim_top();
  void trim_bottom();

  void reverse_rows();
  void reverse_columns();

  void resize(size_t new_width, size_t new_height);
  void resize_and_center(size_t new_width, size_t new_height);
  void trim();

  const BoardGraph& graph() const;

protected:
  VariantBoard(const VariantBoard& rv);
  VariantBoard& operator=(const VariantBoard& rv);
  VariantBoard(VariantBoard&& rv);
  VariantBoard& operator=(VariantBoard&& rv);

  void reinit(size_t board_width, size_t board_height, bool reconf_edges);
  void reinit(const std::string& src, bool reconf_edges);

private:
  class LIBSOKOENGINE_LOCAL PIMPL;
  std::unique_ptr<PIMPL> m_impl;

  void reconfigure_edges();
  friend class implementation::VariantBoardResizer;
};

namespace implementation {

class LIBSOKOENGINE_LOCAL VariantBoardResizer {
public:
  virtual ~VariantBoardResizer() = default;

  virtual void add_row_top(VariantBoard& board, bool reconfigure_edges) const;
  virtual void add_row_bottom(VariantBoard& board, bool reconfigure_edges) const;
  virtual void add_column_left(VariantBoard& board, bool reconfigure_edges) const;
  virtual void add_column_right(VariantBoard& board, bool reconfigure_edges) const;

  virtual void remove_row_top(VariantBoard& board, bool reconfigure_edges) const;
  virtual void remove_row_bottom(VariantBoard& board, bool reconfigure_edges) const;
  virtual void remove_column_left(VariantBoard& board, bool reconfigure_edges) const;
  virtual void remove_column_right(VariantBoard& board, bool reconfigure_edges) const;

  virtual void trim_left(VariantBoard& board, bool reconfigure_edges) const;
  virtual void trim_right(VariantBoard& board, bool reconfigure_edges) const;
  virtual void trim_top(VariantBoard& board, bool reconfigure_edges) const;
  virtual void trim_bottom(VariantBoard& board, bool reconfigure_edges) const;

  virtual void reverse_rows(VariantBoard& board, bool reconfigure_edges) const;
  virtual void reverse_columns(VariantBoard& board, bool reconfigure_edges) const;

protected:
  void reinit(
    VariantBoard& board, size_t board_width=0, size_t board_height=0,
    bool reconf_edges=false
  ) const;
  void reinit(
    VariantBoard& board, const std::string& src="",
    bool reconf_edges=true
  ) const;
  void reconfigure_edges(VariantBoard& board) const;
};

class LIBSOKOENGINE_LOCAL VariantBoardParser {
public:
  virtual ~VariantBoardParser() = default;
  virtual StringList parse(const std::string& board_str) const;
};

class LIBSOKOENGINE_LOCAL VariantBoardPrinter {
public:
  virtual ~VariantBoardPrinter() = default;
  virtual std::string print(
    const VariantBoard& board, bool use_visible_floor=false,
    bool rle_encode=false
  ) const;
};

} // namespace implementation

} // namespace sokoengine

#endif // HEADER_GUARD
