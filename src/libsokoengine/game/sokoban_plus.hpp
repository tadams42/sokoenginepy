#ifndef SOKOBAN_PLUS_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOKOBAN_PLUS_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <memory>
#include <stdexcept>

namespace sokoengine {
namespace game {

class LIBSOKOENGINE_API SokobanPlusDataError : public std::invalid_argument {
public:
  explicit SokobanPlusDataError(const std::string &mess);
  virtual ~SokobanPlusDataError();
};

///
/// Manages Sokoban+ data for game board.
///
/// **Sokoban+ rules**
///
/// In this variant of game rules, each box and each goal on board get number tag
/// (color). Game objective changes slightly: board is considered solved only when
/// each goal is filled with box of the same tag. So, for example goal tagged with
/// number 9 must be filled with any box tagged with number 9.
///
/// Multiple boxes and goals may share same plus id, but the number of boxes with one
/// plus id must be equal to number of goals with that same plus id. There is also
/// default plus id that represents non tagged boxes and goals.
///
/// Sokoban+ ids for given board are defined by two strings called goalorder and
/// boxorder. For example, boxorder "13 24 3 122 1" would give plus_id = 13 to box id
/// = 1, plus_id = 24 to box ID = 2, etc...
///
/// **Valid Sokoban+ id sequences**
///
/// Boxorder and goalorder must define ids for equal number of boxes and goals. This
/// means that in case of boxorder assigning plus id "42" to two boxes, goalorder
/// must also contain number 42 twice.
///
/// Sokoban+ data parser accepts any positive integer as plus id.
///
class LIBSOKOENGINE_API SokobanPlus {
public:
  ///
  /// Sokoban+ ID for pieces that don't have one or when Sokoban+ is disabled.
  ///
  /// Original Sokoban+ implementation used number 99 for default plus ID. As
  /// there can be more than 99 boxes on board, sokoenginepy changes this
  /// detail and uses :const:`DEFAULT_PLUS_ID` as default plus ID. When loading
  /// older puzzles with Sokoban+, legacy default value is converted
  /// transparently.
  ///
  static constexpr piece_id_t DEFAULT_PLUS_ID = 0;

  static constexpr piece_id_t LEGACY_DEFAULT_PLUS_ID = 99;

  static constexpr bool is_valid_plus_id(piece_id_t id) {
    return id >= DEFAULT_PLUS_ID;
  }

  ///
  /// @param boxorder Space separated integers describing Sokoban+ IDs for boxes
  /// @param goalorder Space separated integers describing Sokoban+ IDs for goals
  /// @param pieces_count Total count of boxes/goals on board
  ///
  explicit SokobanPlus(
    piece_id_t         pieces_count = 0,
    const std::string &boxorder     = "",
    const std::string &goalorder    = ""
  );
  SokobanPlus(const SokobanPlus &rv);
  SokobanPlus &operator=(const SokobanPlus &rv);
  SokobanPlus(SokobanPlus &&rv);
  SokobanPlus &operator=(SokobanPlus &&rv);
  virtual ~SokobanPlus();

  bool operator==(const SokobanPlus &rv) const;
  bool operator!=(const SokobanPlus &rv) const;

  piece_id_t pieces_count() const;
  void       set_pieces_count(piece_id_t rv);

  ///
  /// Space separated integers describing Sokoban+ IDs for boxes
  ///
  std::string boxorder() const;
  ///
  /// If rv is different from existing `boxorder`, disables Sokoban+ and sets boxorder
  /// to new value.
  ///
  void set_boxorder(const std::string &rv);

  ///
  /// Space separated integers describing Sokoban+ IDs for goals
  ///
  std::string goalorder() const;
  ///
  /// If rv is different from existing `goalorder`, disables Sokoban+ and sets
  /// goalorder to new value.
  ///
  void set_goalorder(const std::string &rv);

  bool        is_valid() const;
  bool        is_enabled() const;
  bool        is_validated() const;
  std::string errors() const;

  ///
  /// @throws SokobanPlusDataError Trying to enable invalid Sokoban+
  ///
  void enable();
  void disable();

  ///
  /// Get Sokoban+ ID for box.
  ///
  /// @returns
  /// If Sokoban+ is enabled returns Sokoban+ ID of a box. If not, returns
  /// DEFAULT_PLUS_ID
  ///
  /// @throws PieceNotFoundError No box with ID for_id, but only if i Sokoban+ is
  /// enabled
  ///
  piece_id_t box_plus_id(piece_id_t for_id) const;

  ///
  /// Get Sokoban+ ID for goal.
  ///
  /// @returns
  /// If Sokoban+ is enabled returns Sokoban+ ID of a goal. If not, returns
  /// DEFAULT_PLUS_ID
  ///
  /// @throws PieceNotFoundError No goal with ID for_id, but only if i Sokoban+ is
  /// enabled
  ///
  piece_id_t goal_plus_id(piece_id_t for_id) const;

private:
  class PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD
/// @file
