#include "hashed_board_state.hpp"
#include "board_cell.hpp"
#include "sokoban_plus.hpp"
#include "variant_board.hpp"

#include <unordered_set>
#include <chrono>
#include <random>

#include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>

using namespace std;

namespace sokoengine
{

using namespace implementation;

class LIBSOKOENGINE_LOCAL HashedBoardState::PIMPL
{
public:
  bool          m_hash_invalidated          = true;
  zobrist_key_t m_initial_layout_hash       = 0;
  zobrist_key_t m_layout_hash               = 0;
  zobrist_key_t m_initial_with_pushers_hash = 0;
  zobrist_key_t m_layout_with_pushers_hash  = 0;

  typedef vector<zobrist_key_t> hash_vector_t;

  map<piece_id_t, hash_vector_t> m_boxes_factors;
  hash_vector_t m_pushers_factors;
  HashedBoardState::solution_hashes_t m_solutions_hashes;

  static std::string to_str(const hash_vector_t& v, int add_indent = 0) {
    string indent(add_indent,  ' ');

    auto converter = [&]() {
      StringList retv;

      StringList tmp;
      for(auto id : v) {
        tmp.push_back(boost::lexical_cast<string>(id));
        if (tmp.size() == 5) {
          retv.push_back(indent + "    " + boost::join(tmp, ", "));
          tmp.clear();
        }
      }
      if (!tmp.empty()) {
        retv.push_back(indent + "    " + boost::join(tmp, ", "));
      }

      return retv;
    };

    return string("[\n") + boost::join(converter(), ",\n") + "\n" + indent + "]";
  }

  static std::string to_str(
    const map<piece_id_t, hash_vector_t>& m, int add_indent = 0
  ) {
    string indent(add_indent,  ' ');
    auto converter = [&]() {
      StringList retv;
      for (auto p : m) {
        retv.push_back(
          indent + "    " + boost::lexical_cast<string>(p.first) + ": " +
          to_str(p.second, 4 + add_indent)
        );
      }
      return retv;
    };

    return string("{\n") + boost::join(converter(), ",\n") + "\n" + indent + "}";
  }

  hash_vector_t unique_random_keys(size_t of_size) const {
    unordered_set<zobrist_key_t> random_pool_set;
    mt19937_64 generator;

    generator.seed(chrono::system_clock::now().time_since_epoch().count());
    uniform_int_distribution<zobrist_key_t> distribution;
    auto random_key = bind(distribution, generator);

    while (random_pool_set.size() != of_size) {
      random_pool_set.insert(random_key());
    }

    return hash_vector_t(random_pool_set.begin(),
                                 random_pool_set.end());
  }

  void zobrist_rehash(const HashedBoardState &parent) {
    if (!m_hash_invalidated) {
      return;
    }
    m_hash_invalidated = false;

    set<piece_id_t> distinct_box_plus_ids;
    for (auto box_id : parent.boxes_ids()) {
      distinct_box_plus_ids.insert(parent.box_plus_id(box_id));
    }

    size_t random_pool_size =
        parent.board().size() +
        distinct_box_plus_ids.size() * parent.board().size() + 1;

    hash_vector_t random_pool = unique_random_keys(random_pool_size);

    size_t index          = 0;
    m_initial_layout_hash = m_layout_hash = random_pool[index++];

    m_boxes_factors = map<piece_id_t, hash_vector_t>();
    for (auto box_plus_id : distinct_box_plus_ids) {
      m_boxes_factors[box_plus_id] = hash_vector_t();
      for (size_t i = 0; i < parent.board().size(); i++) {
        m_boxes_factors[box_plus_id].push_back(random_pool[index++]);
      }
    }
    for (size_t i = 0; i < parent.board().size(); i++) {
      m_pushers_factors.push_back(random_pool[index++]);
    }

    // Hash from boxes positions
    for (auto box_id : parent.boxes_ids()) {
      m_layout_hash ^= m_boxes_factors[parent.box_plus_id(box_id)]
                                      [parent.box_position(box_id)];
    }

    m_layout_with_pushers_hash = m_initial_with_pushers_hash = m_layout_hash;

    for (auto pusher_id : parent.pushers_ids()) {
      m_layout_with_pushers_hash ^=
          m_pushers_factors[parent.pusher_position(pusher_id)];
    }

    m_solutions_hashes.clear();
  }
}; // HashedBoardState::PIMPL

HashedBoardState::HashedBoardState(VariantBoard &board)
    : BoardState(board), m_impl(std::make_unique<PIMPL>())
{}

HashedBoardState::HashedBoardState(const HashedBoardState &rv)
    : BoardState(rv), m_impl(std::make_unique<PIMPL>(*rv.m_impl))
{}

HashedBoardState &HashedBoardState::operator=(const HashedBoardState &rv) {
  if (this != &rv) {
    BoardState::operator=(rv);
    m_impl = std::make_unique<PIMPL>(*rv.m_impl);
  }
  return *this;
}

HashedBoardState::HashedBoardState(HashedBoardState &&) = default;

HashedBoardState &HashedBoardState::operator=(HashedBoardState &&) = default;

HashedBoardState::~HashedBoardState() = default;

bool HashedBoardState::operator==(const HashedBoardState &rv) const {
  return m_impl->m_layout_hash == rv.m_impl->m_layout_hash;
}

bool HashedBoardState::operator!=(const HashedBoardState &rv) const {
  return !(*this == rv);
}

zobrist_key_t HashedBoardState::boxes_layout_hash() const {
  const_cast<HashedBoardState*>(this)->m_impl->zobrist_rehash(*this);
  return m_impl->m_layout_hash;
}

zobrist_key_t HashedBoardState::boxes_and_pushers_layout_hash() const {
  const_cast<HashedBoardState*>(this)->m_impl->zobrist_rehash(*this);
  return m_impl->m_layout_with_pushers_hash;
}

zobrist_key_t HashedBoardState::external_position_hash(
  const positions_by_id_t& boxes_positions
) const {
  if (boxes_positions.size() != boxes_count() ||
      boxes_positions.size() != goals_count()) {
    return 0;
  }

  const_cast<HashedBoardState*>(this)->m_impl->zobrist_rehash(*this);

  zobrist_key_t retv = m_impl->m_initial_layout_hash;
  for (auto box : boxes_positions) {
    retv ^= m_impl->m_boxes_factors[box_plus_id(box.first)][box.second];
  }

  return retv;
}

void HashedBoardState::pusher_moved(position_t old_position, position_t to_new_position) {
  if (old_position != to_new_position) {
    const_cast<HashedBoardState*>(this)->m_impl->zobrist_rehash(*this);
    m_impl->m_layout_with_pushers_hash ^= m_impl->m_pushers_factors[old_position];
    m_impl->m_layout_with_pushers_hash ^= m_impl->m_pushers_factors[to_new_position];
  }
}

void HashedBoardState::box_moved(position_t old_position, position_t to_new_position) {
  if (old_position != to_new_position) {
    const_cast<HashedBoardState*>(this)->m_impl->zobrist_rehash(*this);

    auto b_plus_id = box_plus_id(box_id_on(to_new_position));

    m_impl->m_layout_hash ^= m_impl->m_boxes_factors[b_plus_id][old_position];
    m_impl->m_layout_hash ^= m_impl->m_boxes_factors[b_plus_id][to_new_position];

    m_impl->m_layout_with_pushers_hash ^= m_impl->m_boxes_factors[b_plus_id][old_position];
    m_impl->m_layout_with_pushers_hash ^= m_impl->m_boxes_factors[b_plus_id][to_new_position];
  }
}

void HashedBoardState::set_boxorder(const std::string& rv) {
  bool old_plus_enabled = is_sokoban_plus_enabled();
  BoardState::set_boxorder(rv);
  if (is_sokoban_plus_enabled() != old_plus_enabled) {
    m_impl->m_hash_invalidated = true;
  }
}

void HashedBoardState::set_goalorder(const std::string& rv) {
  bool old_plus_enabled = is_sokoban_plus_enabled();
  BoardState::set_goalorder(rv);
  if (is_sokoban_plus_enabled() != old_plus_enabled) {
    m_impl->m_hash_invalidated = true;
  }
}

void HashedBoardState::enable_sokoban_plus() {
  if (!is_sokoban_plus_enabled()) {
    BoardState::enable_sokoban_plus();
    m_impl->m_hash_invalidated = true;
  }
}

void HashedBoardState::disable_sokoban_plus() {
  if (is_sokoban_plus_enabled()) {
    BoardState::disable_sokoban_plus();
    m_impl->m_hash_invalidated = true;
  }
}

void HashedBoardState::switch_boxes_and_goals() {
  BoardState::switch_boxes_and_goals();
  m_impl->m_solutions_hashes.clear();
}

bool HashedBoardState::is_solved() const {
  const_cast<HashedBoardState*>(this)->m_impl->zobrist_rehash(*this);

  if (m_impl->m_solutions_hashes.empty()) {
    auto slns = solutions();
    for (auto solution : slns) {
      m_impl->m_solutions_hashes.insert(external_position_hash(solution));
    }
  }

  return m_impl->m_solutions_hashes.count(m_impl->m_layout_hash) > 0;
}

const HashedBoardState::solution_hashes_t& HashedBoardState::solution_hashes() const {
  // regenerate solution hashes
  is_solved();
  return m_impl->m_solutions_hashes;
}

string HashedBoardState::to_str(const solution_hashes_t& v) {
  auto converter = [&]() {
    StringList retv;
    for(auto id : v) {
      retv.push_back(boost::lexical_cast<string>(id));
    }
    return retv;
  };

  return string("[") + boost::join(converter(), ", ") + "]";
}

string HashedBoardState::str() const {
  positions_by_id_t boxes_plus_ids, goals_plus_ids;

  for (auto b_id : boxes_ids()) {
    boxes_plus_ids[b_id] = box_plus_id(b_id);
  }

  for (auto g_id : goals_ids()) {
    goals_plus_ids[g_id] = goal_plus_id(g_id);
  }

  StringList l = {
    string("    'pushers':   ") + BoardState::to_str(pushers_positions()),
    string("    'boxes':     ") + BoardState::to_str(boxes_positions()),
    string("    'goals':     ") + BoardState::to_str(goals_positions()),
    string("    'boxes +':   ") + BoardState::to_str(boxes_plus_ids),
    string("    'goals +':   ") + BoardState::to_str(goals_plus_ids),
    string("    'solutions': ") + BoardState::to_str(solutions(), 4),
    string("    'solution hashes': ") + to_str(solution_hashes()),
    string("    'boxes_factors:' : ") + PIMPL::to_str(m_impl->m_boxes_factors, 4),
    string("    'pushers_factors': ") + PIMPL::to_str(m_impl->m_pushers_factors, 4)
  };

  return string("{\n") + boost::join(l, ",\n") + "\n}";
}

string HashedBoardState::repr() const {
  return "HashedBoardState(" + board().repr() + ")";
}

} // namespace sokoengine
