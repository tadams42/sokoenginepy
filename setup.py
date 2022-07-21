import os
import re
import subprocess
import sys
from typing import List, Optional, Tuple

import pybind11
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


class Sokoenginepyext(Extension):
    """
    Native extension buildable via CMakeBuild.

    A cmake extension uses a ``sourcedir`` instead of a file list.
    The name must be the _single_ output extension from the CMake build.

    Adapted from https://github.com/pybind/cmake_example

    Requirements:

    - cmake must be installed and in ``PATH``
    - ``vcpkg`` must be installed and there must be environment variable
      ``CMAKE_TOOLCHAIN_FILE`` set to absolute path to ``vcpkg.cmake``

    Optional env variables:

    - ``READTHEDOCS``           - if set, extension is not built
    - ``SOKOENGINEPYEXT_SKIP``  - if set to true-ish value, extension is not built
    - ``SOKOENGINEPYEXT_DEBUG`` - if set to true-ish value, compilation produces non
                                  optimized binary
    """

    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

    @classmethod
    def should_try_build(cls) -> bool:
        return (
            not cls._is_on_readthedocs()
            and not cls._env_skips_build()
            and cls._is_vcpkg_configured()
        )

    @classmethod
    def cmake_args(
        cls,
        extdir: str,
        is_msvc_compiler: bool,
        plat_name: str,
        parallel: Optional[int],
    ) -> Tuple[List[str], List[str]]:
        if is_msvc_compiler:
            config_args, build_args = cls._msvc_args(plat_name, extdir)
        else:
            config_args, build_args = cls._non_msvc_args()

        config_args = (
            [
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
                f"-DPython3_EXECUTABLE={sys.executable}",
                # We need to inject this into cmake config because `pip install` creates
                # separate, clean build environment (ie. /tmp/pip-build-env-HASH) which is
                # impossible to detect by cmake
                # Luckily, in cmake we don't need whole pip environment, only location of
                # Find_pybind11 cmake module. Also luckily, pybind11 provides helper just
                # for that purpose.
                f"-DPYBIND11_CMAKE_DIR={pybind11.get_cmake_dir()}",
                f"-DCMAKE_BUILD_TYPE={cls._cmake_build_type()}",  # not used on MSVC, but no harm
                f"-DCMAKE_TOOLCHAIN_FILE={cls._vcpkg_toolchain_file()}",
            ]
            + config_args
            + cls._env_cmake_args()
        )

        if sys.platform.startswith("darwin"):
            # Cross-compile support for macOS - respect ARCHFLAGS if set
            archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
            if archs:
                config_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]

        # Set CMAKE_BUILD_PARALLEL_LEVEL to control the parallel build level across all
        # generators.
        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            if parallel:
                # CMake 3.12+ only.
                build_args += [f"-j{parallel}"]

        build_args = ["--target", "sokoenginepyext"] + build_args

        return config_args, build_args

    @classmethod
    def _non_msvc_args(cls) -> Tuple[List[str], List[str]]:
        config_args = []
        build_args = []

        env_generator = cls._env_cmake_generator()

        # Defaulting to Ninja-build since it a) is available as a wheel and b)
        # multithreads automatically.

        if not env_generator or env_generator == "Ninja":
            try:
                import ninja  # noqa: F401

                ninja_executable_path = os.path.join(ninja.BIN_DIR, "ninja")
                config_args += [
                    "-GNinja",
                    f"-DCMAKE_MAKE_PROGRAM:FILEPATH={ninja_executable_path}",
                ]
            except ImportError:
                pass

        return config_args, build_args

    @classmethod
    def _msvc_args(cls, plat_name: str, extdir: str) -> Tuple[List[str], List[str]]:
        config_args = []
        build_args = []

        env_generator = cls._env_cmake_generator()

        if not env_generator:
            # Assume we are using default generator on Windows
            # Which one can't be known at the time this method is called because it
            # depends on how MS toolset was installed:
            #   - Visual Studio is installed -> generator will be Visual Studio
            #     multi-config
            #   - Only command line build tools are installed -> generator will be
            #     single config ()
            #   - anything in between...
            #
            # We could force using Ninja generator here but, ninja + MS compiler would
            # require all variables be exported for Ninja to pick it up, which is a
            # little tricky to do.

            single_config = False
            contains_arch = False

        else:
            single_config = any(x in env_generator for x in {"NMake", "Ninja"})
            # CMake allows an arch-in-generator style for backward compatibility
            contains_arch = any(x in env_generator for x in {"ARM", "Win64"})

        # Specify the arch if using MSVC generator, but only if it doesn't contain a
        # backward-compatibility arch spec already in the generator name.
        if not single_config and not contains_arch:
            config_args += ["-A", cls._PLAT_TO_CMAKE[plat_name]]

        # Multi-config generators have a different way to specify configs
        if not single_config:
            config_args += [
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cls._cmake_build_type().upper()}={extdir}"
            ]
            build_args += ["--config", cls._cmake_build_type()]

        return config_args, build_args

    @classmethod
    def _is_trueish(cls, val) -> bool:
        return val and str(val).lower() in {"1", "true", "yes", "on"}

    @classmethod
    def _is_on_readthedocs(cls) -> bool:
        return os.environ.get("READTHEDOCS", None) is not None

    @classmethod
    def _env_skips_build(cls) -> bool:
        return cls._is_trueish(os.environ.get("SOKOENGINEPYEXT_SKIP", None))

    @classmethod
    def _is_env_debug_build(cls) -> bool:
        return cls._is_trueish(os.environ.get("SOKOENGINEPYEXT_DEBUG", None))

    @classmethod
    def _is_vcpkg_configured(cls) -> bool:
        val = cls._vcpkg_toolchain_file()
        return bool(val and val.endswith("vcpkg.cmake") and os.path.exists(val))

    @classmethod
    def _vcpkg_toolchain_file(cls) -> Optional[str]:
        return os.environ.get("CMAKE_TOOLCHAIN_FILE", None)

    @classmethod
    def _cmake_build_type(cls) -> str:
        return "Debug" if cls._is_env_debug_build() else "Release"

    @classmethod
    def _env_cmake_generator(cls) -> str:
        # CMake lets you override the generator - we need to check this.
        # Can be set with Conda-Build, for example.
        return os.environ.get("CMAKE_GENERATOR", "")

    @classmethod
    def _env_cmake_args(cls) -> List[str]:
        retv = []
        # CMake arguments set as environment variable (needed e.g. to build for ARM OSx
        # on conda-forge)
        if "CMAKE_ARGS" in os.environ:
            retv = [item for item in os.environ["CMAKE_ARGS"].split(" ") if item]

        return retv

    # Convert distutils Windows platform specifiers to CMake -A arguments
    _PLAT_TO_CMAKE = {
        "win32": "Win32",
        "win-amd64": "x64",
        "win-arm32": "ARM",
        "win-arm64": "ARM64",
    }


class CMakeBuild(build_ext):
    """
    Adapted from https://github.com/pybind/cmake_example
    """

    # Convert distutils Windows platform specifiers to CMake -A arguments
    PLAT_TO_CMAKE = {
        "win32": "Win32",
        "win-amd64": "x64",
        "win-arm32": "ARM",
        "win-arm64": "ARM64",
    }

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        # required for auto-detection & inclusion of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        # self.parallel is a Python 3 only way to set parallel jobs by hand
        # using -j in the build_ext call, not supported by pip or PyPA-build.
        parallel = self.parallel if hasattr(self, "parallel") else None

        cmake_config_args, cmake_build_args = Sokoenginepyext.cmake_args(
            extdir, self.compiler.compiler_type == "msvc", self.plat_name, parallel
        )

        build_temp = os.path.join(self.build_temp, ext.name)
        if not os.path.exists(build_temp):
            os.makedirs(build_temp)

        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_config_args, cwd=build_temp
        )
        subprocess.check_call(
            ["cmake", "--build", "."] + cmake_build_args, cwd=build_temp
        )


if Sokoenginepyext.should_try_build():
    setup(
        ext_modules=[Sokoenginepyext("sokoenginepyext")],
        cmdclass={"build_ext": CMakeBuild},
    )

else:
    setup()
