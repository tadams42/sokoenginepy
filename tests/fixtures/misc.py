from pathlib import Path

import pytest
from faker import Faker

from sokoenginepy.game import PusherStep

_SELF_DIR = Path(__file__).parent.absolute().resolve()


fake = Faker()


@pytest.fixture(scope="session")
def is_using_native():
    return PusherStep.__module__ == "sokoenginepyext.game"


@pytest.fixture(scope="session")
def resources_root():
    return _SELF_DIR
