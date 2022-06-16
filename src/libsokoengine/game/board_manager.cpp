#include "board_manager.hpp"

#include "board_cell.hpp"
#include "board_graph.hpp"
#include "hashed_board_manager.hpp"
#include "sokoban_plus.hpp"
#include "board_state.hpp"

#include <algorithm>

#include <boost/algorithm/string.hpp>
#include <boost/bimap.hpp>
#include <boost/bimap/set_of.hpp>
#include <boost/lexical_cast.hpp>

using namespace boost;
using namespace boost::bimaps;
using namespace std;

namespace sokoengine {
namespace game {

using io::Strings;

namespace implementation {

LIBSOKOENGINE_LOCAL string to_str(const BoardManager::positions_by_id_t &m) {
  auto converter = [&]() {
    Strings retv;
    for (auto p : m) {
      retv.push_back(string() + boost::lexical_cast<string>(p.first) + ": " +
                     boost::lexical_cast<string>(p.second));
    }
    return retv;
  };

  return string("{") + boost::join(converter(), ", ") + "}";
}

} // namespace implementation

CellAlreadyOccupiedError::CellAlreadyOccupiedError(const string &mess)
  : runtime_error(mess) {}

CellAlreadyOccupiedError::~CellAlreadyOccupiedError() = default;

BoxGoalSwitchError::BoxGoalSwitchError(const string &mess) : runtime_error(mess) {}

BoxGoalSwitchError::~BoxGoalSwitchError() = default;

namespace implementation {

enum class LIBSOKOENGINE_LOCAL Selectors : char { BOXES, GOALS, PUSHERS };

} // namespace implementation

using namespace implementation;

class LIBSOKOENGINE_LOCAL BoardManager::PIMPL {
public:
  typedef boost::bimap<set_of<piece_id_t>, set_of<position_t>> ids_to_positions_map_t;

  typedef ids_to_positions_map_t::left_iterator left_iterator;
  typedef ids_to_positions_map_t::right_iterator right_iterator;

  ids_to_positions_map_t m_pushers;
  ids_to_positions_map_t m_boxes;
  ids_to_positions_map_t m_goals;
  Positions m_walls;

  BoardGraph &m_board;
  SokobanPlus m_plus;

  PIMPL(BoardGraph &board, const string &boxorder, const string &goalorder)
    : m_board(board) {
    piece_id_t pusher_id, box_id, goal_id;
    pusher_id = box_id = goal_id = Config::DEFAULT_PIECE_ID;

    for (position_t curent_pos = 0; curent_pos < m_board.vertices_count();
         ++curent_pos) {
      BoardCell cell(m_board[curent_pos]);

      if (cell.has_pusher()) {
        m_pushers.insert(ids_to_positions_map_t::value_type(pusher_id++, curent_pos));
      }
      if (cell.has_box()) {
        m_boxes.insert(ids_to_positions_map_t::value_type(box_id++, curent_pos));
      }
      if (cell.has_goal()) {
        m_goals.insert(ids_to_positions_map_t::value_type(goal_id++, curent_pos));
      }

      if (cell.is_wall()) m_walls.push_back(curent_pos);
    }

    m_plus = SokobanPlus(m_boxes.size(), boxorder, goalorder);
  }

  position_t position_by_id(piece_id_t id, const Selectors &which) const {
    try {
      return which == Selectors::PUSHERS ? m_pushers.left.at(id)
             : which == Selectors::BOXES ? m_boxes.left.at(id)
                                         : m_goals.left.at(id);
    } catch (const out_of_range &) {
      throw KeyError(string("No ") +
                     (which == Selectors::PUSHERS ? "pusher"
                      : which == Selectors::BOXES ? "box"
                                                  : "goal") +
                     " with ID: " + to_string(id));
    }
  }

  piece_id_t id_by_position(position_t position, const Selectors &which) const {
    try {
      return which == Selectors::PUSHERS ? m_pushers.right.at(position)
             : which == Selectors::BOXES ? m_boxes.right.at(position)
                                         : m_goals.right.at(position);
    } catch (const out_of_range &) {
      throw KeyError(string("No ") +
                     (which == Selectors::PUSHERS ? "pusher"
                      : which == Selectors::BOXES ? "box"
                                                  : "goal") +
                     " on position: " + to_string(position));
    }
  }

  bool has_piece(piece_id_t id, const Selectors &which) const {
    return which == Selectors::PUSHERS ? m_pushers.left.find(id) != m_pushers.left.end()
           : which == Selectors::BOXES ? m_boxes.left.find(id) != m_boxes.left.end()
                                       : m_goals.left.find(id) != m_goals.left.end();
  }

  bool has_piece_on_position(position_t on_position, const Selectors &which) const {
    return which == Selectors::PUSHERS
             ? m_pushers.right.find(on_position) != m_pushers.right.end()
           : which == Selectors::BOXES
             ? m_boxes.right.find(on_position) != m_boxes.right.end()
             : m_goals.right.find(on_position) != m_goals.right.end();
  }

  piece_ids_vector_t pieces_ids(const Selectors &which) const {
    piece_ids_vector_t retv;

    switch (which) {
    case Selectors::PUSHERS:
      for (auto pusher : m_pushers.left)
        retv.push_back(pusher.first);
      break;
    case Selectors::BOXES:
      for (auto box : m_boxes.left)
        retv.push_back(box.first);
      break;
    case Selectors::GOALS:
    default:
      for (auto goal : m_goals.left)
        retv.push_back(goal.first);
      break;
    };

    return retv;
  }

  positions_by_id_t pieces_positions(const Selectors &which) const {
    positions_by_id_t retv;

    switch (which) {
    case Selectors::PUSHERS:
      for (auto pusher : m_pushers.left)
        retv[pusher.first] = pusher.second;
      break;
    case Selectors::BOXES:
      for (auto box : m_boxes.left)
        retv[box.first] = box.second;
      break;
    case Selectors::GOALS:
    default:
      for (auto goal : m_goals.left)
        retv[goal.first] = goal.second;
      break;
    };

    return retv;
  }

  void update_position(piece_id_t for_id, const Selectors &which,
                       position_t to_new_position) {
    switch (which) {
    case Selectors::PUSHERS:
      m_pushers.left.replace_data(m_pushers.left.find(for_id), to_new_position);
      break;
    case Selectors::BOXES:
      m_boxes.left.replace_data(m_boxes.left.find(for_id), to_new_position);
      break;
    case Selectors::GOALS:
    default:
      m_boxes.left.replace_data(m_boxes.left.find(for_id), to_new_position);
      break;
    }
  }

  void update_position_on(position_t old_position, const Selectors &which,
                          position_t to_new_position) {
    switch (which) {
    case Selectors::PUSHERS:
      m_pushers.right.replace_key(m_pushers.right.find(old_position), to_new_position);
      break;
    case Selectors::BOXES:
      m_boxes.right.replace_key(m_boxes.right.find(old_position), to_new_position);
      break;
    case Selectors::GOALS:
    default:
      m_goals.right.replace_key(m_goals.right.find(old_position), to_new_position);
      break;
    }
  }

  typedef pair<piece_id_t, position_t> Piece;
  typedef pair<Piece, Piece> BoxGoalPair;
  typedef deque<BoxGoalPair> BoxGoalPairs;

  BoxGoalPairs find_box_goal_pairs() const {
    auto b_count = m_boxes.size();
    auto g_count = m_goals.size();
    bool is_plus_enabled = m_plus.is_enabled();

    BoxGoalPairs retv;

    if (g_count != b_count) return retv;

    auto boxes_todo = m_boxes;

    for (auto goal : m_goals.left) {
      auto box_iter =
        find_if(boxes_todo.left.begin(), boxes_todo.left.end(), [&](auto box) -> bool {
          if (is_plus_enabled)
            return m_plus.box_plus_id(box.first) == m_plus.goal_plus_id(goal.first);
          return box.first == goal.first;
        });
      retv.push_back(make_pair(make_pair(box_iter->first, box_iter->second),
                               make_pair(goal.first, goal.second)));
      boxes_todo.left.erase(box_iter);
    }

    return retv;
  }
}; // BoardManager::PIMPL

BoardManager::BoardManager(BoardGraph &board, const string &boxorder,
                           const string &goalorder)
  : m_impl(make_unique<PIMPL>(board, boxorder, goalorder)) {}

BoardManager::BoardManager(BoardManager &&) = default;

BoardManager &BoardManager::operator=(BoardManager &&) = default;

BoardManager::~BoardManager() = default;

bool BoardManager::operator==(const BoardManager &rv) const {
  return m_impl->m_pushers == rv.m_impl->m_pushers &&
         m_impl->m_boxes == rv.m_impl->m_boxes && m_impl->m_goals == rv.m_impl->m_goals;
}

bool BoardManager::operator!=(const BoardManager &rv) const { return !(*this == rv); }

const BoardGraph &BoardManager::board() const { return m_impl->m_board; }

board_size_t BoardManager::pushers_count() const { return m_impl->m_pushers.size(); }

BoardManager::piece_ids_vector_t BoardManager::pushers_ids() const {
  return m_impl->pieces_ids(Selectors::PUSHERS);
}

BoardManager::positions_by_id_t BoardManager::pushers_positions() const {
  return m_impl->pieces_positions(Selectors::PUSHERS);
}

position_t BoardManager::pusher_position(piece_id_t pusher_id) const {
  return m_impl->position_by_id(pusher_id, Selectors::PUSHERS);
}

piece_id_t BoardManager::pusher_id_on(position_t position) const {
  return m_impl->id_by_position(position, Selectors::PUSHERS);
}

bool BoardManager::has_pusher(piece_id_t pusher_id) const {
  return m_impl->has_piece(pusher_id, Selectors::PUSHERS);
}

bool BoardManager::has_pusher_on(position_t position) const {
  return m_impl->has_piece_on_position(position, Selectors::PUSHERS);
}

void BoardManager::pusher_moved(position_t old_position, position_t o_new_position) {}

void BoardManager::move_pusher_from(position_t old_position,
                                    position_t to_new_position) {
  if (old_position == to_new_position) return;

  BoardCell &dest_cell = m_impl->m_board.cell_at(to_new_position);
  if (!dest_cell.can_put_pusher_or_box()) {
    throw CellAlreadyOccupiedError(
      string("Pusher ID: ") + to_string(pusher_id_on(old_position)) +
      " can't be placed in position " + to_string(to_new_position) + " occupied by '" +
      dest_cell.to_str() + "'");
  }

  m_impl->m_board.cell_at(old_position).remove_pusher();
  dest_cell.put_pusher();
  m_impl->update_position_on(old_position, Selectors::PUSHERS, to_new_position);
  pusher_moved(old_position, to_new_position);
}

void BoardManager::move_pusher(piece_id_t pusher_id, position_t to_new_position) {
  move_pusher_from(pusher_position(pusher_id), to_new_position);
}

board_size_t BoardManager::boxes_count() const { return m_impl->m_boxes.size(); }

BoardManager::piece_ids_vector_t BoardManager::boxes_ids() const {
  return m_impl->pieces_ids(Selectors::BOXES);
}

BoardManager::positions_by_id_t BoardManager::boxes_positions() const {
  return m_impl->pieces_positions(Selectors::BOXES);
}

position_t BoardManager::box_position(piece_id_t box_id) const {
  return m_impl->position_by_id(box_id, Selectors::BOXES);
}

piece_id_t BoardManager::box_id_on(position_t position) const {
  return m_impl->id_by_position(position, Selectors::BOXES);
}

bool BoardManager::has_box(piece_id_t box_id) const {
  return m_impl->has_piece(box_id, Selectors::BOXES);
}

bool BoardManager::has_box_on(position_t position) const {
  return m_impl->has_piece_on_position(position, Selectors::BOXES);
}

void BoardManager::box_moved(position_t old_position, position_t o_new_position) {}

void BoardManager::move_box_from(position_t old_position, position_t to_new_position) {
  if (old_position == to_new_position) return;

  BoardCell &dest_cell = m_impl->m_board.cell_at(to_new_position);
  if (!dest_cell.can_put_pusher_or_box()) {
    throw CellAlreadyOccupiedError(
      string("Box ID: ") + to_string(box_id_on(old_position)) +
      " can't be placed in position " + to_string(to_new_position) + " occupied by '" +
      dest_cell.to_str() + "'");
  }

  m_impl->m_board.cell_at(old_position).remove_box();
  dest_cell.put_box();
  m_impl->update_position_on(old_position, Selectors::BOXES, to_new_position);
  box_moved(old_position, to_new_position);
}

void BoardManager::move_box(piece_id_t box_id, position_t to_new_position) {
  move_box_from(box_position(box_id), to_new_position);
}

board_size_t BoardManager::goals_count() const { return m_impl->m_goals.size(); }

BoardManager::piece_ids_vector_t BoardManager::goals_ids() const {
  return m_impl->pieces_ids(Selectors::GOALS);
}

BoardManager::positions_by_id_t BoardManager::goals_positions() const {
  return m_impl->pieces_positions(Selectors::GOALS);
}

position_t BoardManager::goal_position(piece_id_t goal_id) const {
  return m_impl->position_by_id(goal_id, Selectors::GOALS);
}

piece_id_t BoardManager::goal_id_on(position_t position) const {
  return m_impl->id_by_position(position, Selectors::GOALS);
}

bool BoardManager::has_goal(piece_id_t goal_id) const {
  return m_impl->has_piece(goal_id, Selectors::GOALS);
}

bool BoardManager::has_goal_on(position_t position) const {
  return m_impl->has_piece_on_position(position, Selectors::GOALS);
}

const Positions &BoardManager::walls_positions() const { return m_impl->m_walls; }

piece_id_t BoardManager::box_plus_id(piece_id_t box_id) const {
  return m_impl->m_plus.box_plus_id(box_id);
}

piece_id_t BoardManager::goal_plus_id(piece_id_t goal_id) const {
  return m_impl->m_plus.goal_plus_id(goal_id);
}

string BoardManager::boxorder() const { return m_impl->m_plus.boxorder(); }

string BoardManager::goalorder() const { return m_impl->m_plus.goalorder(); }

void BoardManager::set_boxorder(const string &rv) {
  return m_impl->m_plus.set_boxorder(rv);
}

void BoardManager::set_goalorder(const string &rv) {
  return m_impl->m_plus.set_goalorder(rv);
}

bool BoardManager::is_sokoban_plus_valid() const { return m_impl->m_plus.is_valid(); }

bool BoardManager::is_sokoban_plus_enabled() const {
  return m_impl->m_plus.is_enabled();
}

void BoardManager::enable_sokoban_plus() { return m_impl->m_plus.enable(); }

void BoardManager::disable_sokoban_plus() { return m_impl->m_plus.disable(); }

BoardManager::solutions_vector_t BoardManager::solutions() const {
  solutions_vector_t retv;

  if (boxes_count() != goals_count()) return retv;

  typedef vector<position_t> positions_vector_t;

  auto is_valid_solution = [&](const positions_vector_t &b_positions) -> bool {
    piece_id_t index = 0;
    bool retv = true;
    for (auto box_position : b_positions) {
      auto b_id = index + Config::DEFAULT_PIECE_ID;
      auto b_plus_id = box_plus_id(b_id);
      auto g_id = goal_id_on(box_position);
      auto g_plus_id = goal_plus_id(g_id);
      index++;

      retv = retv && (b_plus_id == g_plus_id);
      if (!retv) break;
    }
    return retv;
  };

  positions_vector_t g_positions;
  for (auto goal : m_impl->m_goals.left)
    g_positions.push_back(goal.second);
  sort(g_positions.begin(), g_positions.end());

  do {
    if (is_valid_solution(g_positions)) {
      retv.push_back(BoardState(Positions(), g_positions));
    }
  } while (std::next_permutation(g_positions.begin(), g_positions.end()));

  return retv;
}

void BoardManager::switch_boxes_and_goals() {
  if (boxes_count() != goals_count()) {
    throw BoxGoalSwitchError(
      "Unable to switch boxes and goals - counts are not the same");
  }

  for (const auto &bg_pair : m_impl->find_box_goal_pairs()) {
    auto old_box_position = box_position(bg_pair.first.first);
    auto old_goal_position = goal_position(bg_pair.second.first);

    if (old_box_position != old_goal_position) {
      piece_id_t moved_pusher_id = Config::DEFAULT_PIECE_ID - 1;
      if (has_pusher_on(old_goal_position)) {
        moved_pusher_id = pusher_id_on(old_goal_position);
        m_impl->update_position(moved_pusher_id, Selectors::PUSHERS, -1);
        m_impl->m_board.cell(old_goal_position).remove_pusher();
      }

      m_impl->update_position_on(old_goal_position, Selectors::GOALS, old_box_position);
      m_impl->m_board.cell(old_goal_position).remove_goal();
      m_impl->m_board.cell(old_box_position).put_goal();

      m_impl->update_position_on(old_box_position, Selectors::BOXES, old_goal_position);
      m_impl->m_board.cell(old_box_position).remove_box();
      m_impl->m_board.cell(old_goal_position).put_box();
      box_moved(old_box_position, old_goal_position);

      if (moved_pusher_id != Config::DEFAULT_PIECE_ID - 1) {
        m_impl->update_position(moved_pusher_id, Selectors::PUSHERS, old_box_position);
        m_impl->m_board.cell(old_box_position).put_pusher();
        pusher_moved(old_goal_position, old_box_position);
      }
    }
  }
}

bool BoardManager::is_solved() const {
  if (boxes_count() != goals_count()) return false;

  bool retv = true;

  for (auto box : m_impl->m_boxes.left) {
    retv = retv && has_goal_on(box.second) &&
           box_plus_id(box.first) == goal_plus_id(goal_id_on(box.second));
    if (!retv) break;
  }

  return retv;
}

bool BoardManager::is_playable() const {
  return pushers_count() > 0 && boxes_count() > 0 && goals_count() > 0 &&
         boxes_count() == goals_count();
}

string BoardManager::str() const {
  auto converter = [](const Positions &positions) {
    size_t max_members = 10;
    Strings tmp;
    for (size_t i = 0; i < min(positions.size(), max_members); ++i) {
      tmp.push_back(boost::lexical_cast<string>(positions[i]));
    }

    if (positions.size() <= max_members)
      return string("[") + boost::join(tmp, ", ") + "]";
    else
      return string("[") + boost::join(tmp, ", ") + ", ...]";
  };

  return "<BoardManager pushers: " + to_str(pushers_positions()) + ",\n" +
         "              boxes: " + to_str(boxes_positions()) + ",\n" +
         "              goals: " + to_str(goals_positions()) + ",\n" +
         "              walls: " + converter(walls_positions()) + ",\n" +
         "              boxorder: '" + boxorder() + "',\n" +
         "              goalorder: '" + boxorder() + "',\n>";
}

BoardState BoardManager::state() const {
  auto p_ids = pushers_ids();
  auto b_ids = boxes_ids();

  sort(p_ids.begin(), p_ids.end());
  sort(b_ids.begin(), b_ids.end());

  Positions pushers, boxes;

  for (auto pid : p_ids)
    pushers.push_back(pusher_position(pid));
  for (auto bid : b_ids)
    boxes.push_back(box_position(bid));

  return BoardState(pushers, boxes);
}

} // namespace game
} // namespace sokoengine
