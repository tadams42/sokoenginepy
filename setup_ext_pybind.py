import os
import sys

import setuptools
from setuptools import Extension

_DEBUG = False


class pybind11_include_dir(object):
    '''Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. '''

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


def clone_cppitertools(dest):
    cppitertools_dir = os.path.join(os.path.abspath(dest), 'cppitertools')
    if not os.path.exists(cppitertools_dir):
        os.system(
            'git clone https://github.com/ryanhaining/cppitertools.git "{}"'.format(
                cppitertools_dir
            )
        )


def libsokoengine_dirs():
    return [
        'lib/libsokoengine/src',
        'lib/libsokoengine/src/board',
        'lib/libsokoengine/src/game',
        'lib/libsokoengine/src/snapshot',
        'lib/libsokoengine/src/tessellation',
        'lib/libsokoengine/src/utilities',
        'lib/libsokoengine/ext'
    ]


def libsokoengine_sources():
    sources = [
        [
            os.path.join(dir_path, file_name)
            for file_name in os.listdir(dir_path)
            if file_name.endswith('.cpp')
        ]
        for dir_path in libsokoengine_dirs()
    ]
    sources = [item for sublist in sources for item in sublist]
    return sources


def configure():
    on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
    skip = str(
        os.environ.get('SKIP_SOKOENGINEPY_NATIVE_EXTENSION', False)
    ).lower() in ['yes', 'true', 'y']

    if skip or on_rtd:
        return {'ext_modules': [], 'install_requires': []}

    clone_cppitertools('lib/libsokoengine/lib/')

    include_dirs = libsokoengine_dirs() + [
        'lib/libsokoengine/lib/',
        pybind11_include_dir(),
        pybind11_include_dir(user=True)
    ]

    extra_compile_args = ['-std=c++14', '-fvisibility=hidden']

    if _DEBUG:
        extra_compile_args += ['-g3', '-O0']
        extra_link_args = []
        undef_macros=[('NDEBUG',)]
        define_macros=[('DEBUG', '1',)]
    else:
        extra_compile_args += ['-O3', '-flto', '-fno-fat-lto-objects']
        extra_link_args = ['-flto']
        undef_macros=[('DEBUG',)]
        define_macros=[('NDEBUG',)]

    return {
        'ext_modules': [
            Extension(
                name='sokoenginepyext',
                sources=libsokoengine_sources(),
                include_dirs=include_dirs,
                language='c++',
                extra_compile_args=extra_compile_args,
                extra_link_args=extra_link_args,
                undef_macros=undef_macros,
                define_macros=define_macros,
                optional=True
            ),
        ],
        'install_requires': [
            'pybind11>=1.7'
        ]
    }
