import requests
from test_helpers import url, http_register_n_users


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