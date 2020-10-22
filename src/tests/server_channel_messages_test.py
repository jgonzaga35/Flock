import requests
from test_helpers import url, http_register_n_users


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
