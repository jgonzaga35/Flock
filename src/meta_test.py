import subprocess
import pytest


def test_black():
    try:
        p = subprocess.Popen(["black", "--check", "."])
    except FileNotFoundError:
        # black can't be (easily?) installed on UNSW's gitlab's runners,
        # because black depends on regex which doesn't have wheels
        # (pre-compiled packages for python) available for the runner's
        # platform. So, pip needs to "compile" regex itself, but regex
        # unfortunately depends on some C code which requires gcc, and that's
        # not avaiable on the runners. So, this test won't run on the pipeline,
        # but it should run on our local machines/vlab
        pytest.skip(
            "black isn't installed, skipping test (you should not guess this warning on your local machine/vlab: pip3 install black)"
        )
        return

    # wait for the process to finish
    p.wait()
    # return code of zero means success
    assert (
        p.returncode == 0
    ), "your python files aren't formated properly. \n\n\n\n Run $ black . \n\n\n"
