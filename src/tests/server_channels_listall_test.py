import requests
from test_helpers import url, http_register_n_users

###########################################################################
#                       Tests for channels/listall                        #
###########################################################################

# test channel with invalid token
def test_channels_listall_invalid_token(url):

    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    token = user["token"]
    requests.post(
        url + "channels/create",
        json={"token": token, "name": "valid_channel_name", "is_public": True},
    ).json()["channel_id"]

    invalid_token = -1

    response = requests.get(url + "channels/listall", params={"token": invalid_token})
    assert response.status_code == 403

# Test when no channel can be list
def test_channels_listall_empty(url):
    requests.delete(url + "clear")
    user_01 = http_register_n_users(url, 1)
    response = requests.get(
        url + "channels/listall", params={"token": user_01["token"]}
    )
    assert response.status_code == 200
    assert response.json() == []

# Test one user list multiple public channel
def test_channels_listall_public(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    token = user["token"]
    # Create two channels by one user
    channel_id_1 = requests.post(
        url + "channels/create",
        json={"token": token, "name": "channel_01", "is_public": True},
    ).json()["channel_id"]

    channel_id_2 = requests.post(
        url + "channels/create",
        json={"token": token, "name": "channel_02", "is_public": True},
    ).json()["channel_id"]

    response = requests.get(url + "channels/listall", params={"token": token})
    assert response.status_code == 200
    channel_ids = [channel["channel_id"] for channel in response.json()]
    assert channel_ids == [channel_id_1, channel_id_2]

# Test one user list multiple public channel
def test_channels_listall_private(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    token = user["token"]
    # Create two channels by one user
    channel_id_1 = requests.post(
        url + "channels/create",
        json={"token": token, "name": "channel_01", "is_public": False},
    ).json()["channel_id"]

    channel_id_2 = requests.post(
        url + "channels/create",
        json={"token": token, "name": "channel_01", "is_public": False},
    ).json()["channel_id"]

    response = requests.get(url + "channels/listall", params={"token": token})
    assert response.status_code == 200
    channel_ids = [channel["channel_id"] for channel in response.json()]
    assert channel_ids == [channel_id_1, channel_id_2]

# Test multiple users list multiple public channels
def test_channels_listall_multiple_users_public(url):
    requests.delete(url + "clear")

    user_01, user_02 = http_register_n_users(url, 2)

    tokens = [user_01["token"], user_02["token"]]
    channel_ids = []
    names = ["private_channel_01", "private_channel_02"]

    # Create a list of tuple which include elements from
    # names and token, and use it to create two channel
    for name, token in zip(names, tokens):
        channel_id = requests.post(
            url + "channels/create",
            json={"token": token, "name": name, "is_public": True},
        ).json()["channel_id"]
        channel_ids.append(channel_id)

    # Authorised channel is our expectation to the
    # channels which should be listed.
    authorised_channels = []
    for channel_id, name in zip(channel_ids, names):
        authorised_channels.append({"channel_id": channel_id, "name": name})

    # For any user, channels/listall should list all of channels that exist.
    response01 = requests.get(
        url + "channels/listall", params={"token": user_01["token"]}
    )
    response02 = requests.get(
        url + "channels/listall", params={"token": user_02["token"]}
    )
    assert response01.json() == authorised_channels
    assert response02.json() == authorised_channels


# Test multiple users list multiple private channels
def test_channels_listall_multiple_users_private(url):
    requests.delete(url + "clear")

    user_01, user_02 = http_register_n_users(url, 2)

    tokens = [user_01["token"], user_02["token"]]
    channel_ids = []
    names = ["private_channel_01", "private_channel_02"]


    # Create a list of tuple which include elements from
    # names and token, and use it to create two channel
    for name, token in zip(names, tokens):
        channel_id = requests.post(
            url + "channels/create",
            json={"token": token, "name": name, "is_public": False},
        ).json()["channel_id"]
        channel_ids.append(channel_id)


    # Authorised channel is our expectation to the
    # channels which should be listed.
    authorised_channels = []
    for channel_id, name in zip(channel_ids, names):
        authorised_channels.append({"channel_id": channel_id, "name": name})

    response01 = requests.get(
        url + "channels/listall", params={"token": user_01["token"]}
    )
    response02 = requests.get(
        url + "channels/listall", params={"token": user_02["token"]}
    )
    assert response01.json() == authorised_channels
    assert response02.json() == authorised_channels
