#!/bin/bash

################################################################################
#
# Builds sokoengeinpyext independently from Python's setuptools. Mainly used to
# test Cmake builds. Also, Ninja is much faster than `python setup.py build_ext`
#
################################################################################

SELF_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)

DEBUG_BUILD_DIR="$SELF_PATH/../cmake_build/debug"
GCC_RELEASE_BUILD_DIR="$SELF_PATH/../cmake_build/release_clang"
CLANG_RELEASE_BUILD_DIR="$SELF_PATH/../cmake_build/release_gcc"

if [ ! -d "$SELF_PATH/../.venv" ]; then
    python3 -m venv .venv
fi
PYTHON_EXECUTABLE="$SELF_PATH/../.venv/bin/python"

if [ ! -d "$DEBUG_BUILD_DIR" ]; then
    mkdir -p "$DEBUG_BUILD_DIR"
    cd "$DEBUG_BUILD_DIR"
    cmake -DCMAKE_INSTALL_PREFIX="/tmp" \
        -DCMAKE_BUILD_TYPE="Debug" \
        -G Ninja \
        -DCMAKE_C_COMPILER=gcc \
        -DCMAKE_CXX_COMPILER="g++" \
        -DPYTHON_EXECUTABLE="$PYTHON_EXECUTABLE" \
        ../../src/libsokoengine
fi

if [ ! -d "$GCC_RELEASE_BUILD_DIR" ]; then
    mkdir -p "$GCC_RELEASE_BUILD_DIR"
    cd "$GCC_RELEASE_BUILD_DIR"
    cmake -DCMAKE_INSTALL_PREFIX="/tmp" \
        -DCMAKE_BUILD_TYPE="RelWithDebInfo" \
        -G Ninja \
        -DCMAKE_C_COMPILER=clang \
        -DCMAKE_CXX_COMPILER="clang++" \
        -DPYTHON_EXECUTABLE="$PYTHON_EXECUTABLE" \
        ../../src/libsokoengine
fi

if [ ! -d "$CLANG_RELEASE_BUILD_DIR" ]; then
    mkdir -p "$CLANG_RELEASE_BUILD_DIR"
    cd "$CLANG_RELEASE_BUILD_DIR"
    cmake -DCMAKE_INSTALL_PREFIX="/tmp" \
        -DCMAKE_BUILD_TYPE="RelWithDebInfo" \
        -G Ninja \
        -DCMAKE_C_COMPILER=clang \
        -DCMAKE_CXX_COMPILER="clang++" \
        -DPYTHON_EXECUTABLE="$PYTHON_EXECUTABLE" \
        ../../src/libsokoengine
fi

# echo "Debug build:"
# cd "$DEBUG_BUILD_DIR"
# ninja sokoenginepyext
# cp src/sokoenginepyext/sokoenginepyext.cpython-36m-x86_64-linux-gnu.so "$SELF_PATH/../src/sokoenginepyext.cpython-36m-x86_64-linux-gnu.debug.so"

# echo "Release build - GCC:"
# cd "$GCC_RELEASE_BUILD_DIR"
# ninja sokoenginepyext
# cp src/sokoenginepyext/sokoenginepyext.cpython-36m-x86_64-linux-gnu.so "$SELF_PATH/../src/sokoenginepyext.cpython-36m-x86_64-linux-gnu.release.gcc.so"

echo "Release build - Clang:"
cd "$CLANG_RELEASE_BUILD_DIR"
ninja sokoenginepyext
cp src/sokoenginepyext/sokoenginepyext.cpython-36m-x86_64-linux-gnu.so "$SELF_PATH/../src/sokoenginepyext.cpython-36m-x86_64-linux-gnu.release.clang.so"

cd "$SELF_PATH/../src"
ln -sf "sokoenginepyext.cpython-36m-x86_64-linux-gnu.release.clang.so" "sokoenginepyext.cpython-36m-x86_64-linux-gnu.so"
