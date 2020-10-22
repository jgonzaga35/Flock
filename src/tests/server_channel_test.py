import requests
from test_helpers import url, http_register_n_users
from channel_test import assert_contains_users_id

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
    owner, member = http_register_n_users(url, 2)
    public_channel = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    ).json() # Create public channel

    # Member joins the owner's channel so now there is 2 users in channel_01
    requests.post(
        url + "channel/join",
        json={"token": member["token"], "channel_id": public_channel["channel_id"]},
    )
    response = requests.get(url + "channel/details", params={"token": owner["token"], "channel_id": public_channel["channel_id"]})
    channel_details = response.json()
    expected_members_id = [owner["u_id"], member["u_id"]]
    assert_contains_users_id(channel_details["all_members"], expected_members_id)

    # Member leaves the channel so there is only the owner in the channel.
    requests.post(
        url + "channel/leave",
        json={"token": member["token"], "channel_id": public_channel["channel_id"]},
    )
    response = requests.get(url + "channel/details", params={"token": owner["token"], "channel_id": public_channel["channel_id"]})
    channel_details = response.json()
    expected_members_id = [owner["u_id"]]
    assert_contains_users_id(channel_details["all_members"], expected_members_id)


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
        json={"token": member["token"], "channel_id": channel["channel_id"]},
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
    