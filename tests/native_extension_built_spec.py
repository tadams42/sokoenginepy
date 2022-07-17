import glob
import inspect
import os
from inspect import getsourcefile

import pytest

import sokoenginepy


def _get_filtered_members(mdl):
    return {
        name
        for name, obj in inspect.getmembers(mdl)
        if not inspect.ismodule(obj) and not name.startswith("__")
    }


def is_trueish(val):
    return val and str(val).lower() in {"1", "true", "yes", "on"}


@pytest.fixture
def ext_members():
    return {
        "BoardCell",
        "BoardGraph",
        "BoardManager",
        "BoardState",
        "BoxGoalSwitchError",
        "CellAlreadyOccupiedError",
        "CellOrientation",
        "Collection",
        "Config",
        "Direction",
        "Edge",
        "HashedBoardManager",
        "IllegalMoveError",
        "Mover",
        "NonPlayableBoardError",
        "PusherStep",
        "Puzzle",
        "Rle",
        "Snapshot",
        "SokobanPlus",
        "SokobanPlusDataError",
        "SolvingMode",
        "Tessellation",
    }


@pytest.fixture
def py_only_members():
    return {
        "index_1d",
        "index_column",
        "index_row",
        "index_x",
        "index_y",
        "is_on_board_1d",
        "is_on_board_2d",
        "JumpCommand",
        "MoveCommand",
        "SelectPusherCommand",
    }


@pytest.fixture
def ext_only_members():
    return {
        # Mapped to Python KeyError
        "PieceNotFoundError",
        # Mapped to Python IndexError
        "InvalidPositionError",
    }


class DescribeNativeCppExtension:
    def it_is_build_and_loaded_if_environment_required_it(self, is_using_native):
        running_on_ci = (
            os.environ.get("TRAVIS", None) is not None
            or os.environ.get("GITHUB_ACTIONS", None) is not None
        )

        ci_job_name = os.environ.get("TRAVIS_JOB_NAME", None) or os.environ.get(
            "GITHUB_JOB", None
        )

        is_CI_cpp_job = ci_job_name and any(
            ["with C++ extension" in ci_job_name, "with_cpp_extension" in ci_job_name]
        )

        if running_on_ci:
            if is_CI_cpp_job:
                assert not is_trueish(
                    os.environ.get("SOKOENGINEPYEXT_SKIP", None)
                ), f"SOKOENGINEPYEXT_SKIP should be false-ish or not set (for job {ci_job_name})"
                assert is_using_native

            else:
                assert is_trueish(os.environ.get("SOKOENGINEPYEXT_SKIP", None))
                assert not is_using_native

        else:
            src_dir = os.path.abspath(
                os.path.join(getsourcefile(lambda: 0), "..", "..", "src")
            )
            ext_built = glob.glob(os.path.join(src_dir, "sokoenginepyext*.so"))

            if ext_built:
                assert is_using_native
            else:
                assert not is_using_native

    def it_is_correctly_imported_if_built(
        self, is_using_native, ext_members, ext_only_members
    ):
        if not is_using_native:
            return

        for member in ext_members:
            assert getattr(sokoenginepy, member).__module__.startswith(
                "sokoenginepyext"
            ), f"{member} should've been imported from C++ implementation!"

        import sokoenginepyext

        for member in ext_only_members:
            assert hasattr(
                sokoenginepyext, member
            ), f"C++ extension should export {member}. Did you change sokoenginepyext code?"

    def it_is_not_imported_if_not_built(self, is_using_native, ext_members):
        if is_using_native:
            return

        for member in ext_members:
            assert getattr(sokoenginepy, member).__module__.startswith(
                "sokoenginepy."
            ), f"{member} should've been imported from Python implementation!"

    def test_some_things_are_always_used_from_python_implementation(
        self, py_only_members
    ):
        for member in py_only_members:
            assert hasattr(
                sokoenginepy, member
            ), f"'sokoenginepy' package should have {member}!"

            module_name = getattr(sokoenginepy, member).__module__
            assert module_name.startswith("sokoenginepy.") or module_name == "typing", (
                f"{member} should be imported from Python implementation even if "
                "C++ extension is used!"
            )
