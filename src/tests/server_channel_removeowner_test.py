import requests
from test_helpers import url, http_register_n_users


###########################################################################
#                       Tests for channel/removeowner                     #
###########################################################################


# Successfully removing owner in a channel with multiple owners
def test_remove_owner_on_owner(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    # Owner creates a public channel
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Owner adds user as owner to the channel
    requests.post(
        url + "channel/addowner",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    # Owner removes themselves as owner
    requests.post(
        url + "channel/removeowner",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": owner["u_id"],
        },
    )

    # Ensure Owner is no longer in owner_members
    response = requests.get(
        url + "channel/details",
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    members = response.json()["owner_members"]
    assert owner["u_id"] not in [x["u_id"] for x in members]


# Trying to use remove_owner on a member of a channel
def test_remove_owner_on_member(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    # Owner creates a public channel
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # User joins channel and becomes a member
    requests.post(
        url + "channel/join",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
        },
    )

    # Owner tries to remove user using removeowner
    response = requests.post(
        url + "channel/removeowner",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    assert response.status_code == 400


# Member without owner privileges tries to remove an owner.
def test_remove_owner_invalid_token(url):

    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    # Owner creates public channel
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # User joins owner's channel
    response = requests.post(
        url + "channel/join",
        json={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    # Assert user is in owner's channel
    response = requests.get(
        url + "channel/details",
        params={"token": owner["token"], "channel_id": channel["channel_id"]},
    )
    members = response.json()["all_members"]
    assert user["u_id"] in [x["u_id"] for x in members]

    # User tries to remove Owner as owner of the channel
    response = requests.post(
        url + "channel/removeowner",
        json={
            "token": user["token"],
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

    # Owner creates public channel
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Owner adds user as another owner of the channel
    requests.post(
        url + "channel/addowner",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    # Owner tries to remove the other owner with invalid channel id
    invalid_channel_id = -1
    response = requests.post(
        url + "channel/removeowner",
        json={
            "token": owner["token"],
            "channel_id": invalid_channel_id,
            "u_id": user["u_id"],
        },
    )

    assert response.status_code == 400


# Owner tries to remove a nonexistent user as owner
def test_remove_owner_on_nonexistent_user(url):

    requests.delete(url + "clear")
    owner = http_register_n_users(url, 1)

    # Owner creates public channel
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # User tries to remove non-existent user as owner of the channel
    nonexistent_user_id = -1
    response = requests.post(
        url + "channel/removeowner",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": nonexistent_user_id,
        },
    )

    assert response.status_code == 400
