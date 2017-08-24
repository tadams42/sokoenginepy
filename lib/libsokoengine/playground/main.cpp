#include <sokoengine.hpp>

using namespace std;
using namespace sokoengine;

int main() {
  SokobanBoard forward_board(string() +
    // 12345678
    "#########\n" +  // 0
    "#$  .  .#\n" +  // 1
    "#   @$# #\n" +  // 2
    "#.$    @#\n" +  // 3
    "#########\n"    // 4
  );

  Mover forward_mover(forward_board);

  forward_mover.select_pusher(2);
  forward_mover.undo_last_move();

  auto sp = forward_mover.selected_pusher();

  bool foo = false;

  return 0;
}
