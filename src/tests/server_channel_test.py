import requests
from test_helpers import url, http_register_n_users


###########################################################################
#                       Tests for channel/invite                          #
###########################################################################

# Owner invites a non-member into their channel successfully
def test_channel_invite_successful(url):
    requests.delete(url + "clear")
    owner, non_member = http_register_n_users(url, 2)

    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    requests.post(
        url + "channel/invite",
        json={"token": owner["token"], "channel_id": channel["channel_id"], "u_id": non_member["u_id"]},
    )

    response = requests.get(url + "channel/details", 
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    members = response.json()["all_members"]
    assert non_member["u_id"] in [x["u_id"] for x in members]

# Non-member of a channel invites another non-member into that channel
def test_channel_invite_from_unauthorised_user(url):
    requests.delete(url + "clear")
    owner, user1, user2 = http_register_n_users(url, 3)

    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    # User 1 (non-member) invites User2 (non-member) to Owner's channel
    response = requests.post(
        url + "channel/invite",
        json={"token": user1["token"], "channel_id": channel["channel_id"], "u_id": user2["u_id"]},
    )

    assert response.status_code == 403

# Inviting a non-existent user to a channel
def test_channel_invite_invalid_user_id(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    invalid_user_id = -1
    response = requests.post(
        url + "channel/invite",
        json={"token": owner["token"], "channel_id": channel["channel_id"], "u_id": invalid_user_id},
    ) 

    assert response.status_code == 400

# Testing for a token that does not exist in the database
def test_channel_invite_invalid_token(url):
    requests.delete(url + "clear")
    owner = http_register_n_users(url, 1)

    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    invalid_token = -1
    response = requests.post(
        url + "channel/invite",
        json={"token": invalid_token, "channel_id": channel["channel_id"], "u_id": invalid_user_id},
    ) 

    assert response.status_code == 400

# Testing for a channel that does not exist in the database
def test_channel_invite_invalid_channel_id(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    invalid_channel_id = -1
    response = requests.post(
        url + "channel/invite",
        json={"token": invalid_token, "channel_id": invalid_channel_id, "u_id": user["user_id"]},
    ) 

    assert response.status_code == 400

# Testing to ensure inviting a member of a channel to the same channel
# again does not increase number of members of channel
def test_channel_invite_invalid_channel_id(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    requests.post(
        url + "channel/invite",
        json={"token": owner["token"], "channel_id": channel["channel_id"], "u_id": user["u_id"]},
    )

    # Get a list of all members in owner's channel
    response = requests.get(url + "channel/details", 
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )
    members = response.json()["all_members"]
    assert user["u_id"] in [x["u_id"] for x in members]
    expected_num_of_members = length(members)

    requests.post(
        url + "channel/invite",
        json={"token": owner["token"], "channel_id": channel["channel_id"], "u_id": user["u_id"]},
    )

    # Ensure length is same as previous list
    response = requests.get(url + "channel/details", 
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )
    members = response.json()["all_members"]
    assert length(members) == expected_num_of_members
     
