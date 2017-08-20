# libsokoengine

Sokoban and variants game engine

![Version](http://img.shields.io/badge/version-0.4.3-blue.svg)
[![Language](http://img.shields.io/badge/language-C++11-lightgrey.svg)](http://en.cppreference.com/w/)
[![License](http://img.shields.io/badge/license-GPLv3-brightgreen.svg)](http://opensource.org/licenses/GPL-3.0)

C++ implementation of classic Sokoban game inspired by [SokobanYASC], [JSoko] and [MazezaM] featuring:

  - portable, using C++11 and [boost]
  - supports Sokoban, Hexoban, Trioban and Octoban variants
      - Sokoban+ for all supported variants
      - multiple pushers (Multiban) for all variants
  - two game engine implementations
      - fast and memory lightweight with single step undo/redo
      - somewhat slower and larger with unlimited movement undo/redo
  - reading and writing level collections
      - fully compatible with [SokobanYASC] .sok file format and variants (.xsb, .tsb, .hsb, .txt)
  - self sufficient, clients are not required to link to any dependencies (not even Boost)

## Warning

libsokoengine API is considered unstable and allowed to break until v1.0.0 release is made.

## Install

- [Install](INSTALL.md) - Detailed build and install instructions (including integration with your [CMake] projects, etc...)

Quick and dirty:

```bash
$ git clone --recursive https://github.com/tadams42/sokoenginepy.git
$ cd sokoenginepy && mkdir build && cd build
$ cmake ../
$ make && make install
```

## Usage & Documentation

- [Tutorial] - useful for grasping the big picture view of how stuff works.

Minimal example `main.cpp`:

```C++
#include <sokoengine.hpp>

using namespace sokoengine;

int main() {

  HexobanBoard b;

  return 0;
}
```

## Troubleshooting, issues and bugs

Pull requests and issue reports are welcome and greatly appreciated.

[SokobanYASC]:http://sourceforge.net/projects/sokobanyasc/
[JSoko]:http://www.sokoban-online.de/
[MazezaM]:http://webpages.dcu.ie/~tyrrelma/MazezaM/
[bandit]:http://banditcpp.org/
[boost]:http://www.boost.org/
[Tutorial]:TUTORIAL.md
[CMake]:http://www.cmake.org
