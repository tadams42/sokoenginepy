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


@pytest.fixture
def io_members():
    return {
        "Collection",
        "Puzzle",
        "PuzzleTypes",
        "Rle",
        "Snapshot",
        "is_blank",
    }


@pytest.fixture
def game_members_both():
    return {
        "AtomicMove",
        "BoardCell",
        "BoardGraph",
        "BoardManager",
        "BoardState",
        "BoxGoalSwitchError",
        "CellAlreadyOccupiedError",
        "CellOrientation",
        "Direction",
        "GraphType",
        "HashedBoardManager",
        "HexobanBoard",
        "HexobanTessellation",
        "IllegalMoveError",
        "Mover",
        "NonPlayableBoardError",
        "OctobanBoard",
        "OctobanTessellation",
        "SokobanBoard",
        "SokobanPlusDataError",
        "SokobanTessellation",
        "SolvingMode",
        "TriobanBoard",
        "TriobanTessellation",
        "VariantBoard",
    }


@pytest.fixture
def game_members_native_only():
    return {
        # Makes no sense in Python layer because board size is not limited (yet) in
        # Python
        "BoardSizeExceededError",
        # Python layer must implement it's own, C++ is exported only because it can't be
        # avoided.
        "CTessellationBase",
        # Mapped to Python KeyError
        "ExtKeyError",
    }


@pytest.fixture
def game_members_py_always():
    # Stuff that is always used from Python implementation, even when native extension
    # is built and loaded
    return {
        "AnyTessellation",
        "COLUMN",
        "DEFAULT_PIECE_ID",
        "JumpCommand",
        "MoveCommand",
        "ROW",
        "SelectPusherCommand",
        "Snapshot",
        "SokobanPlus",
        "Tessellation",
        "TessellationOrDescription",
        "X",
        "Y",
        "index_1d",
        "is_on_board_1d",
        "is_on_board_2d",
    }


class DescribeNativeCppExtension:
    def it_is_build_and_loaded_if_environment_required_it(self, is_using_native):
        building_on_travis = os.environ.get("TRAVIS", None)

        if building_on_travis:
            job_name = os.environ.get("TRAVIS_JOB_NAME", None)

            if job_name and "native extension" in job_name:
                assert os.environ.get("SOKOENGINEPYEXT_BUILD", None) == "true"
                assert is_using_native

            else:
                assert os.environ.get("SOKOENGINEPYEXT_BUILD", None) == "false"
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
        self, is_using_native, io_members, game_members_both, game_members_native_only
    ):
        if not is_using_native:
            return

        for member in io_members:
            assert getattr(io, member).__module__.startswith(
                "sokoenginepyext.io"
            ), f"{member} should've been imported from C++ implementation!"

        for member in game_members_both:
            assert getattr(game, member).__module__.startswith(
                "sokoenginepyext.game"
            ), f"{member} should've been imported from C++ implementation!"

        from sokoenginepyext import game as native_game

        for member in game_members_native_only:
            assert hasattr(
                native_game, member
            ), f"C++ extension should export {member}. Did you change sokoenginepyext code?"

    def it_is_not_imported_if_not_built(
        self, is_using_native, io_members, game_members_both, game_members_native_only
    ):
        if is_using_native:
            return

        for member in io_members:
            assert getattr(io, member).__module__.startswith(
                "sokoenginepy.io"
            ), f"{member} should've been imported from Python implementation!"

        for member in game_members_both:
            assert getattr(game, member).__module__.startswith(
                "sokoenginepy.game"
            ), f"{member} should've been imported from Python implementation!"

    def test_some_things_are_always_used_from_python_implementation(
        self, game_members_py_always
    ):
        for member in game_members_py_always:
            assert hasattr(
                game, member
            ), f"'sokoenginepy.game' package should have {member}!"

            if member not in {"DEFAULT_PIECE_ID"}:
                module_name = getattr(game, member).__module__
                assert (
                    module_name.startswith("sokoenginepy.game")
                    or module_name == "typing"
                ), (
                    f"{member} should be imported from Python implementation even if "
                    "C++ extension is used!"
                )
