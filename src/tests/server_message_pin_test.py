from test_helpers import url, http_register_n_users
from error import AccessError, InputError
import pytest
import requests

INVALID_MESSAGE_ID = -1

# Fixutre which creates a sample public channel
# and sends a message, returning url, user,
# channel and message info
@pytest.fixture
def create_channel(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Create a channel
    response = requests.post(
        url + "channels/create",
        json={
            "token": user["token"],
            "name": "channel_01",
            "is_public": False,
        },
    )
    assert response.status_code == 200
    channel = response.json()

    # User sends a message
    response = requests.post(
        url + "message/send",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "message": "test message",
        },
    )
    assert response.status_code == 200
    message = response.json()
    return [url, user, channel, message]


def test_message_pin_public_simple(create_channel):
    url, user, channel, message = create_channel

    # Return messages in channel
    response = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    )
    assert response.status_code == 200
    channel_msg = response.json()

    # Ensure message is not pinned
    assert channel_msg["messages"][0]["is_pinned"] == False

    response = requests.post(
        url + "message/pin",
        json={"token": user["token"], "message_id": message["message_id"]},
    )

    assert response.status_code == 200
    # Return messages in channel
    response = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    )
    assert response.status_code == 200
    channel_msg = response.json()

    assert channel_msg["messages"][0]["is_pinned"] == True


def test_message_pin_private_simple(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Create a channel
    response = requests.post(
        url + "channels/create",
        json={
            "token": user["token"],
            "name": "channel_01",
            "is_public": False,
        },
    )
    assert response.status_code == 200
    channel = response.json()

    # User sends a message
    response = requests.post(
        url + "message/send",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "message": "test message",
        },
    )
    assert response.status_code == 200
    message = response.json()

    # Return messages in channel
    response = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    )
    assert response.status_code == 200
    channel_msg = response.json()

    # Ensure message is not pinned
    assert channel_msg["messages"][0]["is_pinned"] == False

    response = requests.post(
        url + "message/pin",
        json={"token": user["token"], "message_id": message["message_id"]},
    )

    assert response.status_code == 200

    # Return updated messages in channel
    response = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    )
    assert response.status_code == 200
    channel_msg = response.json()

    assert channel_msg["messages"][0]["is_pinned"] == True


def test_message_pin_invalid_msesage_id(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Create a channel
    response = requests.post(
        url + "channels/create",
        json={
            "token": user["token"],
            "name": "channel_01",
            "is_public": False,
        },
    )
    assert response.status_code == 200
    channel = response.json()

    # User sends a message
    response = requests.post(
        url + "message/send",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "message": "test message",
        },
    )
    assert response.status_code == 200
    message = response.json()

    # Return messages in channel
    response = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    )
    assert response.status_code == 200
    channel_msg = response.json()

    # Ensure message is not pinned
    assert channel_msg["messages"][0]["is_pinned"] == False

    response = requests.post(
        url + "message/pin",
        json={"token": user["token"], "message_id": INVALID_MESSAGE_ID},
    )

    assert response.status_code == 400


def test_message_already_pinned(create_channel):
    url, user, channel, message = create_channel

    # Return messages in channel
    response = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    )
    assert response.status_code == 200
    channel_msg = response.json()

    # Ensure message is not pinned, and pin message
    assert channel_msg["messages"][0]["is_pinned"] == False
    response = requests.post(
        url + "message/pin",
        json={"token": user["token"], "message_id": message["message_id"]},
    )
    assert response.status_code == 200

    # Attempt to pin a message that is already pinned
    assert channel_msg["messages"][0]["is_pinned"] == False
    response = requests.post(
        url + "message/pin",
        json={"token": user["token"], "message_id": message["message_id"]},
    )
    assert response.status_code == 400
