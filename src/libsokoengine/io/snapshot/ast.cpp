#include "ast.hpp"

#include "pusher_step.hpp"
#include "snapshot.hpp"
#include "tessellation.hpp"

#include <algorithm>

namespace sokoengine {
namespace io {
namespace snapshot_parsing {
namespace evaluated_ast {

using namespace std;
using game::BaseTessellation;

LIBSOKOENGINE_LOCAL Converted converted(const string &data,
                                        const BaseTessellation &tessellation) {
  Converted retv;

  for (char c : data) {
    if (c == Snapshot::CURRENT_POSITION_CH) {
      if (retv.size() > 0) retv.back().set_is_current_pos(true);
    } else {
      retv.insert(retv.end(), 1, tessellation.char_to_pusher_step(c));
    }
  }

  return retv;
}

size_t Steps::pushes_count() const {
  return count_if(data.cbegin(), data.cend(),
                  [](char c) { return Snapshot::is_push_step(c); });
}

size_t Steps::moves_count() const {
  return count_if(data.cbegin(), data.cend(),
                  [](char c) { return Snapshot::is_move_step(c); });
}

const string &Steps::to_str() const { return data; }

Converted Steps::pusher_steps(const BaseTessellation &tessellation) const {
  return converted(data, tessellation);
}

size_t Jump::pushes_count() const { return 0; }

size_t Jump::moves_count() const {
  return count_if(data.cbegin(), data.cend(),
                  [](char c) { return Snapshot::is_move_step(c); });
}

string Jump::to_str() const {
  return string(1, Snapshot::JUMP_BEGIN) + data + Snapshot::JUMP_END;
}

Converted Jump::pusher_steps(const BaseTessellation &tessellation) const {
  Converted retv = converted(data, tessellation);
  for (auto &s : retv)
    s.set_is_jump(true);
  return retv;
}

size_t PusherSelection::pushes_count() const { return 0; }

size_t PusherSelection::moves_count() const { return 0; }

string PusherSelection::to_str() const {
  return string(1, Snapshot::PUSHER_CHANGE_BEGIN) + data + Snapshot::PUSHER_CHANGE_END;
}

Converted PusherSelection::pusher_steps(const BaseTessellation &tessellation) const {
  Converted retv = converted(data, tessellation);
  for (auto &s : retv)
    s.set_is_pusher_selection(true);
  return retv;
}

} // namespace evaluated_ast
} // namespace snapshot_parsing
} // namespace io
} // namespace sokoengine
