#include <sokoengine.hpp>

#include <algorithm>
#include <iostream>

using namespace std;
using namespace sokoengine::game;
using namespace sokoengine::io;

void is_everyone_here() {
  SokobanPuzzle s;
  HexobanPuzzle h;
  TriobanPuzzle t;
  OctobanPuzzle o;

  SokobanTessellation st;
  HexobanTessellation ht;
  TriobanTessellation tt;
  OctobanTessellation ot;

  SokobanSnapshot ss;
  HexobanSnapshot hs;
  TriobanSnapshot ts;
  OctobanSnapshot os;
}

Edge get_one() { return Edge(); }

int main() {
  std::vector<Edge> ev;

  Edge e = get_one();

  return 0;
}
