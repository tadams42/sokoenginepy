import os

import setuptools

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import ParallelCompile, Pybind11Extension, naive_recompile


class SokoenginepyextOptions:
    """
    Describes ``sokoenginepyext`` native C++ extension for ``sokoenginepy``.

    On ``Linux``, ``pip install sokoenginepy`` will try to configure and build native
    extension. If build fails, ``sokoenginepy`` will be installed without native
    extension. To succeed, boost header have to be in system include path.

    On all other systems, native extension will not be installed.
    """

    NAME = "sokoenginepyext"

    SHOULD_TRY_BUILD = (
        # We support building only on Linux...
        os.name == "posix"
        # ... and not on Read The Docs
        and os.environ.get("READTHEDOCS", "false").lower()
        not in ["yes", "true", "y", "1"]
        # ... and allow build to be controlled by SOKOENGINEPYEXT_BUILD
        # environment variable
        and os.environ.get("SOKOENGINEPYEXT_BUILD", "true").lower()
        in ["yes", "true", "y", "1"]
    )

    IS_DEBUG = os.environ.get("SOKOENGINEPYEXT_DEBUG", "false").lower() in [
        "yes",
        "true",
        "y",
        "1",
    ]

    CXXFLAGS_RELEASE = ["-O3", "-flto", "-UDEBUG", "-DNDEBUG"]
    CXXFLAGS_DEBUG = ["-g3", "-O0", "-UNDEBUG", "-DDEBUG"]
    CXXFLAGS = [
        "-fPIC",
        "-DBOOST_BIND_NO_PLACEHOLDERS",
        "-DBOOST_MULTI_INDEX_DISABLE_SERIALIZATION",
    ] + (CXXFLAGS_DEBUG if IS_DEBUG else CXXFLAGS_RELEASE)

    LDFLAGS = ["-flto"] if not IS_DEBUG else []

    SOURCES = sorted(
        [
            os.path.join(dir_path, file_name)
            for _ in ["src/libsokoengine", "src/sokoenginepyext"]
            for dir_path, directories, files in os.walk(_)
            for file_name in files
            if file_name.endswith(".cpp")
        ]
    )

    INCLUDE_DIRS = ["/tmp/cmake_cache"] + [
        dir_path
        for _ in ["src/libsokoengine", "src/sokoenginepyext"]
        for dir_path, directories, files in os.walk(_)
    ]

    CPPITERTOOLS_DIR = os.path.abspath("/tmp/cmake_cache/cppitertools")

    @classmethod
    def fetch_cppitertools(cls):
        if not os.path.exists(cls.CPPITERTOOLS_DIR):
            print("Cloning cppitertools...")
            os.system(
                'git clone --branch v1.0 https://github.com/ryanhaining/cppitertools.git "{}"'.format(
                    cls.CPPITERTOOLS_DIR
                )
            )
        return True


if SokoenginepyextOptions.SHOULD_TRY_BUILD:
    SokoenginepyextOptions.fetch_cppitertools()
    ParallelCompile("NPY_NUM_BUILD_JOBS", needs_recompile=naive_recompile).install()
    ext = Pybind11Extension(
        name=SokoenginepyextOptions.NAME,
        sources=SokoenginepyextOptions.SOURCES,
        include_dirs=SokoenginepyextOptions.INCLUDE_DIRS,
        optional=True,
        cxx_std=14,
        extra_compile_args=SokoenginepyextOptions.CXXFLAGS,
        extra_link_args=SokoenginepyextOptions.LDFLAGS,
        # Example: passing in the version to the compiled code
        # define_macros=[("VERSION_INFO", __version__)],
    )
    setuptools.setup(ext_modules=[ext])

else:
    setuptools.setup()
