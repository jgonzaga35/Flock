import requests
from test_helpers import url, http_register_n_users


###########################################################################
#                       Tests for channel/removeowner                     #
###########################################################################


# Successfully removing owner and passing ownership to other user in channel
def test_remove_owner_successful(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/addowner",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    requests.post(
        url + "channel/removeowner",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": owner["u_id"],
        },
    )

    response = requests.get(
        url + "channel/details",
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    members = response.json()["owner_members"]
    assert owner["u_id"] not in [x["u_id"] for x in members]


# Member without owner privileges tries to remove an owner.
def test_remove_owner_invalid_token(url):

    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    response = requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    # Test fails if channel/join is not implemented as well
    response = requests.get(
        url + "channel/details",
        params={"token": owner["token"], "channel_id": channel["channel_id"]},
    )
    members = response.json()["all_members"]
    assert user["u_id"] in [x["u_id"] for x in members]

    response = requests.post(
        url + "channel/removeowner",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "u_id": owner["u_id"],
        },
    )

    assert response.status_code == 403


# Nonexisting member tries to remove an owner.
def test_remove_owner_nonexisting_member(url):

    requests.delete(url + "clear")
    owner = http_register_n_users(url, 1)

    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    nonexistent_token = -1
    response = requests.post(
        url + "channel/removeowner",
        json={
            "token": nonexistent_token,
            "channel_id": channel["channel_id"],
            "u_id": owner["u_id"],
        },
    )

    assert response.status_code == 403


# Owner adds another user using addowner, but uses removeowner with
# an invalid channel id argument.
def test_remove_owner_invalid_channel_id(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/addowner",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    invalid_channel_id = channel["channel_id"] - 1
    response = requests.post(
        url + "channel/removeowner",
        json={
            "token": owner["token"],
            "channel_id": invalid_channel_id,
            "u_id": user["u_id"],
        },
    )

    assert response.status_code == 400
    