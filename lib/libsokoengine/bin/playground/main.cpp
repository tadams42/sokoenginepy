#include <sokoengine.hpp>

using namespace std;
using namespace sokoengine;

int main() {
  SokobanBoard board(string() +
    "###########\n" +
    "#       **#\n" +
    "#       **#\n" +
    "#  *@   **#\n" +
    "#       **#\n" +
    "###########"
  );

  Mover mover(board);

  Directions moves_cycle = {
    Direction::LEFT, Direction::DOWN, Direction::LEFT, Direction::LEFT,
    Direction::UP, Direction::RIGHT, Direction::DOWN, Direction::RIGHT,
    Direction::RIGHT, Direction::UP
  };

  for(int i = 0; i < 1000; ++i)
    for (const Direction& direction : moves_cycle)
      mover.move(direction);

  return 0;
}
