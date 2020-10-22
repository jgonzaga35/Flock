import requests
from test_helpers import url, http_register_n_users

###########################################################################
#                       Tests for channel/join                           #
###########################################################################
# User joins public channel successfully
def test_join_successful(url):
    requests.delete(url + "clear")
    admin, user = http_register_n_users(url, 2)
    response = requests.post(
        url + "channels/create",
        json={"token": admin["token"], "name": "channel_01", "is_public": True},
    )
    assert response.status_code == 200
    channel = response.json()

    requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    # List of dicts of channels user is part of
    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
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
