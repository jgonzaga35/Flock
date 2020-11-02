from test_helpers import url, http_register_n_users
from error import AccessError, InputError
import pytest
import requests
import json

INVALID_MESSAGE_ID = -1

##############################################################
#                   Tests for message/send                   #
##############################################################


def test_send_one_message(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Create a channel
    response = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    )
    assert response.status_code == 200
    channel = response.json()

    # Send a message
    response = requests.post(
        url + "message/send",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "message": "test message",
        },
    )
    assert response.status_code == 200

    # Get a list of messages in the channel
    response = requests.get(
        url + "channel/messages",
        params={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    )
    assert response.status_code == 200

    # Ensure message in the channel
    channel_messages = response.json()
    assert "test message" in [x["message"] for x in channel_messages["messages"]]


def test_messages_send_access_error(url):
    requests.delete(url + "clear")
    user_01, user_02 = http_register_n_users(url, 2)

    # Create a public channel
    response = requests.post(
        url + "channels/create",
        json={"token": user_01["token"], "name": "channel_pub", "is_public": True},
    )
    assert response.status_code == 200
    channel_pub = response.json()

    # Create a private channel
    response = requests.post(
        url + "channels/create",
        json={"token": user_01["token"], "name": "channel_priv", "is_public": False},
    )
    assert response.status_code == 200
    channel_priv = response.json()

    # User_02 tries to send a message to both channels
    response = requests.post(
        url + "message/send",
        json={
            "token": user_02["token"],
            "channel_id": channel_pub["channel_id"],
            "message": "test message",
        },
    )
    assert response.status_code == 403

    response = requests.post(
        url + "message/send",
        json={
            "token": user_02["token"],
            "channel_id": channel_priv["channel_id"],
            "message": "test message",
        },
    )
    assert response.status_code == 403


def test_messages_send_invalid_channel_id(url):
    requests.delete(url + "clear")
    user_01, user_02 = http_register_n_users(url, 2)

    # Create a channel
    response = requests.post(
        url + "channels/create",
        json={"token": user_01["token"], "name": "channel_01", "is_public": True},
    )
    assert response.status_code == 200
    channel = response.json()

    # Send a message to a channel with an invalid channel_id
    response = requests.post(
        url + "message/send",
        json={
            "token": user_02["token"],
            "channel_id": channel["channel_id"] + 1,
            "message": "test message",
        },
    )
    assert response.status_code == 400


def test_message_send_too_long(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)

    # Create a channel
    response = requests.post(
        url + "channels/create",
        json={"token": user["token"], "name": "channel_01", "is_public": True},
    )
    assert response.status_code == 200
    channel = response.json()

    # Send a message which shouldn't cause any problems
    response = requests.post(
        url + "message/send",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "message": "a" * 1000,
        },
    )
    assert response.status_code == 200

    # Send a message which exceeds send limit
    response = requests.post(
        url + "message/send",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "message": "a" * 1001,
        },
    )
    assert response.status_code == 400

    # Send another message which exceeds send limit by a large amount
    response = requests.post(
        url + "message/send",
        json={
            "token": user["token"],
            "channel_id": channel["channel_id"],
            "message": "a" * 12345,
        },
    )
    assert response.status_code == 400


def test_message_send_large_flock(url):
    requests.delete(url + "clear")
    owner, user_01, user_02, user_03, user_04 = http_register_n_users(url, 5)

    # owner creates a public channel
    response = requests.post(
        url + "channels/create",
        json={"token": owner["token"], "name": "channel_01", "is_public": True},
    )
    assert response.status_code == 200
    channel = response.json()

    # Users join the channel
    response = requests.post(
        url + "channel/join",
        json={"token": user_01["token"], "channel_id": channel["channel_id"]},
    )
    assert response.status_code == 200

    response = requests.post(
        url + "channel/join",
        json={"token": user_02["token"], "channel_id": channel["channel_id"]},
    )
    assert response.status_code == 200

    response = requests.post(
        url + "channel/join",
        json={"token": user_03["token"], "channel_id": channel["channel_id"]},
    )
    assert response.status_code == 200

    response = requests.post(
        url + "channel/join",
        json={"token": user_04["token"], "channel_id": channel["channel_id"]},
    )
    assert response.status_code == 200

    # Each user (expect owner) sends a single message
    response = requests.post(
        url + "message/send",
        json={
            "token": user_01["token"],
            "channel_id": channel["channel_id"],
            "message": "message from user_01",
        },
    )
    assert response.status_code == 200

    response = requests.post(
        url + "message/send",
        json={
            "token": user_02["token"],
            "channel_id": channel["channel_id"],
            "message": "message from user_02",
        },
    )
    assert response.status_code == 200

    response = requests.post(
        url + "message/send",
        json={
            "token": user_03["token"],
            "channel_id": channel["channel_id"],
            "message": "message from user_03",
        },
    )
    assert response.status_code == 200

    response = requests.post(
        url + "message/send",
        json={
            "token": user_04["token"],
            "channel_id": channel["channel_id"],
            "message": "message from user_04",
        },
    )
    assert response.status_code == 200

    # Verify messages actually in database
    response = requests.get(
        url + "channel/messages",
        params={
            "token": user_01["token"],
            "channel_id": channel["channel_id"],
            "start": 0,
        },
    )
    assert response.status_code == 200
    channel_messages_dict = response.json()
    messages = [x["message"] for x in channel_messages_dict["messages"]]
    assert "message from user_01" in messages
    assert "message from user_02" in messages
    assert "message from user_03" in messages
    assert "message from user_04" in messages
