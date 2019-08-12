import glob
import os
from inspect import getsourcefile

import sokoenginepy

from .test_helpers import is_using_native_extension


def it_is_correctly_using_native_extension():
    building_on_travis = os.environ.get("TRAVIS", None)

    if building_on_travis:
        tox_env = os.environ.get("TOXENV", None)
        assert tox_env is not None

        if "native_extension" in tox_env:
            assert os.environ.get("SOKOENGINEPYEXT_BUILD", None) == "yes"
            assert is_using_native_extension()

        else:
            assert os.environ.get("SOKOENGINEPYEXT_BUILD", None) == "no"
            assert not is_using_native_extension()

    else:
        src_dir = os.path.abspath(
            os.path.join(getsourcefile(lambda: 0), "..", "..", "src")
        )
        ext_built = glob.glob(os.path.join(src_dir, "sokoenginepyext*.so"))

        if ext_built:
            assert is_using_native_extension()
        else:
            assert not is_using_native_extension()
