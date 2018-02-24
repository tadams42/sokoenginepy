import os

import setuptools
from setuptools import Extension
import tempfile
from setuptools.command.build_ext import build_ext


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


class SokoenginepyExtension(Extension):
    def __init__(self):
        self._included_boost_headers = None
        super().__init__(
            name='sokoenginepyext',
            sources=self.libsokoengine_sources,
            include_dirs=self.libsokoengine_include_dirs,
            language='c++',
            optional=True
        )

    @property
    def libsokoengine_dirs(self):
        src_dir = 'lib/libsokoengine/src'
        return [src_dir] + [
            os.path.join(src_dir, dir_name)
            for dir_name in os.listdir(src_dir)
            if os.path.isdir(os.path.join(src_dir, dir_name))
        ] + ['lib/libsokoengine/ext']

    @property
    def libsokoengine_sources(self):
        sources = []

        for dir_path in self.libsokoengine_dirs:
            for file_name in os.listdir(dir_path):
                if file_name.endswith('.cpp'):
                    sources.append(os.path.join(dir_path, file_name))

        return sources

    @property
    def libsokoengine_lib_dir(self):
        return 'lib/libsokoengine/lib/'

    @property
    def libsokoengine_include_dirs(self):
        return self.libsokoengine_dirs + [
            self.libsokoengine_lib_dir,
            pybind11_include_dir(),
            pybind11_include_dir(user=True)
        ]

    def fetch_compile_dependencies(self):
        print('Fetching sokoenginepyext compile dependencies...')

        cppitertools_dir = os.path.join(
            os.path.abspath(self.libsokoengine_lib_dir), 'cppitertools'
        )
        if not os.path.exists(cppitertools_dir):
            print('cloning cppitertools...')
            os.system(
                'git clone https://github.com/ryanhaining/cppitertools.git "{}"'.format(
                    cppitertools_dir
                )
            )
        else:
            print('All compile dependencies already present, continuing...')

    @property
    def included_boost_headers(self):
        if self._included_boost_headers is None:
            self._included_boost_headers = []
            for source_path in self.libsokoengine_sources:
                with open(source_path, 'r') as f:
                    self._included_boost_headers += [
                        l.strip()
                        for l in f
                        if l.strip().startswith('#include <boost')
                    ]
            self._included_boost_headers = set(self._included_boost_headers)

        return self._included_boost_headers


class BuildExt(build_ext):
    def __init__(self, *args, **kwargs):
        self._is_debug_build = None
        super().__init__(*args, **kwargs)

    def boost_ok(self, included_boost_headers):
        print("Checking if Boost headers are available...")
        retv = True
        with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
            f.write("\n".join(included_boost_headers) + "\n")
            f.write('int main (int argc, char **argv) { return 0; }')

            try:
                self.compiler.compile([f.name])
            except setuptools.distutils.errors.CompileError:
                retv = False

        return retv

    @property
    def should_build_sokoenginepyext(self):
        on_rtd = str(
            os.environ.get('READTHEDOCS', False)
        ).lower() in ['yes', 'true', 'y', '1']

        build = str(
            os.environ.get('SOKOENGINEPYEXT_BUILD', True)
        ).lower() in ['yes', 'true', 'y', '1']

        if on_rtd:
            print("Not building sokoenginepyext because we are on ReadTheDocs")
        elif not build:
            print(
                "Not building sokoenginepyext because of SOKOENGINEPYEXT_BUILD"
            )

        return build and not on_rtd

    @property
    def sokoenginepyext_extra_compile_args(self):
        retv = ['-std=c++14', '-Wno-sign-compare', '-fvisibility=hidden']

        if self.is_debug_build:
            retv += ['-g3', '-O0', '-UNDEBUG', '-DDEBUG']
        else:
            retv += ['-O3', '-flto']

        return retv

    @property
    def sokoenginepyext_extra_link_args(self):
        if self.is_debug_build:
            return []
        else:
            return ['-flto']

    @property
    def is_debug_build(self):
        if self._is_debug_build is None:
            self._is_debug_build = str(
                os.environ.get('SOKOENGINEPYEXT_DEBUG', False)
            ).lower() in ['yes', 'true', 'y', '1']

            if self._is_debug_build:
                print("Building native extensions in DEBUG mode")

        return self._is_debug_build

    def build_extension(self, ext):
        if ext.name == 'sokoenginepyext':
            # `python setup.py install` will try to build wheels before it
            # installs packages from `setup_requires`. This will always fail
            # unless there is pybind11 already installed.
            # So we employ this dirty hack that could potentially break many
            # builds that don't rely on pip.
            # No known way around it.
            os.system('pip install "pybind11>=2.2.0"')
            ext.fetch_compile_dependencies()
            ext.extra_compile_args = self.sokoenginepyext_extra_compile_args
            ext.extra_link_args = self.sokoenginepyext_extra_link_args

        return super().build_extension(ext)

    def build_extensions(self):
        should_remove_sokoenginepyext = not self.should_build_sokoenginepyext

        if not should_remove_sokoenginepyext:
            boost_ok = False
            for ext in self.extensions:
                if ext.name == 'sokoenginepyext':
                    boost_ok = self.boost_ok(ext.included_boost_headers)

            if not boost_ok:
                print(
                    "Not building sokoenginepyext because Boost headers not"
                    " found"
                )
                should_remove_sokoenginepyext = True

        if should_remove_sokoenginepyext:
            self.extensions = [
                ext for ext in self.extensions if ext.name != 'sokoenginepyext'
            ]

        return super().build_extensions()
