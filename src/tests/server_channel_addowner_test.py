import requests
from test_helpers import url, http_register_n_users


###########################################################################
#                       Tests for channel/addowner                        #
###########################################################################

# Testing for if someone tries to add an owner but do not have admin privileges
def test_add_owner_invalid_token(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    # Owner creates a public channel
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # User tries to make themselves the owner of Owner's channel
    response = requests.post(
        url + "channel/addowner",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    assert response.status_code == 403


# Testing for when the owner makes a non-member of their channel into an owner
def test_add_owner_non_member(url):
    requests.delete(url + "clear")
    owner, non_member = http_register_n_users(url, 2)

    # Owner creates public channel
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Owner adds non-member as an owner to their channel
    requests.post(
        url + "channel/addowner",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": non_member["u_id"],
        },
    )

    # Ensure non-member now has access to channel/details
    response = requests.get(
        url + "channel/details",
        params={"token": non_member["token"], "channel_id": channel["channel_id"]},
    )
    assert response.status_code == 200

    # Ensure non-member is part of the owner list
    members = response.json()["owner_members"]
    assert non_member["u_id"] in [x["u_id"] for x in members]


# Testing for when the owner makes a member of their channel into an owner
def test_add_member_as_owner(url):
    requests.delete(url + "clear")
    owner, member = http_register_n_users(url, 2)

    # Owner creates public channel
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Member joins owner's channel
    requests.post(
        url + "channel/join",
        json={"token": member["token"], "channel_id": channel["channel_id"]},
    )

    # Owner adds member as an owner to their channel
    requests.post(
        url + "channel/addowner",
        json={
            "token": owner["token"],
            "channel_id": channel["channel_id"],
            "u_id": member["u_id"],
        },
    )

    # Check that the member is now in the member list
    response = requests.get(
        url + "channel/details",
        params={"token": owner["token"], "channel_id": channel["channel_id"]},
    )

    # Ensure member is part of the owner list
    members = response.json()["owner_members"]
    assert member["u_id"] in [x["u_id"] for x in members]


# Testing for when owner tries to add user using invalid channel id
def test_add_owner_invalid_channel_id(url):
    requests.delete(url + "clear")
    owner, user = http_register_n_users(url, 2)

    # Owner creates public channel
    channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Owner adds user using invalid channel id
    invalid_channel_id = -1
    response = requests.post(
        url + "channel/addowner",
        json={
            "token": owner["token"],
            "channel_id": invalid_channel_id,
            "u_id": user["u_id"],
        },
    )

    assert response.status_code == 400


# Testing that adding an existing owner has no effect
def test_add_owner_repeatedly(url):
    requests.delete(url + "clear")
    owner_1, owner_2 = http_register_n_users(url, 2)

    # Owner_1 creates a public channel
    public_channel = requests.post(
        url + "channels/create",
        json={"token": owner_1["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Owner_1 adds Owner_2 as an owner
    requests.post(
        url + "channel/addowner",
        json={
            "token": owner_1["token"],
            "channel_id": public_channel["channel_id"],
            "u_id": owner_2["u_id"],
        },
    )

    # Owner_1 adds Owner_2 as an owner again
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

    # Owner tries to add a non-existent user as owner
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

    # Owner creates a public channel
    public_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json()

    # Member joins the owner's channel
    response = requests.post(
        url + "channel/join",
        json={"token": member["token"], "channel_id": public_channel["channel_id"]},
    )
    assert response.status_code == 200

    # Check that the member is now in the member list
    response = requests.get(
        url + "channel/details",
        params={"token": owner["token"], "channel_id": public_channel["channel_id"]},
    )
    members = response.json()["all_members"]
    assert member["u_id"] in [x["u_id"] for x in members]

    # The member tries to add a user (non-member) as an owner to the channel
    response = requests.post(
        url + "channel/addowner",
        json={
            "token": member["token"],
            "channel_id": public_channel["channel_id"],
            "u_id": user["u_id"],
        },
    )

    assert response.status_code == 403
