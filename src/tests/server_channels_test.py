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


# User in multiple different channels
def test_channel_list_user_multiple(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # User creates 5 different channels
    channel_01 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    ).json()

    channel_02 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_02", "is_public": True},
    ).json()

    channel_03 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_03", "is_public": True},
    ).json()

    channel_04 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_04", "is_public": True},
    ).json()

    channel_05 = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_05", "is_public": True},
    ).json()

    response = requests.get(url + "channels/list", params={"token": user["token"]})
    assert response.status_code == 200
    channels_list_dict = response.json()
    channel_list = [x["channel_id"] for x in channels_list_dict]

    assert channel_01["channel_id"] in channel_list
    assert channel_02["channel_id"] in channel_list
    assert channel_03["channel_id"] in channel_list
    assert channel_04["channel_id"] in channel_list
    assert channel_05["channel_id"] in channel_list


# Channels list with messages and multiple users in channel
def tests_channels_list_large(url):
    requests.delete(url + "clear")
    admin, user01, user02, user03 = http_register_n_users(url, 4)

    channel = requests.post(
        url + "channels/create",
        json={"token": admin["token"], "name": "channel_01", "is_public": True},
    ).json()

    # 3 users join the channel
    r = requests.post(
        url + "channel/join",
        json={"token": user01["token"], "channel_id": channel["channel_id"]},
    )
    assert r.status_code == 200

    r = requests.post(
        url + "channel/join",
        json={"token": user02["token"], "channel_id": channel["channel_id"]},
    )
    assert r.status_code == 200

    r = requests.post(
        url + "channel/join",
        json={"token": user03["token"], "channel_id": channel["channel_id"]},
    )
    assert r.status_code == 200

    # Each user sends a customised message
    r = requests.post(
        url + "message/send",
        json={
            "token": user01["token"],
            "channel_id": channel["channel_id"],
            "message": "user01",
        },
    )
    assert r.status_code == 200

    r = requests.post(
        url + "message/send",
        json={
            "token": user02["token"],
            "channel_id": channel["channel_id"],
            "message": "user02",
        },
    )
    assert r.status_code == 200

    r = requests.post(
        url + "message/send",
        json={
            "token": user03["token"],
            "channel_id": channel["channel_id"],
            "message": "user03",
        },
    )
    assert r.status_code == 200

    # Ensure each user has this channel in their channel list
    response = requests.get(url + "channels/list", params={"token": admin["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list]

    response = requests.get(url + "channels/list", params={"token": user01["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list]

    response = requests.get(url + "channels/list", params={"token": user02["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list]

    response = requests.get(url + "channels/list", params={"token": user03["token"]})
    assert response.status_code == 200
    channels_list = response.json()
    assert channel["channel_id"] in [x["channel_id"] for x in channels_list]


###########################################################################
#                       Tests for channels/listall                        #
###########################################################################


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


def test_channels_listall_empty(url):
    requests.delete(url + "clear")
    user_01 = http_register_n_users(url, 1)
    response = requests.get(
        url + "channels/listall", params={"token": user_01["token"]}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_channels_listall_public(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    token = user["token"]
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
    assert channel_id_1 in channel_ids
    assert channel_id_2 in channel_ids


def test_channels_listall_private(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    token = user["token"]
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
    assert channel_id_1 in channel_ids
    assert channel_id_2 in channel_ids


def test_channels_listall_multiple_users_public(url):
    requests.delete(url + "clear")

    user_01, user_02 = http_register_n_users(url, 2)

    tokens = [user_01["token"], user_02["token"]]
    channel_ids = []
    names = ["private_channel_01", "private_channel_02"]

    for name, token in zip(names, tokens):
        channel_id = requests.post(
            url + "channels/create",
            json={"token": token, "name": name, "is_public": True},
        ).json()["channel_id"]
        channel_ids.append(channel_id)

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


def test_channels_listall_multiple_users_private(url):
    requests.delete(url + "clear")

    user_01, user_02 = http_register_n_users(url, 2)

    tokens = [user_01["token"], user_02["token"]]
    channel_ids = []
    names = ["private_channel_01", "private_channel_02"]

    for name, token in zip(names, tokens):
        channel_id = requests.post(
            url + "channels/create",
            json={"token": token, "name": name, "is_public": False},
        ).json()["channel_id"]
        channel_ids.append(channel_id)

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
