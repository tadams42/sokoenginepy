import glob
import os
from inspect import getsourcefile


def it_is_correctly_using_native_extension(is_using_native):
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
