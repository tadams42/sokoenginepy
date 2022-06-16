#include <sokoengine.hpp>

#include <iostream>
#include <algorithm>

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

int main() {
  is_everyone_here();

  return 0;
}
