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

    cppitertools_dir = os.path.abspath('lib/libsokoengine/lib/cppitertools')
    if not os.path.exists(cppitertools_dir):
        os.system(
            'git clone https://github.com/ryanhaining/cppitertools.git "{}"'.format(
                cppitertools_dir
            )
        )

    extra_compile_args = [
        '-std=c++14',
        '-Wno-overloaded-virtual',
        '-Wno-sign-compare',
        '-Wno-unused-parameter',
        '-Wno-attributes'
    ]

    include_dirs = [
        'lib',
        'lib/libsokoengine/lib',
        'lib/libsokoengine/src',
        'lib/libsokoengine/src/board',
        'lib/libsokoengine/src/game',
        'lib/libsokoengine/src/snapshot',
        'lib/libsokoengine/src/tessellation',
    ]

    sources = [
        [
            os.path.join(dir_path, file_name)
            for file_name in os.listdir(dir_path)
            if file_name.endswith(".cpp")
        ]
        for dir_path in [
            'src/ext/',
            'lib/libsokoengine/src/board/',
            'lib/libsokoengine/src/game/',
            'lib/libsokoengine/src/snapshot/',
            'lib/libsokoengine/src/tessellation/',
        ]
    ]
    sources = [item for sublist in sources for item in sublist]

    if _DEBUG:
        extra_compile_args += ["-g3", "-O0", "-DDEBUG=1", "-UNDEBUG"]
        undef_macros=["NDEBUG"]
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
