from test_helpers import url, http_register_n_users

from error import AccessError
import pytest
import requests
import json

INVALID_MESSAGE_ID = -1

###############################################################################
#                           Tests for message_edit                            #
###############################################################################
def test_edit_non_existent_user(url):
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

    # Non-existent user tries to edit the message
    message_edit_data = {
        "token": -1,
        "message_id": message["message_id"],
        "message": "try editing",
    }
    response = requests.put(url + "message/edit", json=message_edit_data)
    assert response.status_code == 400


def test_edit_invalid_message_id(url):
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

    # User tries to edit message with an invalid message id
    message_edit_data = {
        "token": user["token"] + 1,
        "message_id": INVALID_MESSAGE_ID,
        "message": "try editing",
    }
    response = requests.put(url + "message/edit", json=message_edit_data)
    assert response.status_code == 400


# # User editing a message is not authorised to edit it
def test_edit_unauthorised_user(url):
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

    # User 2 tries to edit the message
    message_edit = {
        "token": user02["token"],
        "message_id": message["message_id"],
        "message": "try editing",
    }
    response = requests.put(url + "message/edit", json=message_edit)
    assert response.status_code == 400


# Test that owner of channel can edit any message
def test_edit_owner(url):
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

    response = requests.post(
        url + "channel/join",
        json={"token": user02["token"], "channel_id": channel["channel_id"]},
    )
    assert response.status_code == 200

    # User 2 sends a message
    message_params = {
        "token": user02["token"],
        "channel_id": channel["channel_id"],
        "message": "test message",
    }
    response = requests.post(url + "message/send", json=message_params)
    assert response.status_code == 200
    message = response.json()

    # User01 (admin) edits it
    message_edit = {
        "token": user01["token"],
        "message_id": message["message_id"],
        "message": "try editing",
    }
    response = requests.put(url + "message/edit", json=message_edit)
    assert response.status_code == 200

    # Confirm that message was edited successfully, returns {messages, start, end}
    channel_messages_params = {
        "token": user01["token"],
        "channel_id": channel["channel_id"],
        "start": 0,
    }
    response = requests.get(url + "channel/messages", params=channel_messages_params)
    assert response.status_code == 200
    channel_messages_dict = response.json()

    assert "try editing" in [x["message"] for x in channel_messages_dict["messages"]]


# # Tests that a message is deleted is edit if empty string
def test_edit_empty_string(url):
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

    # Send message
    message_params = {
        "token": user["token"],
        "channel_id": channel["channel_id"],
        "message": "test message",
    }
    response = requests.post(url + "message/send", json=message_params)
    assert response.status_code == 200
    message = response.json()

    # Ensure message in database
    channel_messages_params = {
        "token": user["token"],
        "channel_id": channel["channel_id"],
        "start": 0,
    }
    response = requests.get(url + "channel/messages", params=channel_messages_params)
    assert response.status_code == 200
    channel_messages_dict = response.json()
    assert message["message_id"] in [
        x["message_id"] for x in channel_messages_dict["messages"]
    ]

    # Edit message with empty string
    message_edit = {
        "token": user["token"],
        "message_id": message["message_id"],
        "message": "",
    }
    response = requests.put(url + "message/edit", json=message_edit)
    assert response.status_code == 200

    # Ensure message id not in database
    response = requests.get(url + "channel/messages", params=channel_messages_params)
    assert response.status_code == 200
    channel_messages_dict = response.json()
    assert message["message_id"] not in [
        x["message_id"] for x in channel_messages_dict["messages"]
    ]
