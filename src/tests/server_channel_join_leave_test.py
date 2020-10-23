import requests
from test_helpers import url, http_register_n_users


###########################################################################
#                       Tests for channel/join                           #
###########################################################################


# User joins public channel successfully
def test_join_successful(url):
    requests.delete(url + "clear")
    admin, user = http_register_n_users(url, 2)
    channel = requests.post(
        url + "channels/create",
        json={"token": admin["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    # List of dicts of channels user is part of
    response = requests.get(url + "channels/list", params={"token": user["token"]})
    # Ensure channel_id is in this lists
    assert channel["channel_id"] in [x["channel_id"] for x in response.json()]


# User with invalid token tires to join a channel
def test_join_invalid_token(url):
    requests.delete(url + "clear")
    admin = http_register_n_users(url, 1)
    channel = requests.post(
        url + "channels/create",
        json={"token": admin["token"], "name": "channel_01", "is_public": True},
    ).json()

    response = requests.post(
        url + "channel/join",
        json={"token": -1, "channel_id": channel["channel_id"]},
    )
    assert response.status_code == 403


# User tries to join channel with invalid channel id
def test_join_invalid_channel_id(url):
    requests.delete(url + "clear")
    admin, user = http_register_n_users(url, 2)
    channel = requests.post(
        url + "channels/create",
        json={"token": admin["token"], "name": "channel_01", "is_public": True},
    ).json()

    invalid_channel_id = channel["channel_id"] + 1
    response = requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": invalid_channel_id},
    )
    assert response.status_code == 400


###########################################################################
#                       Tests for channel/leave                           #
###########################################################################

# User with invalid token tries to leave a channel
def test_leave_invalid_token(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    channel = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    ).json()

    response = requests.post(
        url + "channel/leave",
        json={"token": -1, "channel_id": channel["channel_id"]},
    )

    assert response.status_code == 403


# User leaves public channel successfully
def test_leave_channel_successfully(url):
    requests.delete(url + "clear")
    owner = http_register_n_users(url, 1)
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Member leaves the channel so there is only the owner in the channel.
    requests.post(
        url + "channel/leave",
        json={"token": owner["token"], "channel_id": channel["channel_id"]},
    )

    # Response should return error 403 as owner no longer has access
    response = requests.get(
        url + "channel/details",
        params={"token": owner["token"], "channel_id": channel["channel_id"]},
    )
    assert response.status_code == 403


# A user tries to leave a private channel that they are not part of
def test_inexist_user_leave_channel_private(url):
    requests.delete(url + "clear")
    owner, member = http_register_n_users(url, 2)
    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    response = requests.post(
        url + "channel/leave",
        json={"token": member["token"], "channel_id": private_channel["channel_id"]},
    )

    assert response.status_code == 403


# A user tries to leave a public channel that they are not part of
def test_inexist_user_leave_channel_public(url):
    requests.delete(url + "clear")
    owner, member = http_register_n_users(url, 2)
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    response = requests.post(
        url + "channel/leave",
        json={"token": member["token"], "channel_id": channel["channel_id"]},
    )

    assert response.status_code == 403


# User tries to leave channel with invalid channel id
def test_leave_channel_id_invalid(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    )

    invalid_channel_id = -1

    response = requests.post(
        url + "channel/leave",
        json={"token": user["token"], "channel_id": invalid_channel_id},
    )

    assert response.status_code == 400
