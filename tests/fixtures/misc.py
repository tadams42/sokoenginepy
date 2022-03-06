from pathlib import Path

import pytest
from faker import Faker

from sokoenginepy import AtomicMove

_SELF_DIR = Path(__file__).parent.absolute().resolve()


fake = Faker()


@pytest.fixture(scope="session")
def is_using_native():
    return AtomicMove.__module__ == "sokoenginepyext"


@pytest.fixture(scope="session")
def resources_root():
    return _SELF_DIR
