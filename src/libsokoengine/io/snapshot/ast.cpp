/// @file
#include "ast.hpp"

#include "characters.hpp"
#include "pusher_step.hpp"
#include "tessellation_impl.hpp"

#include <algorithm>

using sokoengine::implementation::Characters;
using sokoengine::implementation::TessellationImpl;
using std::string;

namespace sokoengine {
  namespace io {
    namespace snapshot_parsing {
      namespace evaluated_ast {

        LIBSOKOENGINE_LOCAL Converted
        converted(const string &data, const TessellationImpl &tessellation) {
          Converted retv;

          for (char c : data) {
            if (c == Characters::CURRENT_POSITION_CH) {
              if (retv.size() > 0)
                retv.back().set_is_current_pos(true);
            } else {
              retv.insert(retv.end(), 1, tessellation.char_to_pusher_step(c));
            }
          }

          return retv;
        }

        size_t Steps::pushes_count() const {
          return count_if(data.cbegin(), data.cend(), [](char c) {
            return Characters::is_push_step(c);
          });
        }

        size_t Steps::moves_count() const {
          return count_if(data.cbegin(), data.cend(), [](char c) {
            return Characters::is_move_step(c);
          });
        }

        const string &Steps::to_str() const { return data; }

        Converted Steps::pusher_steps(const TessellationImpl &tessellation) const {
          return converted(data, tessellation);
        }

        size_t Jump::pushes_count() const { return 0; }

        size_t Jump::moves_count() const {
          return count_if(data.cbegin(), data.cend(), [](char c) {
            return Characters::is_move_step(c);
          });
        }

        string Jump::to_str() const {
          return string(1, Characters::JUMP_BEGIN) + data + Characters::JUMP_END;
        }

        Converted Jump::pusher_steps(const TessellationImpl &tessellation) const {
          Converted retv = converted(data, tessellation);
          for (auto &s : retv)
            s.set_is_jump(true);
          return retv;
        }

        size_t PusherSelection::pushes_count() const { return 0; }

        size_t PusherSelection::moves_count() const { return 0; }

        string PusherSelection::to_str() const {
          return string(1, Characters::PUSHER_CHANGE_BEGIN) + data
               + Characters::PUSHER_CHANGE_END;
        }

        Converted PusherSelection::pusher_steps(const TessellationImpl &tessellation
        ) const {
          Converted retv = converted(data, tessellation);
          for (auto &s : retv)
            s.set_is_pusher_selection(true);
          return retv;
        }

      } // namespace evaluated_ast
    }   // namespace snapshot_parsing
  }     // namespace io
} // namespace sokoengine
