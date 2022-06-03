#ifndef SOKOBAN_PLUS_0FEA723A_C86F_6753_04ABD475F6FCA5FB
#define SOKOBAN_PLUS_0FEA723A_C86F_6753_04ABD475F6FCA5FB

#include "sokoengine_config.hpp"

#include <memory>
#include <stdexcept>

namespace sokoengine {
namespace game {

///
/// Exception.
///
class LIBSOKOENGINE_API SokobanPlusDataError : public std::invalid_argument {
public:
  explicit SokobanPlusDataError(const std::string &mess);
  virtual ~SokobanPlusDataError();
};

///
/// Exception.
///
class LIBSOKOENGINE_API KeyError : public std::invalid_argument {
public:
  explicit KeyError(const std::string &mess);
  virtual ~KeyError();
};

///
/// SokobanPlus+ parsing and management.
///
class LIBSOKOENGINE_API SokobanPlus {
public:
  constexpr static u_int8_t DEFAULT_PLUS_ID = 0;

  constexpr static bool is_valid_plus_id(piece_id_t id) {
    return id >= DEFAULT_PLUS_ID;
  }

  SokobanPlus();
  explicit SokobanPlus(piece_id_t pieces_count, const std::string &boxorder = "",
                       const std::string &goalorder = "");
  SokobanPlus(const SokobanPlus &rv);
  SokobanPlus &operator=(const SokobanPlus &rv);
  SokobanPlus(SokobanPlus &&rv);
  SokobanPlus &operator=(SokobanPlus &&rv);
  virtual ~SokobanPlus();

  bool operator==(const SokobanPlus &rv) const;
  bool operator!=(const SokobanPlus &rv) const;

  piece_id_t pieces_count() const;
  void set_pieces_count(piece_id_t rv);
  std::string boxorder() const;
  void set_boxorder(const std::string &rv);
  std::string goalorder() const;
  void set_goalorder(const std::string &rv);

  bool is_valid() const;
  bool is_enabled() const;

  void enable();
  void disable();

  piece_id_t box_plus_id(piece_id_t for_id) const;
  piece_id_t goal_plus_id(piece_id_t for_id) const;

private:
  class LIBSOKOENGINE_LOCAL PIMPL;
  std::unique_ptr<PIMPL> m_impl;
};

} // namespace game
} // namespace sokoengine

#endif // HEADER_GUARD