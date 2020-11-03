import requests
import pytest
import re
import signal
from database import database
from auth import auth_register, auth_get_current_user_id_from_token
from subprocess import Popen, PIPE
from time import sleep


def register_n_users(num_users, *, include_admin=False):
    """
    If include_admin is False, returns n *regular* users (the admin is discarded).
    Else, it the admin user PLUS n - 1 *regular* users (n users total)

    Usage

    >>> single = register_n_users(1)
    >>> usera, userb = register_n_users(2)
    >>> usera, userb, userc = register_n_users(3)

    Returned user format:
    >>> {
        'token':
        'u_id':
    }
    """
    assert isinstance(num_users, int)

    users = []
    # register the admin user (the first user has admin privileges)
    admin = auth_register(
        "admin@gmail.com", "admin password that is long", "My name is", "admin"
    )
    if include_admin:
        users.append(admin)
        num_users -= 1

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

    return users


def get_user_details_from_user_id(user_id):
    """
    Returns a user_detail from user_id:
    >>> {
        "u_id": current_user["id"],
        "email": current_user["email"],
        "name_first": current_user["first_name"],
        "name_last": current_user["last_name"],
        "handle_str": current_user["handle"],
    }
    """
    for user in database["users"].values():
        if user_id == user["id"]:
            current_user = user
            break

    return {
        "u_id": current_user["id"],
        "email": current_user["email"],
        "name_first": current_user["first_name"],
        "name_last": current_user["last_name"],
        "handle_str": current_user["handle"],
    }


def assert_contains_users_id(user_details, expected_user_ids):
    """
    Checks whether the expected users' id are in the users details list.

    >>> user_details = channel_details(token, channel_id)['all_members']
    >>> expected_members_id = [usera['u_id'], userb['u_id']]
    >>> assert_contains_users_id(user_details, expected_members_id)
    """

    assert len(user_details) == len(
        expected_user_ids
    ), f"expect {len(expected_user_ids)} users, but got {len(user_details)}"

    for user in user_details:
        assert (
            user["u_id"] in expected_user_ids
        ), f"channel contains unexpected user {user['u_id']}"
        expected_user_ids.remove(user["u_id"])
    assert (
        len(expected_user_ids) == 0
    ), f"users ${expected_user_ids} where not found in the channel"


def http_register_n_users(url, num_users, include_admin=False):
    """Same thing as register_n_users, except it goes through the web server"""
    assert isinstance(num_users, int)

    users = []
    response = requests.post(
        url + "auth/register",
        json={
            "email": f"admin@gmail.com",
            "password": f"admin long enough password",
            "name_first": "hello",
            "name_last": "world",
        },
    )
    assert response.status_code == 200
    if include_admin:
        user_infos = response.json()
        users.append(user_infos)
        num_users -= 1

    for i in range(num_users):
        response = requests.post(
            url + "auth/register",
            json={
                "email": f"email{i}@gmail.com",
                "password": f"passwordthatislongenough{i}",
                "name_first": f"first{i}",
                "name_last": f"last{i}",
            },
        )
        assert response.status_code == 200  # everything went well

        user_infos = response.json()
        assert "u_id" in user_infos
        assert "token" in user_infos
        users.append(user_infos)

    if len(users) == 1:
        return users[0]

    return users


def is_user_reacted(token, channel_id, message_id, react_id):
    """
    Ensure that a authorized user has reacted to a certain message with
    specific react_id
    """
    # Assume channel_id and message_id are valid
    assert channel_id in database["channels"]
    assert message_id in database["channels"][channel_id]["messages"]
    message = database["channels"][channel_id]["messages"][message_id]
    react = message["reacts"][react_id]
    user_id = auth_get_current_user_id_from_token(token)
    # User is reacted and user is in the react user_id list
    return user_id in react["u_ids"]


# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture(scope="session")
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
