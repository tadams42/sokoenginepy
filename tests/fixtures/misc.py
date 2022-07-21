from pathlib import Path

import pytest
from faker import Faker


_SELF_DIR = Path(__file__).parent.absolute().resolve()


fake = Faker()


@pytest.fixture(scope="session")
def resources_root():
    return _SELF_DIR
