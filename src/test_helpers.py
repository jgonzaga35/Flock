import pytest
import re
import signal
from database import database
from auth import auth_register
from subprocess import Popen, PIPE
from time import sleep


def register_n_users(num_users):
    """
    Usage

    >>> single = register_n_users(1)
    >>> usera, userb = register_n_users(2)
    >>> usera, userb, userc = register_n_users(3)
    """
    assert isinstance(num_users, int)

    users = []
    for i in range(num_users):
        users.append(
            auth_register(
                f"email{i}@gmail.com",
                f"passwordthatislongenough{i}",
                f"first{i}",
                f"last{i}",
            )
        )

    if len(users) == 1:
        return users[0]

    # try to make the job of autocompletion engines easier
    assert len(users) == num_users

    return users

def get_user_details_from_user_id(user_id):

    for user in database["users"].values():
        if user_id == user["id"]:
            current_user = user
            break

    return {
        "u_id": current_user["id"],
        "email": current_user["email"],
        "name_first": current_user["first_name"],
        "name_last": current_user["last_name"],
        "handle_str": current_user["handle"]
    }

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    url_re = re.compile(r" \* Running on ([^ ]*)")
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")
