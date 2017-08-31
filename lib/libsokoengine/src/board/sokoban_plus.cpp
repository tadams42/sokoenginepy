#include "sokoban_plus.hpp"
#include "text_utils.hpp"

#include <map>
#include <set>
#include <vector>

#include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>

using namespace std;
using namespace boost;

namespace sokoengine {

SokobanPlusDataError::SokobanPlusDataError(const string& mess):
  invalid_argument(mess)
{}

SokobanPlusDataError::~SokobanPlusDataError() = default;

KeyError::KeyError(const string& mess):
  invalid_argument(mess)
{}

KeyError::~KeyError() = default;

class LIBSOKOENGINE_LOCAL SokobanPlus::PIMPL {
public:
  typedef map<piece_id_t, piece_id_t> IdsMap;

  IdsMap m_box_plus_ids;
  IdsMap m_goal_plus_ids;
  string m_boxorder;
  string m_goalorder;
  size_t m_pieces_count = 0;
  bool m_enabled = false;
  bool m_validated = false;
  vector<string> m_errors;

  enum {
    LEGACY_DEFAULT_PLUS_ID = 99
  };

  piece_id_t get_plus_id(piece_id_t for_id, const IdsMap& from_where) const {
    if(m_enabled) {
      return from_where.at(for_id);
    } else {
      return DEFAULT_PLUS_ID;
    }
  }

  string rstrip_default_plus_ids(const string& str) const {
    if (m_pieces_count < LEGACY_DEFAULT_PLUS_ID) {
      return trim_right_copy_if(
        str,
        boost::is_any_of(lexical_cast<string>(LEGACY_DEFAULT_PLUS_ID)) ||
        boost::is_any_of(lexical_cast<string>(SokobanPlus::DEFAULT_PLUS_ID)) ||
        boost::is_space()
      );
    } else {
      return trim_right_copy_if(
        str,
        boost::is_any_of(
          lexical_cast<string>(SokobanPlus::DEFAULT_PLUS_ID)
        ) || boost::is_space()
      );
    }
  }

  IdsMap parse_and_clean_ids_string(const string& ids_str) const {
    vector<string> trimmed;
    string tmp = rstrip_default_plus_ids(ids_str);
    boost::algorithm::split(
      trimmed, tmp, is_space(),
      boost::token_compress_on
    );

    vector<piece_id_t> cleaned;
    for(const string& str_id : trimmed) {
      if (!TextUtils::is_blank(str_id)) {
        piece_id_t converted_id;
        try {
          converted_id = lexical_cast<piece_id_t>(str_id);
        }
        catch(const bad_lexical_cast&) {
          throw SokobanPlusDataError(
            "Can't parse Sokoban+ string! Illegal characters found. Only digits and spaces allowed."
          );
        }

        if (converted_id == LEGACY_DEFAULT_PLUS_ID &&
            m_pieces_count < LEGACY_DEFAULT_PLUS_ID) {
          converted_id = SokobanPlus::DEFAULT_PLUS_ID;
        }

        cleaned.push_back(converted_id);
      }
    }

    if (cleaned.size() < m_pieces_count) {
      cleaned.resize(m_pieces_count, SokobanPlus::DEFAULT_PLUS_ID);
    }

    IdsMap retv;
    piece_id_t index = 0;
    for(const auto& plus_id : cleaned) {
      retv[index + DEFAULT_PIECE_ID] = plus_id;
      index++;
    }

    return retv;
  }

  void validate_plus_ids(const IdsMap& ids) {
    for (auto id : ids) {
      if (!SokobanPlus::is_valid_plus_id(id.second)) {
        m_errors.push_back("Invalid Sokoban+ ID: " + std::to_string(id.second));
      }
    }
  }

  void validate_ids_counts() {
    if (!m_box_plus_ids.empty() && m_box_plus_ids.size() != m_pieces_count) {
      m_errors.push_back(
        string("Sokoban+ boxorder data doesn't contain same amount ") +
        "of IDs as there are pieces on board!. (pieces_count: " +
        std::to_string(m_pieces_count) + ")"
      );
    }

    if (!m_goal_plus_ids.empty() && m_goal_plus_ids.size() != m_pieces_count) {
      m_errors.push_back(
        string("Sokoban+ goalorder data doesn't contain same amount ") +
        "of IDs as there are pieces on board!. (pieces_count: " +
        std::to_string(m_pieces_count) + ")"
      );
    }
  }

  void validate_id_sets_equality() {
    set<piece_id_t> boxes, goals;
    for (auto id : m_box_plus_ids) {
      if (id.second != SokobanPlus::DEFAULT_PLUS_ID) {
        boxes.insert(id.second);
      }
    }
    for (auto id : m_goal_plus_ids) {
      if (id.second != SokobanPlus::DEFAULT_PLUS_ID) {
        goals.insert(id.second);
      }
    }

    if (boxes != goals) {
      m_errors.push_back(
        "Sokoban+ data doesn't define equal sets of IDs for boxes and goals"
      );
    }
  }
};

SokobanPlus::SokobanPlus() :
  m_impl(make_unique<PIMPL>())
{}

SokobanPlus::SokobanPlus(size_t pieces_count, const string& boxorder,
                        const string& goalorder) :
  SokobanPlus()
{
  m_impl->m_pieces_count = pieces_count;
  m_impl->m_boxorder = boxorder;
  m_impl->m_goalorder = goalorder;
}

SokobanPlus::SokobanPlus(const SokobanPlus& rv) :
  m_impl(make_unique<PIMPL>(*rv.m_impl))
{}

SokobanPlus& SokobanPlus::operator=(const SokobanPlus& rv) {
  if (this != &rv) {
      m_impl = make_unique<PIMPL>(*rv.m_impl);
  }
  return *this;
}

SokobanPlus::SokobanPlus(SokobanPlus &&) = default;

SokobanPlus& SokobanPlus::operator=(SokobanPlus &&) = default;

SokobanPlus::~SokobanPlus() = default;

bool SokobanPlus::operator== (const SokobanPlus& rv) const {
  return m_impl->m_pieces_count == rv.m_impl->m_pieces_count &&
         boxorder() == rv.boxorder() &&
         goalorder() == rv.goalorder();
}

bool SokobanPlus::operator!= (const SokobanPlus& rv) const {
  return !(*this == rv);
}

size_t SokobanPlus::pieces_count() const {
  return m_impl->m_pieces_count;
}

void SokobanPlus::set_pieces_count(size_t rv) {
  if (rv != m_impl->m_pieces_count) {
    disable();
    m_impl->m_validated = false;
    m_impl->m_pieces_count = rv;
  }
}

string SokobanPlus::boxorder() const {
  if (is_enabled() && is_valid()) {
    vector<string> tmp;
    for (const auto& id : m_impl->m_box_plus_ids) {
      tmp.push_back(std::to_string(id.second));
    }
    string tmp2 = boost::algorithm::join(tmp, " ");
    return m_impl->rstrip_default_plus_ids(tmp2);
  } else {
    return m_impl->m_boxorder;
  }
}

void SokobanPlus::set_boxorder(const string& rv) {
  if (rv != m_impl->m_boxorder) {
    disable();
    m_impl->m_validated = false;
    m_impl->m_boxorder = rv;
  }
}

string SokobanPlus::goalorder() const {
  if (is_enabled() and is_valid()) {
    vector<string> tmp;
    for (const auto& id : m_impl->m_goal_plus_ids) {
      tmp.push_back(std::to_string(id.second));
    }
    string tmp2 = boost::algorithm::join(tmp, " ");
    return m_impl->rstrip_default_plus_ids(tmp2);
  } else {
    return m_impl->m_goalorder;
  }
}

void SokobanPlus::set_goalorder(const string& rv) {
  if (rv != m_impl->m_goalorder) {
    disable();
    m_impl->m_validated = false;
    m_impl->m_goalorder = rv;
  }
}

bool SokobanPlus::is_valid() const {
  if (m_impl->m_validated == false) {
    m_impl->m_validated = true;
    m_impl->m_errors.clear();

    try {
      m_impl->m_box_plus_ids = m_impl->parse_and_clean_ids_string(m_impl->m_boxorder);
      m_impl->m_goal_plus_ids = m_impl->parse_and_clean_ids_string(m_impl->m_goalorder);
    }
    catch (const std::exception& exc) {
      m_impl->m_errors.push_back(exc.what());
    }

    m_impl->validate_plus_ids(m_impl->m_box_plus_ids);
    m_impl->validate_plus_ids(m_impl->m_goal_plus_ids);
    m_impl->validate_ids_counts();
    m_impl->validate_id_sets_equality();
  }

  return m_impl->m_errors.empty();
}

bool SokobanPlus::is_enabled() const {
  return m_impl->m_enabled;
}

void SokobanPlus::enable() {
  if (!is_valid()) {
    throw SokobanPlusDataError(boost::algorithm::join(m_impl->m_errors, ", "));
  }
  m_impl->m_enabled = true;
}

void SokobanPlus::disable() {
  m_impl->m_enabled = false;
}

piece_id_t SokobanPlus::box_plus_id(piece_id_t for_id) const {
  try {
    return m_impl->get_plus_id(for_id, m_impl->m_box_plus_ids);
  }
  catch (const out_of_range&) {
    throw KeyError("No box with ID: " + std::to_string(for_id));
  }
}

piece_id_t SokobanPlus::goal_plus_id(piece_id_t for_id) const {
  try {
    return m_impl->get_plus_id(for_id, m_impl->m_goal_plus_ids);
  }
  catch (const out_of_range&) {
    throw KeyError("No goal with ID: " + std::to_string(for_id));
  }
}

} // namespace sokoengine
