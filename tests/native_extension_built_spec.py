import glob
import os
from inspect import getsourcefile

import sokoenginepy


def it_is_correctly_using_native_extension():
    building_on_travis = os.environ.get("TRAVIS", None)

    if building_on_travis:
        tox_env = os.environ.get("TOXENV", None)
        assert tox_env is not None

        if "native_extension" in tox_env:
            assert os.environ.get("SOKOENGINEPYEXT_BUILD", None) == "yes"
            assert sokoenginepy.BoardCell.__module__ == "sokoenginepyext"

        else:
            assert os.environ.get("SOKOENGINEPYEXT_BUILD", None) == "no"
            assert "sokoenginepyext" not in sokoenginepy.BoardCell.__module__

    else:
        src_dir = os.path.abspath(
            os.path.join(getsourcefile(lambda: 0), "..", "..", "src")
        )
        ext_built = glob.glob(os.path.join(src_dir, "sokoenginepyext*.so"))

        if ext_built:
            assert sokoenginepy.BoardCell.__module__ == "sokoenginepyext"
        else:
            assert "sokoenginepyext" not in sokoenginepy.BoardCell.__module__
