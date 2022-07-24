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
        "TileShape",
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


@pytest.fixture(scope="session")
def is_running_on_CI():
    return bool(
        os.environ.get("TRAVIS", None) is not None
        or os.environ.get("GITHUB_ACTIONS", None) is not None
    )


@pytest.fixture(scope="session")
def is_CI_job_CPP():
    return is_trueish(os.environ.get("SOKOENGINEPY_EXPECT_CPP", None))


@pytest.fixture(scope="session")
def is_CPP_built_locally():
    src_dir = os.path.abspath(os.path.join(getsourcefile(lambda: 0), "..", "..", "src"))
    ext_built = glob.glob(os.path.join(src_dir, "sokoenginepyext*.so"))
    return bool(ext_built)


@pytest.fixture(scope="session")
def should_be_using_CPP(is_running_on_CI, is_CI_job_CPP, is_CPP_built_locally):
    if is_running_on_CI:
        return is_CI_job_CPP
    else:
        return is_CPP_built_locally


@pytest.fixture(scope="session")
def is_using_CPP():
    return "sokoenginepyext" in sokoenginepy.PusherStep.__module__


class DescribeNativeCppExtension:
    def test_CI_is_correctly_configured(
        self, is_running_on_CI, is_CI_job_CPP, is_using_CPP
    ):
        if not is_running_on_CI:
            return

        if is_CI_job_CPP:
            assert is_using_CPP
        else:
            assert not is_using_CPP

    def it_is_build_and_loaded_if_environment_required_it(
        self, is_using_CPP, should_be_using_CPP
    ):
        if should_be_using_CPP:
            assert is_using_CPP

        if not should_be_using_CPP:
            assert not is_using_CPP

    def it_is_correctly_imported_if_built(
        self, is_using_CPP, ext_members, ext_only_members
    ):
        if not is_using_CPP:
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

    def it_is_not_imported_if_not_built(self, is_using_CPP, ext_members):
        if is_using_CPP:
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
