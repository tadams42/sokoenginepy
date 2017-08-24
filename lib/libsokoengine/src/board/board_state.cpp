#include "board_state.hpp"
#include "sokoban_plus.hpp"
#include "variant_board.hpp"
#include "board_cell.hpp"
#include "hashed_board_state.hpp"

#include <boost/multi_index_container.hpp>
#include <boost/multi_index/ordered_index.hpp>
#include <boost/multi_index/member.hpp>
#include <boost/multi_index/mem_fun.hpp>
#include <boost/range/counting_range.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>

using namespace boost;
using namespace boost::multi_index;
using namespace std;

namespace sokoengine {

CellAlreadyOccupiedError::CellAlreadyOccupiedError(const string& mess):
  runtime_error(mess)
{}

CellAlreadyOccupiedError::~CellAlreadyOccupiedError() = default;

BoxGoalSwitchError::BoxGoalSwitchError(const string& mess):
  runtime_error(mess)
{}

BoxGoalSwitchError::~BoxGoalSwitchError() = default;

namespace implementation {

class LIBSOKOENGINE_LOCAL InvalidPieceId: public invalid_argument {
public:
  InvalidPieceId() : invalid_argument("Invalid Piece ID") {}
  virtual ~InvalidPieceId() = default;
};

class LIBSOKOENGINE_LOCAL Piece {
public:
  Piece() {}

  Piece(position_t position, piece_id_t id) :
    m_position (position), m_id (id)
  {}

  virtual ~Piece() = default;

  void set_position(position_t position) {
    m_position = position;
  }

  void set_id(piece_id_t rv) {
    if(!BoardState::is_valid_piece_id(rv)) throw InvalidPieceId();
    m_id = rv;
  }

  bool operator== (const Piece& rv) const {
    return (m_position == rv.m_position && m_id == rv.m_id);
  }

  bool operator!= (const Piece& rv) const {
    return !(*this == rv);
  }

  position_t position() const { return m_position; }
  piece_id_t id() const { return m_id; }

private:
  position_t m_position = 0;
  piece_id_t m_id       = DEFAULT_PIECE_ID;
};

struct LIBSOKOENGINE_LOCAL id_tag_t {}; // Attribute extractor
struct LIBSOKOENGINE_LOCAL position_tag_t {}; // Attribute extractor

// index_type <tag, key_extractor, comparator predicate>
typedef multi_index_container<
  Piece,
  indexed_by<
    ordered_non_unique<
      tag<id_tag_t>,
      const_mem_fun<Piece, piece_id_t, &Piece::id>
    >,
    ordered_non_unique<
      tag<position_tag_t>,
      const_mem_fun<Piece, position_t, &Piece::position>
    >
  >
>
IndexedPieceArray;

typedef IndexedPieceArray::index<id_tag_t>::type::iterator id_iterator_t;
typedef IndexedPieceArray::index<position_tag_t>::type::iterator position_iterator_t;

} // namespace implementation

using namespace implementation;

class LIBSOKOENGINE_LOCAL BoardState::PIMPL {
public:
  struct LIBSOKOENGINE_LOCAL change_position { // Attribte modifier
    change_position(position_t new_position) :
      n_value(new_position)
    {}

    void operator()(Piece& p) {
      p.set_position(n_value);
    }

  private:
    position_t n_value;
  };

  IndexedPieceArray m_boxes;
  IndexedPieceArray m_goals;
  IndexedPieceArray m_pushers;

  // non owned pointer
  VariantBoard* m_board;
  SokobanPlus m_plus;

  PIMPL(VariantBoard& board) :
    m_board(&board)
  {
    piece_id_t pusher_id, box_id, goal_id;
    pusher_id = box_id = goal_id = DEFAULT_PIECE_ID;

    for (position_t curent_pos = 0; curent_pos < m_board->size(); ++curent_pos) {
      const BoardCell& cell = m_board->cell(curent_pos);

      if (cell.has_pusher()) {
        m_pushers.insert(m_pushers.end(), Piece(curent_pos, pusher_id++));
      }
      if (cell.has_box()) {
        m_boxes.insert(m_boxes.end(), Piece(curent_pos, box_id++));
      }
      if (cell.has_goal()) {
        m_goals.insert(m_goals.end(), Piece(curent_pos, goal_id++));
      }
    }

    m_plus = SokobanPlus(m_boxes.size());
  }

  PIMPL(const PIMPL& rv) = default;
  PIMPL& operator=(const PIMPL& rv) = default;
  PIMPL(PIMPL&& rv) = default;
  PIMPL& operator=(PIMPL&& rv) = default;

  id_iterator_t piece_by_id(piece_id_t id, const IndexedPieceArray& from) {
    auto i = from.get<id_tag_t>().find(id);
    if (i == from.get<id_tag_t>().end()) {
      string piece_name;
      if (&from == &m_pushers) {
        piece_name = "pusher";
      } else if (&from == &m_boxes) {
        piece_name = "box";
      } else {
        piece_name = "goal";
      }
      throw KeyError(
        string("No ") + piece_name + " with ID: " + std::to_string(id)
      );
    } else {
      return i;
    }
  }

  position_iterator_t piece_by_position(
    position_t position, const IndexedPieceArray& from
  ) {
    auto i = from.get<position_tag_t>().find(position);
    if (i == from.get<position_tag_t>().end()) {
      string piece_name;
      if (&from == &m_pushers) {
        piece_name = "pusher";
      } else if (&from == &m_boxes) {
        piece_name = "box";
      } else {
        piece_name = "goal";
      }
      throw KeyError(
        string("No ") + piece_name + " on position: " + std::to_string(position)
      );
    } else {
      return i;
    }
  }

  bool has_piece(piece_id_t id, const IndexedPieceArray& from) const {
    return from.get<id_tag_t>().find(id) != from.get<id_tag_t>().end();
  }

  bool has_piece_on_position(
    position_t on_position, const IndexedPieceArray& from
  ) const {
    return from.get<position_tag_t>().find(on_position) !=
           from.get<position_tag_t>().end();
  }

  BoardState::piece_ids_vector_t pieces_ids(
    const IndexedPieceArray& from
  ) const {
    BoardState::piece_ids_vector_t retv;
    auto i = from.template get<id_tag_t>().begin();
    auto iend = from.template get<id_tag_t>().end();
    for (; i != iend; ++i) {
      retv.push_back(i->id());
    }
    return retv;
  }

  BoardState::piece_positions_map_t pieces_positions(
    const IndexedPieceArray from
  ) const {
    BoardState::piece_positions_map_t retv;
    auto i = from.template get<id_tag_t>().begin();
    auto iend = from.template get<id_tag_t>().end();
    for (; i != iend; ++i) {
      retv[i->id()] = i->position();
    }
    return retv;
  }

  void update_position(piece_id_t for_id, IndexedPieceArray& from,
                       position_t to_new_position) {
    from.get<id_tag_t>().modify(
      piece_by_id(for_id, from), change_position(to_new_position)
    );
  }

  void update_position_on(position_t old_position, IndexedPieceArray& from,
                          position_t to_new_position) {
    from.get<position_tag_t>().modify(
      piece_by_position(old_position, from), change_position(to_new_position)
    );
  }

  typedef pair<Piece, Piece> BoxGoalPair;
  typedef deque<BoxGoalPair> BoxGoalPairs;
  BoxGoalPairs find_box_goal_pairs() {
    auto b_count = m_boxes.size();
    auto g_count = m_goals.size();
    bool is_plus_enabled = m_plus.is_enabled();

    BoxGoalPairs retv;

    if (g_count != b_count) {
      return retv;
    }

    deque<Piece> boxes_todo;
    for(auto box : m_boxes) {
      boxes_todo.push_back(box);
    }

    for(auto goal: m_goals) {
      auto box_iter = find_if(boxes_todo.begin(), boxes_todo.end(),
        [&] (const Piece& box) -> bool {
          if (is_plus_enabled) {
            return
              m_plus.box_plus_id(box.id())
              ==
              m_plus.goal_plus_id(goal.id());
          } else {
            return box.id() == goal.id();
          }
        });
      retv.push_back(BoxGoalPair(*box_iter, goal));
      boxes_todo.erase(box_iter);
    }

    return retv;
  }
}; // BoardState::PIMPL

BoardState::BoardState(VariantBoard& board) :
  m_impl(make_unique<PIMPL>(board))
{}

BoardState::BoardState(const BoardState& rv) :
  m_impl(make_unique<PIMPL>(*rv.m_impl))
{}

BoardState& BoardState::operator=(const BoardState& rv) {
  if (this != &rv) {
    m_impl = make_unique<PIMPL>(*rv.m_impl);
  }
  return *this;
}

BoardState::BoardState(BoardState &&) = default;

BoardState& BoardState::operator=(BoardState &&) = default;

BoardState::~BoardState() = default;

bool BoardState::operator== (const BoardState& rv) const {
  return m_impl->m_boxes == rv.m_impl->m_boxes &&
         m_impl->m_goals == rv.m_impl->m_goals &&
         m_impl->m_pushers == rv.m_impl->m_pushers;
}

bool BoardState::operator!= (const BoardState& rv) const {
  return !(*this == rv);
}

const VariantBoard& BoardState::board() const {
  return *m_impl->m_board;
}

size_t BoardState::pushers_count() const {
  return m_impl->m_pushers.size();
}

BoardState::piece_ids_vector_t BoardState::pushers_ids() const {
  return m_impl->pieces_ids(m_impl->m_pushers);
}

BoardState::piece_positions_map_t BoardState::pushers_positions() const {
  return m_impl->pieces_positions(m_impl->m_pushers);
}

position_t BoardState::pusher_position(piece_id_t pusher_id) const {
  return m_impl->piece_by_id(pusher_id, m_impl->m_pushers)->position();
}

piece_id_t BoardState::pusher_id_on(position_t position) const {
  return m_impl->piece_by_position(position, m_impl->m_pushers)->id();
}

bool BoardState::has_pusher(piece_id_t pusher_id) const {
  return m_impl->has_piece(pusher_id, m_impl->m_pushers);
}

bool BoardState::has_pusher_on(position_t position) const {
  return m_impl->has_piece_on_position(position, m_impl->m_pushers);
}

void BoardState::pusher_moved(position_t old_position, position_t to_new_position) {
}

void BoardState::move_pusher_from(
  position_t old_position, position_t to_new_position
) {
  if (old_position == to_new_position) {
    return;
  }

  BoardCell& dest_cell = m_impl->m_board->cell_at(to_new_position);
  if (!dest_cell.can_put_pusher_or_box()) {
    throw CellAlreadyOccupiedError(
      string("Pusher ID: ") + std::to_string(pusher_id_on(old_position)) +
      " can't be placed in position " + std::to_string(to_new_position) +
      " occupied by '" + dest_cell.to_str() + "'"
    );
  }

  m_impl->m_board->cell_at(old_position).remove_pusher();
  dest_cell.put_pusher();
  m_impl->update_position_on(old_position, m_impl->m_pushers, to_new_position);
  pusher_moved(old_position, to_new_position);
}

void BoardState::move_pusher(piece_id_t pusher_id, position_t to_new_position) {
  move_pusher_from(pusher_position(pusher_id), to_new_position);
}

size_t BoardState::boxes_count() const {
  return m_impl->m_boxes.size();
}

BoardState::piece_ids_vector_t BoardState::boxes_ids() const {
  return m_impl->pieces_ids(m_impl->m_boxes);
}

BoardState::piece_positions_map_t BoardState::boxes_positions() const {
  return m_impl->pieces_positions(m_impl->m_boxes);
}

position_t BoardState::box_position(piece_id_t box_id) const {
  return m_impl->piece_by_id(box_id, m_impl->m_boxes)->position();
}

piece_id_t BoardState::box_id_on(position_t position) const {
  return m_impl->piece_by_position(position, m_impl->m_boxes)->id();
}

bool BoardState::has_box(piece_id_t box_id) const {
  return m_impl->has_piece(box_id, m_impl->m_boxes);
}

bool BoardState::has_box_on(position_t position) const {
  return m_impl->has_piece_on_position(position, m_impl->m_boxes);
}

void BoardState::box_moved(position_t old_position, position_t to_new_position) {
}

void BoardState::move_box_from(position_t old_position, position_t to_new_position) {
  if (old_position == to_new_position) {
    return;
  }

  BoardCell& dest_cell = m_impl->m_board->cell_at(to_new_position);
  if (!dest_cell.can_put_pusher_or_box()) {
    throw CellAlreadyOccupiedError(
      string("Box ID: ") + std::to_string(box_id_on(old_position)) +
      " can't be placed in position " + std::to_string(to_new_position) +
      " occupied by '" + dest_cell.to_str() + "'"
    );
  }

  m_impl->m_board->cell_at(old_position).remove_box();
  dest_cell.put_box();
  m_impl->update_position_on(old_position, m_impl->m_boxes, to_new_position);
  box_moved(old_position, to_new_position);
}

void BoardState::move_box(piece_id_t box_id, position_t to_new_position) {
  move_box_from(box_position(box_id), to_new_position);
}

size_t BoardState::goals_count() const {
  return m_impl->m_goals.size();
}

BoardState::piece_ids_vector_t BoardState::goals_ids() const {
  return m_impl->pieces_ids(m_impl->m_goals);
}

BoardState::piece_positions_map_t BoardState::goals_positions() const {
  return m_impl->pieces_positions(m_impl->m_goals);
}

position_t BoardState::goal_position(piece_id_t goal_id) const {
  return m_impl->piece_by_id(goal_id, m_impl->m_goals)->position();
}

piece_id_t BoardState::goal_id_on(position_t position) const {
  return m_impl->piece_by_position(position, m_impl->m_goals)->id();
}

bool BoardState::has_goal(piece_id_t goal_id) const {
  return m_impl->has_piece(goal_id, m_impl->m_goals);
}

bool BoardState::has_goal_on(position_t position) const {
  return m_impl->has_piece_on_position(position, m_impl->m_goals);
}

piece_id_t BoardState::box_plus_id(piece_id_t box_id) const {
  return m_impl->m_plus.box_plus_id(box_id);
}

piece_id_t BoardState::goal_plus_id(piece_id_t goal_id) const {
  return m_impl->m_plus.goal_plus_id(goal_id);
}

string BoardState::boxorder() const {
  return m_impl->m_plus.boxorder();
}

string BoardState::goalorder() const {
  return m_impl->m_plus.goalorder();
}

void BoardState::set_boxorder(const string& rv) {
  return m_impl->m_plus.set_boxorder(rv);
}

void BoardState::set_goalorder(const string& rv) {
  return m_impl->m_plus.set_goalorder(rv);
}

bool BoardState::is_sokoban_plus_valid() const {
  return m_impl->m_plus.is_valid();
}

bool BoardState::is_sokoban_plus_enabled() const {
  return m_impl->m_plus.is_enabled();
}

void BoardState::enable_sokoban_plus() {
  return m_impl->m_plus.enable();
}

void BoardState::disable_sokoban_plus() {
  return m_impl->m_plus.disable();
}

///
/// Map of all box IDs and positions that constitute all solutions.
///
BoardState::solutions_vector_t BoardState::solutions() const {
  solutions_vector_t retv;

  if (boxes_count() != goals_count()) {
    return retv;
  }

  typedef vector<position_t> positions_vector_t;

  auto is_valid_solution = [&] (const positions_vector_t& b_positions) -> bool {
    size_t index = 0;
    bool retv = true;
    for (auto box_position : b_positions) {
      auto b_id = index + DEFAULT_PIECE_ID;
      auto b_plus_id = box_plus_id(b_id);
      auto g_id = goal_id_on(box_position);
      auto g_plus_id = goal_plus_id(g_id);
      index++;

      retv = retv && (b_plus_id == g_plus_id);
      if (!retv) {
        break;
      }
    }
    return retv;
  };

  positions_vector_t g_positions;
  for (auto goal : m_impl->m_goals) {
    g_positions.push_back(goal.position());
  }
  sort(g_positions.begin(), g_positions.end());

  do {
    if (is_valid_solution(g_positions)) {
      piece_positions_map_t solution;
      size_t index = 0;
      for (position_t b_position : g_positions) {
        solution[index + DEFAULT_PIECE_ID] = b_position;
        index++;
      }
      retv.push_back(solution);
    }
  } while (std::next_permutation(g_positions.begin(), g_positions.end()));

  return retv;
}

void BoardState::switch_boxes_and_goals() {
  if (boxes_count() != goals_count()) {
    throw BoxGoalSwitchError(
      "Unable to switch boxes and goals - counts are not the same"
    );
  }

  for (const auto& bg_pair : m_impl->find_box_goal_pairs()) {
    auto old_box_position = box_position(bg_pair.first.id());
    auto old_goal_position = goal_position(bg_pair.second.id());

    if (old_box_position != old_goal_position) {
      piece_id_t moved_pusher_id = DEFAULT_PIECE_ID - 1;
      if (has_pusher_on(old_goal_position)) {
        moved_pusher_id = pusher_id_on(old_goal_position);
        m_impl->update_position(moved_pusher_id, m_impl->m_pushers, -1);
        m_impl->m_board->cell(old_goal_position).remove_pusher();
      }

      m_impl->update_position_on(old_goal_position, m_impl->m_goals, old_box_position);
      m_impl->m_board->cell(old_goal_position).remove_goal();
      m_impl->m_board->cell(old_box_position).put_goal();

      m_impl->update_position_on(old_box_position, m_impl->m_boxes, old_goal_position);
      m_impl->m_board->cell(old_box_position).remove_box();
      m_impl->m_board->cell(old_goal_position).put_box();
      box_moved(old_box_position, old_goal_position);

      if (moved_pusher_id != DEFAULT_PIECE_ID - 1) {
        m_impl->update_position(moved_pusher_id, m_impl->m_pushers, old_box_position);
        m_impl->m_board->cell(old_box_position).put_pusher();
        pusher_moved(old_goal_position, old_box_position);
      }
    }
  }
}

bool BoardState::is_playable() const {
  return pushers_count() > 0 &&
         boxes_count() > 0 &&
         goals_count() > 0 &&
         boxes_count() == goals_count();
}

string BoardState::to_str(const piece_ids_vector_t& v) {
  auto converter = [&]() {
    StringList retv;
    for(auto id : v) {
      retv.push_back(boost::lexical_cast<string>(id));
    }
    return retv;
  };

  return string("[") + boost::join(converter(), ", ") + "]";
}

string BoardState::to_str(const piece_positions_map_t& m) {
  auto converter = [&]() {
    StringList retv;
    for (auto p : m) {
      retv.push_back(
        string() + boost::lexical_cast<string>(p.first) + ": " +
        boost::lexical_cast<string>(p.second)
      );
    }
    return retv;
  };

  return string("{") + boost::join(converter(), ", ") + "}";
}

string BoardState::to_str(const solutions_vector_t& v, int add_indent) {
  string indent(add_indent,  ' ');
  auto converter = [&]() {
    StringList retv;
    for (auto s : v) {
      retv.push_back(indent + "    " + BoardState::to_str(s));
    }
    return retv;
  };

  return string("[\n") + boost::join(converter(), ",\n") + "\n" + indent + "]";
}

string BoardState::str() const {
  piece_positions_map_t boxes_plus_ids, goals_plus_ids;

  for (auto b_id : boxes_ids()) {
    boxes_plus_ids[b_id] = box_plus_id(b_id);
  }

  for (auto g_id : goals_ids()) {
    goals_plus_ids[g_id] = goal_plus_id(g_id);
  }

  StringList l = {
    string("    'pushers':   ") + to_str(pushers_positions()),
    string("    'boxes':     ") + to_str(boxes_positions()),
    string("    'goals':     ") + to_str(goals_positions()),
    string("    'boxes +':   ") + to_str(boxes_plus_ids),
    string("    'goals +':   ") + to_str(goals_plus_ids),
    string("    'solutions': ") + to_str(solutions(), 4)
  };

  return string("{\n") + boost::join(l, ",\n") + "\n}";
}

string BoardState::repr() const {
  return "BoardState(" + m_impl->m_board->repr() + ")";
}

} // namespace sokoengine
