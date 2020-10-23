import requests
from test_helpers import url, http_register_n_users

###########################################################################
#                       Tests for channel/messages                        #
###########################################################################


def test_messages_no_messages(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Create a channel
    response = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    )
    assert response.status_code == 200
    channel = response.json()

    response = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    )
    assert response.status_code == 200
    channel_messages_dict = response.json()
    assert len([x["message_id"] for x in channel_messages_dict["messages"]]) == 0


def test_messages_invalid_channel_id(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Create a channel
    response = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    )
    assert response.status_code == 200

    response = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": -1,
            "start": 0,
        },
    )
    assert response.status_code == 400


def test_messages_invalid_start(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Create a channel
    response = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    )
    assert response.status_code == 200
    channel = response.json()

    response = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "start": -1,
        },
    )
    assert response.status_code == 400


def test_messages_invalid_token(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Create a channel
    response = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    )
    assert response.status_code == 200
    channel = response.json()

    response = requests.get(
        url + "channel/messages",
        params={
            "token": -1,
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    )
    assert response.status_code == 403


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

    response = requests.post(
        url + "channel/invite",
        json={
            "token": owner["token"],
            "channel_id": private_channel["channel_id"],
            "u_id": non_member["u_id"],
        },
    )

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

    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

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

    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

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

    requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

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

    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    requests.post(
        url + "channel/invite",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    # Get a list of all members in owner's channel
    response = requests.get(
        url + "channel/details",
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )
    members = response.json()["all_members"]
    assert user["u_id"] in [x["u_id"] for x in members]
    expected_num_of_members = len(members)

    requests.post(
        url + "channel/invite",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    # Ensure length is same as previous list
    response = requests.get(
        url + "channel/details",
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )
    members = response.json()["all_members"]
    assert len(members) == expected_num_of_members


###########################################################################
#                       Tests for channel/addowner                        #
###########################################################################

# Testing for if someone tries to add an owner but do not have admin privileges
def test_add_owner_invalid_token(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    response = requests.post(
        url + "channel/addowner",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    assert response.status_code == 403


def test_add_owner_successfully(url):
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

    response = requests.get(
        url + "channel/details",
        params={"token": user["token"], "channel_id": channel["channel_id"]},
    )

    members = response.json()["owner_members"]
    assert user["u_id"] in [x["u_id"] for x in members]


def test_add_owner_invalid_channel_id(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    invalid_channel_id = channel["channel_id"] - 1
    response = requests.post(
        url + "channel/addowner",
        json={
            "token": owner["token"],
            "channel_id": invalid_channel_id,
            "u_id": user["u_id"],
        },
    )

    assert response.status_code == 400


def test_add_owner_repeatedly(url):
    requests.delete(url + "clear")
    owner_1, owner_2 = http_register_n_users(url, 2)

    public_channel = requests.post(
        url + "channels/create",
        json={"token": owner_1["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/addowner",
        json={
            "token": owner_1["token"],
            "channel_id": public_channel["channel_id"],
            "u_id": owner_2["u_id"],
        },
    )

    response = requests.post(
        url + "channel/addowner",
        json={
            "token": owner_1["token"],
            "channel_id": public_channel["channel_id"],
            "u_id": owner_2["u_id"],
        },
    )

    assert response.status_code == 400


# Testing that an owner cannot add nonexistent users
def test_add_invalid_user_to_owner(url):
    requests.delete(url + "clear")
    owner = http_register_n_users(url, 1)

    private_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": False},
    ).json()

    invalid_uid = -1

    response = requests.post(
        url + "channel/addowner",
        json={
            "token": owner["token"],
            "channel_id": private_channel["channel_id"],
            "u_id": invalid_uid,
        },
    )

    assert response.status_code == 400


# A member without owner privileges should not be able to addowner in the channel
def test_add_owner_by_non_owner(url):
    requests.delete(url + "clear")
    owner, member, user = http_register_n_users(url, 3)

    public_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    requests.post(
        url + "channel/join",
        json={"token": member["token"], "channel_id": public_channel["channel_id"]},
    )

    # Test fails if channel/join is not implemented as well
    # The member that joined the channel should be in the members list now.
    response = requests.get(
        url + "channel/details",
        params={"token": owner["token"], "channel_id": public_channel["channel_id"]},
    )
    members = response.json()["all_members"]
    assert member["u_id"] in [x["u_id"] for x in members]

    # The member should not be able to addowner.
    response = requests.post(
        url + "channel/addowner",
        json={
            "token": member["token"],
            "channel_id": public_channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    assert response.status_code == 403


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
