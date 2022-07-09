# Changelog

## 1.0.2 (unreleased)

- added: `BoardGraph.cell_orientation()`
- build: optimized Python C++ extension binary size

## 1.0.1 (2022-07-08)

- added: `BoardGraph.wall_neighbor_directions()`
- added: `Puzzle.has_sokoban_plus`
- renamed: `Collection.save()` -> `Collection.dump()`
- changed: `Collection.dump()` can now save to IO streams (previously it could only save
  to file path)
- changed: `Collection.load()` can now load from IO streams (previously it could only load
  from file path)
- added: `Collection.loads()` and `Collection.dumps()`
- changed: `Collection.notes`, `Puzzle.notes` and `Snapshot.notes` are now ordinary
  strings (instead of list of strings)
- build: `pip` and `python -m build` now use `cmake` instead of `distutils`
- build: `vcpkg` is used for all C++ dependencies

## 1.0.0 (2022-06-20)

- renamed `DEFAULT_PIECE_ID` -> `DEFAULT_ID`
- renamed index functions
  - `X()` -> `index_x()`
  - `Y()` -> `index_y()`
  - `ROW()` -> `index_row()`
  - `COLUMN()` -> `index_column()`
- replaced use of `None` in method arguments and returned values with explicit constants
  - ie. `BoardGraph.neighbor()` now always returns `int` and instead of `None` it
    returns `Config.NO_POS`.
  - this makes APIs easier to use and pybind11 bridge more efficient (because pybind11
    doesn't need to handle `None`)
- simplified `PusherStep`
  - signaling box movement is now done by single attribute, `moved_box_id`
  - added explicit constant for "no piece ID is present" situations (`Config.NO_ID`)
- improved docs and tests, mainly on the front of exceptions
- fix: in many places we now check for negative values and raise early
  - having ie. negative board width not only makes no sense, but is completely
    impossible to pass into C++ layer where board with type is strictly defined and
    is using unsigned integer

## 0.6.0 (2022-06-16)

- massive refactoring and cleanup or public API
- updated .sok format reader to v0.19
- cleanly separated I/O from game engine (both architecturally and in implementation)
  - `VariantBoard` monstrosity is gone
  - Tessellation selection via inelegant and unsafe strings is gone
- replaced hand written parsers with Boost.X3 on C++ side and Lark on Python side
- implemented parts of I/O that were missing on C++ side
  - Python doesn't really need I/O speedup here, but it was missing part of
    libsokoengine C++
  - consequently, to be able to test C++ I/O implementation, it was exported into Python
    and is used alongside other parts of native extension

## 0.5.4 (2022-03-06)

- improved build process for Python native extension

## 0.5.3 (2018-02-24)

- Documentation and build fixes

## 0.5.2 (2017-09-03)

- Improved native extension build configuration process.
- Upgraded to pybind11 v2.2.0

## 0.5.1 (2017-08-31)

- Switched from Boost.Python to pybind11 in C++ extension

## 0.5.0 (2017-08-25)

- added optional C++ native extension (Boost.Graph, Boost.Python)
