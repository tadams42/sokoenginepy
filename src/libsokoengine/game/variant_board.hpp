#ifndef VARIANT_BOARD_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define VARIANT_BOARD_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "board_graph.hpp"
#include "sokoengine_config.hpp"
#include "tessellation.hpp"

#include <memory>

namespace sokoengine {
namespace game {

class BoardCell;
class Tessellation;

namespace implementation {
class LIBSOKOENGINE_LOCAL VariantBoardResizer;
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

  static unique_ptr_t instance_from(const Tessellation &tessellation,
                                    board_size_t board_width,
                                    board_size_t board_height);
  static unique_ptr_t instance_from(const std::string &tessellation_name,
                                    board_size_t board_width,
                                    board_size_t board_height);
  static unique_ptr_t instance_from(const Tessellation &tessellation,
                                    const std::string &board_str);
  static unique_ptr_t instance_from(const std::string &tessellation_name,
                                    const std::string &board_str);

  VariantBoard(const Tessellation &tessellation, board_size_t board_width = 0,
               board_size_t board_height = 0);
  VariantBoard(const Tessellation &tessellation, const std::string &board_str = "");

  virtual ~VariantBoard();
  virtual unique_ptr_t create_clone() const = 0;

  const Tessellation &tessellation() const;

  bool operator==(const VariantBoard &rv) const;
  bool operator!=(const VariantBoard &rv) const;

  const BoardCell &cell_at(position_t position) const;
  BoardCell &cell_at(position_t position);
  const BoardCell &cell(position_t position) const;
  BoardCell &cell(position_t position);
  const BoardCell operator[](position_t position) const;
  BoardCell &operator[](position_t position);

  bool contains(position_t position) const;

  std::string to_str(bool use_visible_floor = false) const;
  std::string str() const;
  std::string repr() const;

  board_size_t width() const;
  board_size_t height() const;
  board_size_t size() const;

  position_t neighbor(position_t from_position, const Direction &direction) const;
  position_t neighbor_at(position_t from_position, const Direction &direction) const;
  Positions wall_neighbors(position_t from_position) const;
  Positions all_neighbors(position_t from_position) const;

  void clear();
  void mark_play_area();
  Positions positions_reachable_by_pusher(
    position_t pusher_position,
    const Positions &excluded_positions = Positions()) const;
  position_t
  normalized_pusher_position(position_t pusher_position,
                             const Positions &excluded_positions = Positions()) const;
  position_t path_destination(position_t start_position,
                              const Directions &directions_path) const;
  Positions find_jump_path(position_t start_position, position_t end_position) const;
  Positions find_move_path(position_t start_position, position_t end_position) const;
  CellOrientation cell_orientation(position_t position) const;
  Directions positions_path_to_directions_path(const Positions &positions_path) const;

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

  void resize(board_size_t new_width, board_size_t new_height);
  void resize_and_center(board_size_t new_width, board_size_t new_height);
  void trim();

  const BoardGraph &graph() const;

protected:
  VariantBoard(const VariantBoard &rv);
  VariantBoard &operator=(const VariantBoard &rv);
  VariantBoard(VariantBoard &&rv);
  VariantBoard &operator=(VariantBoard &&rv);

  void reinit(board_size_t board_width, board_size_t board_height, bool reconf_edges);
  void reinit(const std::string &src, bool reconf_edges);

private:
  class LIBSOKOENGINE_LOCAL PIMPL;
  std::unique_ptr<PIMPL> m_impl;

  friend class implementation::VariantBoardResizer;
};

namespace implementation {

class LIBSOKOENGINE_LOCAL VariantBoardResizer {
public:
  virtual ~VariantBoardResizer() = default;

  virtual void add_row_top(VariantBoard &board, bool reconfigure_edges) const;
  virtual void add_row_bottom(VariantBoard &board, bool reconfigure_edges) const;
  virtual void add_column_left(VariantBoard &board, bool reconfigure_edges) const;
  virtual void add_column_right(VariantBoard &board, bool reconfigure_edges) const;

  virtual void remove_row_top(VariantBoard &board, bool reconfigure_edges) const;
  virtual void remove_row_bottom(VariantBoard &board, bool reconfigure_edges) const;
  virtual void remove_column_left(VariantBoard &board, bool reconfigure_edges) const;
  virtual void remove_column_right(VariantBoard &board, bool reconfigure_edges) const;

  virtual void trim_left(VariantBoard &board, bool reconfigure_edges) const;
  virtual void trim_right(VariantBoard &board, bool reconfigure_edges) const;
  virtual void trim_top(VariantBoard &board, bool reconfigure_edges) const;
  virtual void trim_bottom(VariantBoard &board, bool reconfigure_edges) const;

  virtual void reverse_rows(VariantBoard &board, bool reconfigure_edges) const;
  virtual void reverse_columns(VariantBoard &board, bool reconfigure_edges) const;

protected:
  void reinit(VariantBoard &board, board_size_t board_width = 0,
              board_size_t board_height = 0, bool reconf_edges = false) const;
  void reinit(VariantBoard &board, const std::string &src = "",
              bool reconf_edges = true) const;
  void reconfigure_edges(VariantBoard &board) const;
};

class LIBSOKOENGINE_LOCAL VariantBoardParser {
public:
  virtual ~VariantBoardParser() = default;
  virtual Strings parse(const std::string &board_str) const;

  static size_t calculate_width(const Strings &string_list);
  static Strings normalize_width(const Strings &strings, char fill_chr = ' ');
  static Strings cleaned_board_lines(const std::string &line);
};

class LIBSOKOENGINE_LOCAL VariantBoardPrinter {
public:
  virtual ~VariantBoardPrinter() = default;
  virtual std::string print(const VariantBoard &board,
                            bool use_visible_floor = false) const;
};

} // namespace implementation
} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
