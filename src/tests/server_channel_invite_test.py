import requests
from test_helpers import url, http_register_n_users


###########################################################################
#                       Tests for channel/invite                          #
###########################################################################

# Owner invites a non-member into their channel successfully
def test_channel_invite_successful(url):
    requests.delete(url + "clear")
    owner, non_member = http_register_n_users(url, 2)

    # Owner creates private channel
    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    # Owner invites non-member to private channel
    response = requests.post(
        url + "channel/invite",
        json={
            "token": owner["token"],
            "channel_id": private_channel["channel_id"],
            "u_id": non_member["u_id"],
        },
    )
    assert response.status_code == 200

    # Check if the non_member is now in the member list
    response = requests.get(
        url + "channel/details",
        params={"token": owner["token"], "channel_id": private_channel["channel_id"]},
    )

    members = response.json()["all_members"]
    assert non_member["u_id"] in [x["u_id"] for x in members]


# Non-member of a channel invites another non-member into that channel
def test_channel_invite_from_unauthorised_user(url):
    requests.delete(url + "clear")
    owner, user1, user2 = http_register_n_users(url, 3)

    # Owner creates a private channel
    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    # User 1 (non-member) invites User2 (non-member) to Owner's channel
    response = requests.post(
        url + "channel/invite",
        json={
            "token": user1["token"],
            "channel_id": private_channel["channel_id"],
            "u_id": user2["u_id"],
        },
    )

    assert response.status_code == 403


# Inviting a non-existent user to a channel
def test_channel_invite_invalid_user_id(url):
    requests.delete(url + "clear")
    owner = http_register_n_users(url, 1)

    # Owner creates private channel
    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    # Owner invites a user that does not exist in the database
    invalid_user_id = -1
    response = requests.post(
        url + "channel/invite",
        json={
            "token": owner["token"],
            "channel_id": private_channel["channel_id"],
            "u_id": invalid_user_id,
        },
    )

    assert response.status_code == 400


# Testing for a token that does not exist in the database
def test_channel_invite_invalid_token(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    # Owner creates private channel
    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    # Invalid token used to invite user to owner's channel
    invalid_token = "arandomtoken"
    response = requests.post(
        url + "channel/invite",
        json={
            "token": invalid_token,
            "channel_id": private_channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    assert response.status_code == 403


# Testing for a channel that does not exist in the database
def test_channel_invite_invalid_channel_id(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    # Owner creates a private channel
    requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    # Owner invites user with invalid channel id
    invalid_channel_id = -1
    response = requests.post(
        url + "channel/invite",
        json={
            "token": owner["token"],
            "channel_id": invalid_channel_id,
            "u_id": user["u_id"],
        },
    )

    assert response.status_code == 400


# Testing to ensure inviting a member of a channel to the same channel
# again does not increase number of members of channel
def test_channel_invite_repeated(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    # Owner creates a private channel
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    # Owner invites user to their channel
    requests.post(
        url + "channel/invite",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    # Ensure that the user is now a member of the channel
    response = requests.get(
        url + "channel/details",
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )
    members = response.json()["all_members"]
    assert user["u_id"] in [x["u_id"] for x in members]
    expected_num_of_members = len(members)

    # Owner invites the same user to their channel again
    requests.post(
        url + "channel/invite",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    # Ensure the number of members has not increased
    response = requests.get(
        url + "channel/details",
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )
    members = response.json()["all_members"]
    assert len(members) == expected_num_of_members
