import os

from setuptools import Extension

_DEBUG = False


def native_extensions():
    libsokoengine = configure_libsokoengine()
    return [libsokoengine] if libsokoengine else []


def configure_libsokoengine():
    # TODO: configure script for native extension should:
    #     - figure out Python version under which we are installing
    #     - find Boost.Python for that version
    #     - be portable

    libraries={
        'Boost.Python': (
            'boost_python-py35'
            if os.path.exists('/usr/lib/x86_64-linux-gnu/libboost_python-py35.so')
            else None
        ),
        'Boost.Graph': (
            'boost_graph'
            if os.path.exists('/usr/lib/x86_64-linux-gnu/libboost_graph.so')
            else None
        )
    }

    extra_compile_args = [
        '-std=c++14',
        '-Wno-overloaded-virtual',
        '-Wno-sign-compare',
        '-Wno-unused-parameter',
        '-Wno-attributes'
    ]

    include_dirs = [
        'lib/libsokoengine/src',
        'lib/libsokoengine/src/board',
        'lib/libsokoengine/src/snapshot',
        'lib/libsokoengine/src/tessellation',
    ]

    sources = [
        'src/ext/export_common.cpp',
        'src/ext/export_atomic_move.cpp',
        'src/ext/export_board_cell.cpp',
        'src/ext/export_direction.cpp',
        'src/ext/export_tessellations.cpp',
        'src/ext/export_libsokoengine.cpp',
        'src/ext/export_board_graph.cpp',
    ] + [
        'lib/libsokoengine/src/board/text_utils.cpp',
        'lib/libsokoengine/src/board/board_cell.cpp',
        'lib/libsokoengine/src/board/board_graph.cpp',
        'lib/libsokoengine/src/snapshot/atomic_move.cpp',
        'lib/libsokoengine/src/tessellation/direction.cpp',
        'lib/libsokoengine/src/tessellation/tessellation_base.cpp',
        'lib/libsokoengine/src/tessellation/tessellation.cpp',
        'lib/libsokoengine/src/tessellation/sokoban_tessellation.cpp',
        'lib/libsokoengine/src/tessellation/hexoban_tessellation.cpp',
        'lib/libsokoengine/src/tessellation/octoban_tessellation.cpp',
        'lib/libsokoengine/src/tessellation/trioban_tessellation.cpp',
    ]

    if _DEBUG:
        extra_compile_args += [
            "-g3", "-O0", "-DDEBUG=1", "-UNDEBUG"
        ]
        undef_macros=["NDEBUG"]

        # ----------------------------------------------------------------------
        # Requires `apt-get install binutils-dev` or `apt-get install libdw-dev`
        # and
        # `#define BACKWARD_HAS_BFD 1` or `#define BACKWARD_HAS_DW 1`
        # ----------------------------------------------------------------------
        if os.path.exists('lib/backward-cpp'):
            libraries['backward_cpp'] = 'bfd'
            sources += ['lib/backward-cpp/backward.cpp']
            include_dirs += ['lib/backward-cpp']
            extra_compile_args += ['-DBACKWARD_HAS_BFD=1']
    else:
        extra_compile_args += ["-DNDEBUG", "-O3"]
        undef_macros = []

    if libraries['Boost.Python'] and libraries['Boost.Graph']:
        return Extension(
            name='libsokoengine',
            sources=sources,
            include_dirs=include_dirs,
            libraries=list(libraries.values()),
            language='c++',
            extra_compile_args=extra_compile_args,
            undef_macros=undef_macros,
            optional=True
        )

    return None
