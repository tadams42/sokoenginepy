#include "hashed_board_manager.hpp"

#include "board_cell.hpp"
#include "board_graph.hpp"
#include "board_state.hpp"
#include "sokoban_plus.hpp"

#include <chrono>
#include <random>
#include <unordered_set>

#include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>

using namespace std;

namespace sokoengine {
namespace game {

using io::Strings;

class LIBSOKOENGINE_LOCAL HashedBoardManager::PIMPL {
public:
  bool m_hash_invalidated = true;
  zobrist_key_t m_initial_state_hash = 0;
  zobrist_key_t m_state_hash = 0;

  typedef vector<zobrist_key_t> hash_vector_t;

  map<piece_id_t, hash_vector_t> m_boxes_factors;
  hash_vector_t m_pushers_factors;
  HashedBoardManager::solutions_hashes_t m_solutions_hashes;

  PIMPL() {}
  PIMPL(PIMPL &&rv) = default;
  PIMPL &operator=(PIMPL &&rv) = default;

  static std::string to_str(const hash_vector_t &v, int add_indent = 0) {
    string indent(add_indent, ' ');

    auto converter = [&]() {
      Strings retv;

      Strings tmp;
      for (auto id : v) {
        tmp.push_back(boost::lexical_cast<string>(id));
        if (tmp.size() == 5) {
          retv.push_back(indent + "    " + boost::join(tmp, ", "));
          tmp.clear();
        }
      }
      if (!tmp.empty()) { retv.push_back(indent + "    " + boost::join(tmp, ", ")); }

      return retv;
    };

    return string("[\n") + boost::join(converter(), ",\n") + "\n" + indent + "]";
  }

  static std::string to_str(const map<piece_id_t, hash_vector_t> &m,
                            int add_indent = 0) {
    string indent(add_indent, ' ');
    auto converter = [&]() {
      Strings retv;
      for (auto p : m) {
        retv.push_back(indent + "    " + boost::lexical_cast<string>(p.first) + ": " +
                       to_str(p.second, 4 + add_indent));
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

    return hash_vector_t(random_pool_set.begin(), random_pool_set.end());
  }

  void zobrist_rehash(const HashedBoardManager &parent) {
    if (!m_hash_invalidated) return;
    m_hash_invalidated = false;

    set<piece_id_t> distinct_box_plus_ids;
    for (auto box_id : parent.boxes_ids()) {
      distinct_box_plus_ids.insert(parent.box_plus_id(box_id));
    }

    board_size_t board_without_walls_size =
      parent.board().vertices_count() - parent.walls_positions().size();

    size_t random_pool_size = board_without_walls_size +
                              distinct_box_plus_ids.size() * board_without_walls_size +
                              1;

    hash_vector_t random_pool = unique_random_keys(random_pool_size);

    size_t index = 0;
    m_initial_state_hash = m_state_hash = random_pool[index++];

    m_boxes_factors = map<piece_id_t, hash_vector_t>();
    for (auto box_plus_id : distinct_box_plus_ids) {
      m_boxes_factors[box_plus_id] = hash_vector_t();
      for (board_size_t i = 0; i < parent.board().vertices_count(); i++) {
        if (std::find(parent.walls_positions().begin(), parent.walls_positions().end(),
                      i) != parent.walls_positions().end())
          m_boxes_factors[box_plus_id].push_back(0);
        else
          m_boxes_factors[box_plus_id].push_back(random_pool[index++]);
      }
    }
    for (board_size_t i = 0; i < parent.board().vertices_count(); i++) {
      if (std::find(parent.walls_positions().begin(), parent.walls_positions().end(),
                    i) != parent.walls_positions().end())
        m_pushers_factors.push_back(0);
      else
        m_pushers_factors.push_back(random_pool[index++]);
    }

    // Hash from boxes positions
    for (auto box_id : parent.boxes_ids()) {
      m_state_hash ^=
        m_boxes_factors[parent.box_plus_id(box_id)][parent.box_position(box_id)];
    }

    for (auto pusher_id : parent.pushers_ids()) {
      m_state_hash ^= m_pushers_factors[parent.pusher_position(pusher_id)];
    }
  }
}; // HashedBoardManager::PIMPL

HashedBoardManager::HashedBoardManager(BoardGraph &board, const string &boxorder,
                                       const string &goalorder)
  : BoardManager(board, boxorder, goalorder), m_impl(std::make_unique<PIMPL>()) {}

HashedBoardManager::HashedBoardManager(HashedBoardManager &&) = default;

HashedBoardManager &HashedBoardManager::operator=(HashedBoardManager &&) = default;

HashedBoardManager::~HashedBoardManager() = default;

bool HashedBoardManager::operator==(const HashedBoardManager &rv) const {
  return m_impl->m_state_hash == rv.m_impl->m_state_hash;
}

bool HashedBoardManager::operator!=(const HashedBoardManager &rv) const {
  return !(*this == rv);
}

zobrist_key_t HashedBoardManager::state_hash() const {
  const_cast<HashedBoardManager *>(this)->m_impl->zobrist_rehash(*this);
  return m_impl->m_state_hash;
}

zobrist_key_t HashedBoardManager::initial_state_hash() const {
  const_cast<HashedBoardManager *>(this)->m_impl->zobrist_rehash(*this);
  return m_impl->m_initial_state_hash;
}

zobrist_key_t HashedBoardManager::external_state_hash(BoardState &board_state) const {
  if (board_state.boxes_positions().size() != boxes_count() ||
      board_state.boxes_positions().size() != goals_count())
    return 0;

  const_cast<HashedBoardManager *>(this)->m_impl->zobrist_rehash(*this);

  zobrist_key_t retv = m_impl->m_initial_state_hash;

  piece_id_t index = 0;
  for (auto box_position : board_state.boxes_positions()) {
    retv ^=
      m_impl
        ->m_boxes_factors[box_plus_id(Config::DEFAULT_PIECE_ID + index)][box_position];
    index++;
  }

  for (auto pusher_position : board_state.pushers_positions())
    retv ^= m_impl->m_pushers_factors[pusher_position];

  board_state.zobrist_hash() = retv;

  return retv;
}

void HashedBoardManager::pusher_moved(position_t old_position,
                                      position_t to_new_position) {
  if (old_position != to_new_position) {
    const_cast<HashedBoardManager *>(this)->m_impl->zobrist_rehash(*this);
    m_impl->m_state_hash ^= m_impl->m_pushers_factors[old_position];
    m_impl->m_state_hash ^= m_impl->m_pushers_factors[to_new_position];
  }
}

void HashedBoardManager::box_moved(position_t old_position,
                                   position_t to_new_position) {
  if (old_position != to_new_position) {
    const_cast<HashedBoardManager *>(this)->m_impl->zobrist_rehash(*this);
    auto b_plus_id = box_plus_id(box_id_on(to_new_position));
    m_impl->m_state_hash ^= m_impl->m_boxes_factors[b_plus_id][old_position];
    m_impl->m_state_hash ^= m_impl->m_boxes_factors[b_plus_id][to_new_position];
  }
}

void HashedBoardManager::set_boxorder(const std::string &rv) {
  bool old_plus_enabled = is_sokoban_plus_enabled();
  BoardManager::set_boxorder(rv);
  if (is_sokoban_plus_enabled() != old_plus_enabled) {
    m_impl->m_solutions_hashes.clear();
    m_impl->m_hash_invalidated = true;
  }
}

void HashedBoardManager::set_goalorder(const std::string &rv) {
  bool old_plus_enabled = is_sokoban_plus_enabled();
  BoardManager::set_goalorder(rv);
  if (is_sokoban_plus_enabled() != old_plus_enabled) {
    m_impl->m_solutions_hashes.clear();
    m_impl->m_hash_invalidated = true;
  }
}

void HashedBoardManager::enable_sokoban_plus() {
  if (!is_sokoban_plus_enabled()) {
    BoardManager::enable_sokoban_plus();
    m_impl->m_solutions_hashes.clear();
    m_impl->m_hash_invalidated = true;
  }
}

void HashedBoardManager::disable_sokoban_plus() {
  if (is_sokoban_plus_enabled()) {
    BoardManager::disable_sokoban_plus();
    m_impl->m_solutions_hashes.clear();
    m_impl->m_hash_invalidated = true;
  }
}

bool HashedBoardManager::is_solved() const {
  return solutions_hashes().count(state_hash()) > 0;
}

const HashedBoardManager::solutions_hashes_t &
HashedBoardManager::solutions_hashes() const {
  if (m_impl->m_solutions_hashes.empty()) {
    // regenerate hashes
    auto slns = solutions();
    for (auto solution : slns) {
      const_cast<HashedBoardManager *>(this)->m_impl->m_solutions_hashes.insert(
        external_state_hash(solution));
    }
  }

  return m_impl->m_solutions_hashes;
}

string HashedBoardManager::str() const {
  string retv = BoardManager::str();
  boost::replace_all(retv, "<BoardManager pushers:", "<HashedBoardManager pushers:");
  boost::replace_all(retv, "              boxes:", "                    boxes:");
  boost::replace_all(retv, "              goals:", "                    goals:");
  boost::replace_all(retv, "              walls:", "                    walls:");
  boost::replace_all(retv, "              boxorder:", "                    boxorder:");
  boost::replace_all(retv,
                     "              goalorder:", "                    goalorder:");
  boost::replace_all(retv, "              board:", "                    board:");
  return retv;
}

BoardState HashedBoardManager::state() const {
  auto retv = BoardManager::state();
  retv.zobrist_hash() = state_hash();
  return retv;
}

} // namespace game
} // namespace sokoengine
