import requests
from test_helpers import url, http_register_n_users


###########################################################################
#                       Tests for channel/addowner                        #
###########################################################################

def test_add_owner_successful(url):
    requests.delete(url + "clear")
    owner,user = http_register_n_users(url, 1)

    channel = requests.post(
        url + "channels/create"
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    requests.post(
        url + "channel/addowner",
        json={"token": owner["token"], "channel_id": channel["channel_id"], "u_id": user["u_id"]},
    )

    response = requests.get(url + "channel/details", 
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    members = response.json()["owner_members"]
    assert user in members

def test_add_owner_invalid_token(url):
    requests.delete(url + "clear")
    owner,user = http_register_n_users(url, 1)

    channel = requests.post(
        url + "channels/create"
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    response = requests.post(
        url + "channel/addowner",
        json={"token": user["token"], "channel_id": channel["channel_id"], "u_id": user["u_id"]},
    )

    assert response.status_code == 403


def test_add_owner_invalid_channel_id(url):
    requests.delete(url + "clear")
    owner,user = http_register_n_users(url, 1)

    channel = requests.post(
        url + "channels/create"
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    invalid_channel_id = channel["channel_id"] - 1
    response = requests.post(
        url + "channel/addowner",
        json={"token": owner["token"], "channel_id": invalid_channel_id, "u_id": user["u_id"]},
    )

    assert response.status_code == 403


###########################################################################
#                       Tests for channel/removeowner                     #
###########################################################################


# Successfully removing owner and passing ownership to user
# Owner creates a channel
# User joins channel
# Owner removes himself from channel
# User should be owner now.
def test_remove_owner_successful(url):
    requests.delete(url + "clear")
    owner,user = http_register_n_users(url, 1)

    channel = requests.post(
        url + "channels/create"
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    requests.post(
        url + "channel/removeowner",
        json={"token": owner["token"], "channel_id": channel["channel_id"], "u_id": owner["u_id"]},
    )

    response = requests.get(url + "channel/details", 
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    members = response.json()["owner_members"]
    assert user in members

def test_remove_owner_invalid_token(url):
    requests.delete(url + "clear")
    owner,user = http_register_n_users(url, 1)

    channel = requests.post(
        url + "channels/create"
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    response = requests.post(
        url + "channel/removeowner",
        json={"token": user["token"], "channel_id": channel["channel_id"], "u_id": owner["u_id"]},
    )

    assert response.status_code == 403

def test_remove_owner_invalid_channel_id(url):
    requests.delete(url + "clear")
    owner,user = http_register_n_users(url, 1)

    channel = requests.post(
        url + "channels/create"
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    invalid_channel_id = channel["channel_id"] - 1
    response = requests.post(
        url + "channel/removeowner",
        json={"token": user["token"], "channel_id": invalid_channel_id, "u_id": owner["u_id"]},
    )

    assert response.status_code == 403




    