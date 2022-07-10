import glob
import inspect
import os
from inspect import getsourcefile

import pytest

from sokoenginepy import game, io


def _get_filtered_members(mdl):
    return {
        name
        for name, obj in inspect.getmembers(mdl)
        if not inspect.ismodule(obj) and not name.startswith("__")
    }


def is_trueish(val):
    return val and str(val).lower() in {"1", "true", "yes", "on"}


@pytest.fixture
def io_members():
    return {
        "CellOrientation",
        "Collection",
        "HexobanPuzzle",
        "HexobanSnapshot",
        "OctobanPuzzle",
        "OctobanSnapshot",
        "Puzzle",
        "Rle",
        "Snapshot",
        "SokobanPuzzle",
        "SokobanSnapshot",
        "TriobanPuzzle",
        "TriobanSnapshot",
    }


@pytest.fixture
def io_members_py_only():
    # Stuff that is always used from Python implementation, even when native extension
    # is built and loaded
    return {
        "is_blank",
    }


@pytest.fixture
def game_members():
    klasses = {
        "BaseTessellation",
        "BoardCell",
        "BoardGraph",
        "BoardManager",
        "BoardState",
        "Direction",
        "Edge",
        "GraphType",
        "HashedBoardManager",
        "HexobanTessellation",
        "Mover",
        "OctobanTessellation",
        "PusherStep",
        "SokobanPlus",
        "SokobanTessellation",
        "SolvingMode",
        "Tessellation",
        "TriobanTessellation",
        "Config",
    }

    exceptions = {
        "BoxGoalSwitchError",
        "CellAlreadyOccupiedError",
        "IllegalMoveError",
        "NonPlayableBoardError",
        "SokobanPlusDataError",
    }

    return klasses.union(exceptions)


@pytest.fixture
def game_members_native_only():
    return {
        # Mapped to Python KeyError
        "PieceNotFoundError",
        # Mapped to Python IndexError
        "InvalidPositionError",
    }


@pytest.fixture
def game_members_py_only():
    # Stuff that is always used from Python implementation, even when native extension
    # is built and loaded
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


def is_CI_cpp_job(job_name):
    return


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
        self, is_using_native, io_members, game_members, game_members_native_only
    ):
        if not is_using_native:
            return

        for member in io_members:
            assert getattr(io, member).__module__.startswith(
                "sokoenginepyext.io"
            ), f"{member} should've been imported from C++ implementation!"

        for member in game_members:
            assert getattr(game, member).__module__.startswith(
                "sokoenginepyext.game"
            ), f"{member} should've been imported from C++ implementation!"

        from sokoenginepyext import game as native_game

        for member in game_members_native_only:
            assert hasattr(
                native_game, member
            ), f"C++ extension should export {member}. Did you change sokoenginepyext code?"

    def it_is_not_imported_if_not_built(
        self, is_using_native, io_members, game_members
    ):
        if is_using_native:
            return

        for member in io_members:
            assert getattr(io, member).__module__.startswith(
                "sokoenginepy.io"
            ), f"{member} should've been imported from Python implementation!"

        for member in game_members:
            assert getattr(game, member).__module__.startswith(
                "sokoenginepy.game"
            ), f"{member} should've been imported from Python implementation!"

    def test_some_things_are_always_used_from_python_implementation(
        self, game_members_py_only, io_members_py_only
    ):
        for member in game_members_py_only:
            assert hasattr(
                game, member
            ), f"'sokoenginepy.game' package should have {member}!"

            module_name = getattr(game, member).__module__
            assert (
                module_name.startswith("sokoenginepy.game") or module_name == "typing"
            ), (
                f"{member} should be imported from Python implementation even if "
                "C++ extension is used!"
            )

        for member in io_members_py_only:
            assert hasattr(
                io, member
            ), f"'sokoenginepy.io' package should have {member}!"

            module_name = getattr(io, member).__module__
            assert (
                module_name.startswith("sokoenginepy.io") or module_name == "typing"
            ), (
                f"{member} should be imported from Python implementation even if "
                "C++ extension is used!"
            )
