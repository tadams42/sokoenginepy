#include "mover.hpp"

#include "board_cell.hpp"
#include "board_graph.hpp"
#include "hashed_board_manager.hpp"
#include "pusher_step.hpp"
#include "puzzle.hpp"
#include "tessellation.hpp"

#include "cppitertools/groupby.hpp"

#include <algorithm>

using namespace std;

namespace sokoengine {
namespace game {

using io::Puzzle;

NonPlayableBoardError::NonPlayableBoardError()
  : runtime_error("Board is not playable!") {}

NonPlayableBoardError::~NonPlayableBoardError() = default;

IllegalMoveError::IllegalMoveError(const string &mess) : runtime_error(mess) {}

IllegalMoveError::~IllegalMoveError() = default;

class LIBSOKOENGINE_LOCAL Mover::PIMPL {
public:
  BoardGraph m_initial_board;
  HashedBoardManager m_manager;
  SolvingMode m_solving_mode;
  bool m_pulls_boxes = true;
  piece_id_t m_selected_pusher = Config::DEFAULT_PIECE_ID;
  size_t m_pull_count = 0;
  PusherSteps m_last_move;

  PIMPL(BoardGraph &board, SolvingMode mode)
    : m_initial_board(board), m_manager(board), m_solving_mode(mode) {
    if (!m_manager.is_playable()) { throw NonPlayableBoardError(); }

    if (m_solving_mode == SolvingMode::REVERSE) { m_manager.switch_boxes_and_goals(); }
  }

  PIMPL(PIMPL &&rv) = default;
  PIMPL &operator=(PIMPL &&rv) = default;

  struct MoveWorkerOptions {
    bool decrease_pull_count = false;
    bool increase_pull_count = false;
    bool force_pulls = false;
  };

  void select_pusher(piece_id_t pusher_id) {
    if (pusher_id == m_selected_pusher) return;

    position_t old_pusher_position = m_manager.pusher_position(m_selected_pusher);
    position_t new_pusher_position = m_manager.pusher_position(pusher_id);

    auto selection_path = m_manager.board().positions_path_to_directions_path(
      m_manager.board().find_jump_path(old_pusher_position, new_pusher_position));

    m_last_move.clear();
    for (const Direction &direction : selection_path) {
      PusherStep pusher_step(direction, false);
      pusher_step.set_is_pusher_selection(true);
      m_last_move.push_back(pusher_step);
    }

    m_selected_pusher = pusher_id;
  }

  void jump(position_t new_position) {
    if (m_pull_count != 0) {
      throw IllegalMoveError("Jumps not allowed after first pull");
    }

    if (m_solving_mode != SolvingMode::REVERSE) {
      throw IllegalMoveError("Jumps allowed only in reverse solving mode");
    }

    position_t old_position = m_manager.pusher_position(m_selected_pusher);
    if (old_position == new_position) { return; }

    try {
      m_manager.move_pusher_from(old_position, new_position);
    } catch (const CellAlreadyOccupiedError &exc) {
      throw IllegalMoveError(exc.what());
    }

    auto path = m_manager.board().positions_path_to_directions_path(
      m_manager.board().find_jump_path(old_position, new_position));
    m_last_move.clear();
    for (const Direction &direction : path) {
      PusherStep pusher_step(direction, false);
      pusher_step.set_is_jump(true);
      pusher_step.set_pusher_id(m_selected_pusher);
      m_last_move.push_back(pusher_step);
    }
  }

  void push_or_move(const Direction &direction, const MoveWorkerOptions &options) {
    position_t initial_pusher_position = m_manager.pusher_position(m_selected_pusher);
    position_t in_front_of_pusher =
      m_manager.board().neighbor(initial_pusher_position, direction);

    if (in_front_of_pusher > Config::MAX_POS) {
      throw IllegalMoveError(
        "Can't move pusher off board! (ID: " + std::to_string(m_selected_pusher) +
        ", direction: " + BaseTessellation::direction_str(direction) + ")");
    }

    bool is_push = false;
    position_t in_front_of_box = numeric_limits<position_t>::max();

    if (m_manager.has_box_on(in_front_of_pusher)) {
      is_push = true;
      in_front_of_box = m_manager.board().neighbor(in_front_of_pusher, direction);
      if (in_front_of_box > Config::MAX_POS) {
        throw IllegalMoveError(
          "Can't push box off board (ID: " +
          std::to_string(m_manager.box_id_on(in_front_of_pusher)) +
          ", direction: " + BaseTessellation::direction_str(direction) + ")");
      }

      try {
        m_manager.move_box_from(in_front_of_pusher, in_front_of_box);
      } catch (const CellAlreadyOccupiedError &exc) {
        throw IllegalMoveError(exc.what());
      }
    }

    try {
      m_manager.move_pusher_from(initial_pusher_position, in_front_of_pusher);
    } catch (const CellAlreadyOccupiedError &exc) {
      throw IllegalMoveError(exc.what());
    }

    PusherStep pusher_step(direction, is_push);
    pusher_step.set_pusher_id(m_selected_pusher);
    if (is_push) {
      pusher_step.set_moved_box_id(m_manager.box_id_on(in_front_of_box));
      if (options.decrease_pull_count && m_pull_count > 0) { m_pull_count -= 1; }
    }
    m_last_move.clear();
    m_last_move.push_back(pusher_step);
  }

  void pull_or_move(const Direction &direction, const MoveWorkerOptions &options) {
    position_t initial_pusher_position = m_manager.pusher_position(m_selected_pusher);
    position_t in_front_of_pusher =
      m_manager.board().neighbor(initial_pusher_position, direction);

    if (in_front_of_pusher > Config::MAX_POS) {
      throw IllegalMoveError(
        "Can't move pusher off board! (ID: " + std::to_string(m_selected_pusher) +
        ", direction: " + BaseTessellation::direction_str(direction) + ")");
    }

    try {
      m_manager.move_pusher_from(initial_pusher_position, in_front_of_pusher);
    } catch (const CellAlreadyOccupiedError &exc) {
      throw IllegalMoveError(exc.what());
    }

    bool is_pull = false;

    if (options.force_pulls) {
      position_t behind_pusher =
        m_manager.board().neighbor(initial_pusher_position, opposite(direction));

      if (behind_pusher <= Config::MAX_POS &&
          m_manager.board().cell(behind_pusher).has_box()) {
        is_pull = true;
        try {
          m_manager.move_box_from(behind_pusher, initial_pusher_position);
        } catch (const CellAlreadyOccupiedError &exc) {
          throw IllegalMoveError(exc.what());
        }
        if (options.increase_pull_count) { m_pull_count += 1; }
      }
    }

    PusherStep pusher_step(direction, is_pull);
    pusher_step.set_pusher_id(m_selected_pusher);
    if (is_pull) {
      pusher_step.set_moved_box_id(m_manager.box_id_on(initial_pusher_position));
    }
    m_last_move.clear();
    m_last_move.push_back(pusher_step);
  }

  void undo_last_move() {
    PusherSteps new_last_moves;
    PusherSteps old_last_moves = m_last_move;

    int jump_key = 0;
    int pusher_change_key = 1;
    int move_key = 2;

    auto key_functor = [&](const PusherStep &elem) {
      if (elem.is_jump()) {
        return jump_key;
      } else if (elem.is_pusher_selection()) {
        return pusher_change_key;
      }
      return move_key;
    };

    reverse(old_last_moves.begin(), old_last_moves.end());
    for (auto &&gb : iter::groupby(old_last_moves, key_functor)) {
      // gb.first -> key
      // gb.second -> values

      if (gb.first == move_key) {
        for (const PusherStep &am : gb.second) {
          undo_pusher_step(am);
          new_last_moves.insert(new_last_moves.end(), m_last_move.begin(),
                                m_last_move.end());
        }
      } else if (gb.first == jump_key) {
        PusherSteps tmp(gb.second.begin(), gb.second.end());
        undo_jump(tmp);
        new_last_moves.insert(new_last_moves.end(), m_last_move.begin(),
                              m_last_move.end());
      } else {
        PusherSteps tmp(gb.second.begin(), gb.second.end());
        undo_pusher_selection(tmp);
        new_last_moves.insert(new_last_moves.end(), m_last_move.begin(),
                              m_last_move.end());
      }
    }

    m_last_move = new_last_moves;
  }

  void undo_pusher_step(const PusherStep &pusher_step) {
    MoveWorkerOptions options;
    if (m_solving_mode == SolvingMode::FORWARD) {
      bool has_box_behind_pusher = m_manager.has_box_on(m_manager.board().neighbor(
        m_manager.pusher_position(m_selected_pusher), pusher_step.direction()));

      if (!pusher_step.is_move() && !has_box_behind_pusher)
        throw IllegalMoveError("Requested push undo, but no box behind pusher!");

      options.force_pulls = !pusher_step.is_move();
      options.increase_pull_count = false;
      pull_or_move(opposite(pusher_step.direction()), options);
    } else {
      options.decrease_pull_count = true;
      push_or_move(opposite(pusher_step.direction()), options);
    }
  }

  void undo_jump(const PusherSteps &jump_moves) {
    Directions path;
    for (const PusherStep &am : jump_moves)
      path.push_back(opposite(am.direction()));
    position_t old_position = m_manager.pusher_position(m_selected_pusher);
    position_t new_position = m_manager.board().path_destination(old_position, path);
    jump(new_position);
  }

  void undo_pusher_selection(const PusherSteps &selection_moves) {
    Directions path;
    for (const PusherStep &am : selection_moves)
      path.push_back(opposite(am.direction()));
    position_t old_position = m_manager.pusher_position(m_selected_pusher);
    position_t new_position = m_manager.board().path_destination(old_position, path);
    select_pusher(m_manager.pusher_id_on(new_position));
  }

protected:
  PIMPL(const PIMPL &) = delete;
  PIMPL &operator=(const PIMPL &) = delete;
};

Mover::Mover(BoardGraph &board, SolvingMode mode)
  : m_impl(std::make_unique<PIMPL>(board, mode)) {}

Mover::Mover(Mover &&) = default;

Mover &Mover::operator=(Mover &&) = default;

Mover::~Mover() = default;

const BoardGraph &Mover::board() const { return m_impl->m_manager.board(); }

SolvingMode Mover::solving_mode() const { return m_impl->m_solving_mode; }

const HashedBoardManager &Mover::board_manager() const { return m_impl->m_manager; }

piece_id_t Mover::selected_pusher() const { return m_impl->m_selected_pusher; }

void Mover::select_pusher(piece_id_t pusher_id) { m_impl->select_pusher(pusher_id); }

void Mover::jump(position_t new_position) { m_impl->jump(new_position); }

void Mover::move(const Direction &direction) {
  PIMPL::MoveWorkerOptions options;
  if (m_impl->m_solving_mode == SolvingMode::FORWARD) {
    options.decrease_pull_count = false;
    m_impl->push_or_move(direction, options);
  } else {
    options.force_pulls = m_impl->m_pulls_boxes;
    options.increase_pull_count = true;
    m_impl->pull_or_move(direction, options);
  }
}

void Mover::undo_last_move() { m_impl->undo_last_move(); }

const PusherSteps &Mover::last_move() const { return m_impl->m_last_move; }

void Mover::set_last_move(const PusherSteps &rv) { m_impl->m_last_move = rv; }

bool Mover::pulls_boxes() const { return m_impl->m_pulls_boxes; }

void Mover::set_pulls_boxes(bool value) { m_impl->m_pulls_boxes = value; }

const BoardGraph &Mover::initial_board() const { return m_impl->m_initial_board; }

} // namespace game
} // namespace sokoengine
