import requests
from test_helpers import url, http_register_n_users

###########################################################################
#                       Tests for channel/leave                           #
###########################################################################

# User leaves public channel successfully
def test_leave_successful(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.json() == []

    channel = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/leave",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    # List of dicts of channels that user is part of
    response = requests.get(url + "channels/list", params={"token": user["token"]})
    
    # Ensure the list is empty
    assert response.json() == []


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


# User tries to leave channel with invalid channel id
def test_leave_invalid_channel_id(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    channel = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    ).json()

    invalid_channel_id = channel["channel_id"] + 1
    response = requests.post(
        url + "channel/leave",
        json={"token": user["token"], "channel_id": invalid_channel_id},
    )

    assert response.status_code == 400


# A user tries to leave a private channel that they are not part of
def test_inexist_user_leave_channel_private(url):
    requests.delete(url + "clear")
    user1, user2 = http_register_n_users(url, 2)
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": False},
    ).json()

    response = requests.post(
        url + "channel/leave",
        json={"token": user2["token"], "channel_id": channel["channel_id"]},
    )

    assert response.status_code == 403


# A user tries to leave a public channel that they are not part of
def test_inexist_user_leave_channel_public(url):
    requests.delete(url + "clear")
    user1, user2 = http_register_n_users(url, 2)
    channel = requests.post(
        url + "channels/create",
        json={"token": user1["token"], "name": "channel_01", "is_public": True},
    ).json()

    response = requests.post(
        url + "channel/leave",
        json={"token": user2["token"], "channel_id": channel["channel_id"]},
    )

    assert response.status_code == 403
    