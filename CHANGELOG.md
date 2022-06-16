# Changelog

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
