#include "mover.hpp"
#include "variant_board.hpp"
#include "board_cell.hpp"
#include "hashed_board_state.hpp"
#include "cppitertools/groupby.hpp"

#include <algorithm>

using namespace std;
using namespace iter;

namespace sokoengine {

using namespace implementation;

NonPlayableBoardError::NonPlayableBoardError():
  runtime_error("Board is not playable!")
{}

NonPlayableBoardError::~NonPlayableBoardError() = default;


IllegalMoveError::IllegalMoveError(const string& mess):
  runtime_error(mess)
{}

IllegalMoveError::~IllegalMoveError() = default;

class LIBSOKOENGINE_LOCAL Mover::PIMPL {
public:
  VariantBoard::unique_ptr_t m_initial_board;
  HashedBoardState m_state;
  SolvingMode m_solving_mode;
  bool m_pulls_boxes = true;
  piece_id_t m_selected_pusher = DEFAULT_PIECE_ID;
  size_t m_pull_count = 0;
  Mover::Moves m_last_move;

  PIMPL(VariantBoard& board, SolvingMode mode) :
    m_initial_board(board.create_clone()),
    m_state(board),
    m_solving_mode(mode)
  {
    if (!m_state.is_playable()) {
      throw NonPlayableBoardError();
    }

    if(m_solving_mode == SolvingMode::REVERSE) {
      m_state.switch_boxes_and_goals();
    }
  }

  PIMPL(const PIMPL& rv) :
    m_initial_board(rv.m_initial_board->create_clone()),
    m_state(rv.m_state),
    m_solving_mode(rv.m_solving_mode),
    m_pulls_boxes(rv.m_pulls_boxes),
    m_selected_pusher(rv.m_selected_pusher),
    m_pull_count(rv.m_pull_count),
    m_last_move(rv.m_last_move)
  {}

  PIMPL& operator=(const PIMPL& rv) {
    if (this != &rv) {
      m_initial_board = rv.m_initial_board->create_clone();
      m_state = rv.m_state;
      m_solving_mode = rv.m_solving_mode;
      m_pulls_boxes = rv.m_pulls_boxes;
      m_selected_pusher = rv.m_selected_pusher;
      m_pull_count = rv.m_pull_count;
      m_last_move = rv.m_last_move;
    }
    return *this;
  }

  PIMPL(PIMPL&& rv) = default;
  PIMPL& operator=(PIMPL&& rv) = default;

  struct MoveWorkerOptions {
    bool decrease_pull_count;
    bool increase_pull_count;
    bool force_pulls;
  };

  void select_pusher (piece_id_t pusher_id) {
    if (pusher_id == m_selected_pusher)
      return;

    position_t old_pusher_position = m_state.pusher_position(m_selected_pusher);
    position_t new_pusher_position = m_state.pusher_position(pusher_id);

    auto selection_path = m_state.board().positions_path_to_directions_path(
      m_state.board().find_jump_path(old_pusher_position, new_pusher_position)
    );

    m_last_move.clear();
    for (const Direction& direction : selection_path) {
      AtomicMove atomic_move (direction, false);
      atomic_move.set_is_pusher_selection(true);
      m_last_move.push_back(atomic_move);
    }

    m_selected_pusher = pusher_id;
  }

  void jump (position_t new_position) {
    if (m_pull_count != 0) {
      throw IllegalMoveError("Jumps not allowed after first pull");
    }

    if (m_solving_mode != SolvingMode::REVERSE) {
      throw IllegalMoveError("Jumps allowed only in reverse solving mode");
    }

    position_t old_position = m_state.pusher_position(m_selected_pusher);
    if (old_position == new_position) {
      return;
    }

    try {
      m_state.move_pusher_from(old_position, new_position);
    } catch (const CellAlreadyOccupiedError& exc) {
      throw IllegalMoveError(exc.what());
    }

    auto path = m_state.board().positions_path_to_directions_path(
      m_state.board().find_jump_path(old_position, new_position)
    );
    m_last_move.clear();
    for (const Direction& direction : path) {
      AtomicMove atomic_move(direction, false);
      atomic_move.set_is_jump(true);
      atomic_move.set_pusher_id(m_selected_pusher);
      m_last_move.push_back(atomic_move);
    }
  }

  void push_or_move(const Direction& direction, const MoveWorkerOptions& options) {
    position_t initial_pusher_position = m_state.pusher_position(
      m_selected_pusher
    );
    position_t in_front_of_pusher = m_state.board().neighbor(
      initial_pusher_position, direction
    );

    if (in_front_of_pusher == NULL_POSITION) {
      throw IllegalMoveError(
        "Can't move pusher off board! (ID: " +
        std::to_string(m_selected_pusher) + ", direction: " +
        direction.str() + ")"
      );
    }

    bool is_push = false;
    position_t in_front_of_box = NULL_POSITION;

    if (m_state.has_box_on(in_front_of_pusher)) {
      is_push = true;
      in_front_of_box = m_state.board().neighbor(
        in_front_of_pusher, direction
      );
      if (in_front_of_box == NULL_POSITION) {
        throw IllegalMoveError(
          "Can't push box off board (ID: " +
          std::to_string(m_state.box_id_on(in_front_of_pusher)) +
          ", direction: " + direction.str() + ")"
        );
      }

      try {
        m_state.move_box_from(in_front_of_pusher, in_front_of_box);
      } catch (const CellAlreadyOccupiedError& exc) {
        throw IllegalMoveError(exc.what());
      }
    }

    try {
      m_state.move_pusher_from(initial_pusher_position, in_front_of_pusher);
    } catch (const CellAlreadyOccupiedError& exc) {
      throw IllegalMoveError(exc.what());
    }

    AtomicMove atomic_move(direction, is_push);
    atomic_move.set_pusher_id(m_selected_pusher);
    if (is_push) {
      atomic_move.set_moved_box_id(m_state.box_id_on(in_front_of_box));
      if (options.decrease_pull_count && m_pull_count > 0) {
        m_pull_count -= 1;
      }
    }
    m_last_move.clear();
    m_last_move.push_back(atomic_move);
  }

  void pull_or_move(const Direction& direction, const MoveWorkerOptions& options) {
    position_t initial_pusher_position = m_state.pusher_position(
      m_selected_pusher
    );
    position_t in_front_of_pusher = m_state.board().neighbor(
      initial_pusher_position, direction
    );

    if (in_front_of_pusher == NULL_POSITION) {
      throw IllegalMoveError(
        "Can't move pusher off board! (ID: " +
        std::to_string(m_selected_pusher) + ", direction: " +
        direction.str() + ")"
      );
    }

    try {
      m_state.move_pusher_from(initial_pusher_position, in_front_of_pusher);
    } catch (const CellAlreadyOccupiedError& exc) {
      throw IllegalMoveError(exc.what());
    }

    bool is_pull = false;

    if (options.force_pulls) {
      position_t behind_pusher = m_state.board().neighbor(
        initial_pusher_position, direction.opposite()
      );

      if (behind_pusher != NULL_POSITION &&
          m_state.board().cell(behind_pusher).has_box()) {
        is_pull = true;
        try {
          m_state.move_box_from(behind_pusher, initial_pusher_position);
        } catch (const CellAlreadyOccupiedError& exc) {
          throw IllegalMoveError(exc.what());
        }
        if (options.increase_pull_count) {
          m_pull_count += 1;
        }
      }
    }

    AtomicMove atomic_move(direction, is_pull);
    atomic_move.set_pusher_id(m_selected_pusher);
    if (is_pull) {
      atomic_move.set_moved_box_id(m_state.box_id_on(initial_pusher_position));
    }
    m_last_move.clear();
    m_last_move.push_back(atomic_move);
  }

  void undo_last_move() {
    Mover::Moves new_last_moves;
    Mover::Moves old_last_moves = m_last_move;

    int jump_key = 0;
    int pusher_change_key = 1;
    int move_key = 2;

    auto key_functor = [&] (const AtomicMove& elem) {
      if (elem.is_jump()) {
        return jump_key;
      } else if (elem.is_pusher_selection()) {
        return pusher_change_key;
      }
      return move_key;
    };

    reverse(old_last_moves.begin(), old_last_moves.end());
    for (auto&& gb : groupby(old_last_moves, key_functor)) {
      // gb.first -> key
      // gb.second -> values

      if (gb.first == move_key) {
        for (const AtomicMove& am : gb.second) {
          undo_atomic_move(am);
          new_last_moves.insert(
            new_last_moves.end(), m_last_move.begin(), m_last_move.end()
          );
        }
      } else if (gb.first == jump_key) {
        Mover::Moves tmp (gb.second.begin(), gb.second.end());
        undo_jump(tmp);
        new_last_moves.insert(
          new_last_moves.end(), m_last_move.begin(), m_last_move.end()
        );
      } else {
        Mover::Moves tmp (gb.second.begin(), gb.second.end());
        undo_pusher_selection(tmp);
        new_last_moves.insert(
          new_last_moves.end(), m_last_move.begin(), m_last_move.end()
        );
      }
    }

    m_last_move = new_last_moves;
  }

  void undo_atomic_move(const AtomicMove& atomic_move) {
    MoveWorkerOptions options;
    if (m_solving_mode == SolvingMode::FORWARD) {
      bool has_box_behind_pusher = m_state.has_box_on(
        m_state.board().neighbor(
          m_state.pusher_position(m_selected_pusher),
          atomic_move.direction()
        )
      );

      if (!atomic_move.is_move() && !has_box_behind_pusher)
        throw IllegalMoveError("Requested push undo, but no box behind pusher!");

      options.force_pulls = !atomic_move.is_move();
      options.increase_pull_count = false;
      pull_or_move(atomic_move.direction().opposite(), options);
    } else {
      options.decrease_pull_count = true;
      push_or_move(atomic_move.direction().opposite(), options);
    }
  }

  void undo_jump(const Mover::Moves& jump_moves) {
    Directions path;
    for (const AtomicMove& am : jump_moves)
      path.push_back(am.direction().opposite());
    position_t old_position = m_state.pusher_position(m_selected_pusher);
    position_t new_position = m_state.board().path_destination(old_position, path);
    jump(new_position);
  }

  void undo_pusher_selection(const Mover::Moves& selection_moves) {
    Directions path;
    for (const AtomicMove& am : selection_moves)
      path.push_back(am.direction().opposite());
    position_t old_position = m_state.pusher_position(m_selected_pusher);
    position_t new_position = m_state.board().path_destination(old_position, path);
    select_pusher(m_state.pusher_id_on(new_position));
  }
};

Mover::Mover(VariantBoard& board, const SolvingMode& mode) :
  m_impl(std::make_unique<PIMPL>(board, mode))
{}

Mover::Mover(const Mover& rv) :
  m_impl(std::make_unique<PIMPL>(*rv.m_impl))
{}

Mover& Mover::operator=(const Mover& rv) {
  if (this != &rv) {
      m_impl = std::make_unique<PIMPL>(*rv.m_impl);
  }
  return *this;
}

Mover::Mover(Mover &&) = default;

Mover& Mover::operator=(Mover &&) = default;

Mover::~Mover() = default;

const VariantBoard& Mover::board() const { return m_impl->m_state.board(); }

SolvingMode Mover::solving_mode() const { return m_impl->m_solving_mode; }

const HashedBoardState& Mover::state() const { return m_impl->m_state; }

piece_id_t Mover::selected_pusher() const { return m_impl->m_selected_pusher; }

void Mover::select_pusher (piece_id_t pusher_id) {
  m_impl->select_pusher(pusher_id);
}

void Mover::jump( position_t new_position ) { m_impl->jump(new_position); }

void Mover::move( const Direction& direction ) {
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

const Mover::Moves& Mover::last_move() const { return m_impl->m_last_move; }

void Mover::set_last_move(const Moves& rv) { m_impl->m_last_move = rv; }

bool Mover::pulls_boxes() const { return m_impl->m_pulls_boxes; }

void Mover::set_pulls_boxes( bool value ) { m_impl->m_pulls_boxes = value; }

const VariantBoard& Mover::initial_board() const {
  return *(m_impl->m_initial_board);
}

} // namespace sokoengine
