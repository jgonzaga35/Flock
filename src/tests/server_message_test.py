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
    admin, user_01, user_02, user_03, user_04 = http_register_n_users(url, 5)

    # Admin creates a public channel
    response = requests.post(
        url + "channels/create",
        json={"token": admin["token"], "name": "channel_01", "is_public": True},
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

    # Each user (expect admin) sends a single message
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


###################################################################
#                   Tests for message/remove                      #
###################################################################
def test_remove_invalid_user_token(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    # Create a new channel
    channel_params = {
        "token": user["token"],
        "name": "channel_01",
        "is_public": True,
    }
    response = requests.post(url + "channels/create", json=channel_params)
    assert response.status_code == 200
    channel = response.json()
    # User sends a message
    message_params = {
        "token": user["token"],
        "channel_id": channel["channel_id"],
        "message": "test message",
    }
    response = requests.post(url + "message/send", json=message_params)
    assert response.status_code == 200
    message = response.json()

    message_remove_params = {
        "token": "-1",
        "message_id": message["message_id"],
    }
    # Ensure access error raised
    r = requests.delete(url + "message/remove", json=message_remove_params)
    assert r.status_code == 403


def test_remove_invald_message_id(url):
    requests.delete(url + "clear")
    user = http_register_n_users(url, 1)
    # Create a new channel
    channel_params = {
        "token": user["token"],
        "name": "channel_01",
        "is_public": True,
    }
    response = requests.post(url + "channels/create", json=channel_params)
    assert response.status_code == 200
    channel = response.json()

    # User sends a message
    message_params = {
        "token": user["token"],
        "channel_id": channel["channel_id"],
        "message": "test message",
    }
    response = requests.post(url + "message/send", json=message_params)
    assert response.status_code == 200

    # User tries to edit message with invalid message id
    message_remove_params = {"token": user["token"], "message_id": INVALID_MESSAGE_ID}

    # Ensure input error raised
    r = requests.delete(url + "message/remove", json=message_remove_params)
    assert r.status_code == 400


# User removing a message is not authorised to remove it
def test_remove_unauthorised_user(url):
    requests.delete(url + "clear")
    user01, user02 = http_register_n_users(url, 2)

    # Create a new channel
    channel_params = {
        "token": user01["token"],
        "name": "channel_01",
        "is_public": True,
    }
    response = requests.post(url + "channels/create", json=channel_params)
    assert response.status_code == 200
    channel = response.json()

    # User 1 sends a message
    message_params = {
        "token": user01["token"],
        "channel_id": channel["channel_id"],
        "message": "test message",
    }
    response = requests.post(url + "message/send", json=message_params)
    assert response.status_code == 200
    message = response.json()

    # User 2 tries to remove message from User 1
    message_remove_params = {
        "token": user02["token"],
        "message_id": message["message_id"],
    }

    r = requests.delete(url + "message/remove", json=message_remove_params)
    assert r.status_code == 403


# Test that owner of channel can remove any message
def test_remove_owner(url):
    requests.delete(url + "clear")
    user01, user02 = http_register_n_users(url, 2)

    # Create a new channel with User01 as admin
    channel_params = {
        "token": user01["token"],
        "name": "channel_01",
        "is_public": True,
    }
    response = requests.post(url + "channels/create", json=channel_params)
    assert response.status_code == 200
    channel = response.json()

    # User 2 joins channel
    response = requests.post(
        url + "channel/join",
        json={"token": user02["token"], "channel_id": channel["channel_id"]},
    )
    assert response.status_code == 200

    # User 2 sends a messages to channel
    message_params = {
        "token": user02["token"],
        "channel_id": channel["channel_id"],
        "message": "test message",
    }
    response = requests.post(url + "message/send", json=message_params)
    assert response.status_code == 200
    message = response.json()

    # User01 (admin) removes it
    message_remove_params = {
        "token": user01["token"],
        "message_id": message["message_id"],
    }
    response = requests.delete(url + "message/remove", json=message_remove_params)
    assert response.status_code == 200

    # Verify that message was removed successfuly
    channel_message_params = {
        "token": user01["token"],
        "channel_id": channel["channel_id"],
        "start": 0,
    }
    response = requests.get(url + "channel/messages", params=channel_message_params)
    assert response.status_code == 200
    channel_messages_dict = response.json()

    channel_messages = [x["message_id"] for x in channel_messages_dict["messages"]]
    assert message["message_id"] not in channel_messages


def test_remove_large_flockr(url):
    requests.delete(url + "clear")
    admin, user_01, user_02, user_03, user_04 = http_register_n_users(url, 5)

    # Admin creates a public channel
    response = requests.post(
        url + "channels/create",
        json={"token": admin["token"], "name": "channel_01", "is_public": True},
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

    # Each user (expect admin) sends a single message
    response = requests.post(
        url + "message/send",
        json={
            "token": user_01["token"],
            "channel_id": channel["channel_id"],
            "message": "message from user_01",
        },
    )
    assert response.status_code == 200
    message_id_01 = response.json()["message_id"]

    response = requests.post(
        url + "message/send",
        json={
            "token": user_02["token"],
            "channel_id": channel["channel_id"],
            "message": "message from user_02",
        },
    )
    assert response.status_code == 200
    message_id_02 = response.json()["message_id"]

    response = requests.post(
        url + "message/send",
        json={
            "token": user_03["token"],
            "channel_id": channel["channel_id"],
            "message": "message from user_03",
        },
    )
    assert response.status_code == 200
    message_id_03 = response.json()["message_id"]

    response = requests.post(
        url + "message/send",
        json={
            "token": user_04["token"],
            "channel_id": channel["channel_id"],
            "message": "message from user_04",
        },
    )
    assert response.status_code == 200
    message_id_04 = response.json()["message_id"]

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

    # Admin removes all messages from users
    message_ids = [message_id_01, message_id_02, message_id_03, message_id_04]
    for i in message_ids:
        response = requests.delete(
            url + "message/remove",
            json={
                "token": admin["token"],
                "message_id": i,
            },
        )
        assert response.status_code == 200

    # Verify messages is actually removed from database
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

    assert "message from user_01" not in messages
    assert "message from user_02" not in messages
    assert "message from user_03" not in messages
    assert "message from user_04" not in messages
