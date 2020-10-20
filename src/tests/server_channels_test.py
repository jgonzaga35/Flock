import requests
from test_helpers import url, http_register_n_users


###########################################################################
#                       Tests for channels/list                           #
###########################################################################
# User admin of one channel
def test_channels_list_1_channel(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    channel = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    ).json()

    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list]


# User admin of two chanels
def test_channels_list_2_channels(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    channel01 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    ).json()
    channel02 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_02", "is_public": True},
    ).json()

    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel01["channel_id"] in [x["channel_id"] for x in channels_list]
    assert channel02["channel_id"] in [x["channel_id"] for x in channels_list]


# User admin of private channel
def test_channels_list_public(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    channel = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": False},
    ).json()

    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list]


# Non-admin requests channels list
def tests_channels_list_non_admin(url):
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

    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list]


# Channels list with messages and multiple users in channel
def tests_channels_list_mock_channel(url):
    pass
    requests.delete(url + "clear")
    admin = http_register_n_users(url, 1)
    channel = requests.post(
        url + "channels/create",
        json={"token": admin["token"], "name": "channel_01", "is_public": True},
    ).json()
    response = requests.get(url + "channels/list", params={"token": admin["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list]
