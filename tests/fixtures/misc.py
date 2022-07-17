from pathlib import Path

import pytest
from faker import Faker

from sokoenginepy import PusherStep

_SELF_DIR = Path(__file__).parent.absolute().resolve()


fake = Faker()


@pytest.fixture(scope="session")
def is_using_native():
    return "sokoenginepyext" in PusherStep.__module__


@pytest.fixture(scope="session")
def resources_root():
    return _SELF_DIR
