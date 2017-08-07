import pytest

from sokoenginepy import settings

from .atomic_move_factories import *
from .board_cell_factories import *
from .board_factories import *
from .mover_factories import *
from .snapshot_factories import *


@pytest.fixture(scope='function', autouse=True)
def preserved_settings(request):
    backup_flag1 = settings.OUTPUT_BOARDS_WITH_VISIBLE_FLOORS

    def teardown():
        settings.OUTPUT_BOARDS_WITH_VISIBLE_FLOORS = backup_flag1

    request.addfinalizer(teardown)
