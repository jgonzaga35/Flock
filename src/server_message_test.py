from test_helpers import url

from error import AccessError
import pytest
import requests
import json

INVALID_MESSAGE_ID = -1

def register_new_account(url):
    return requests.post(
        url + "/auth/register",
        json={
            "email": "validemail@gmail.com",
            "password": "123abc!@#",
            "name_first": "Hayden",
            "name_last": "Everest",
        },
    ).json()

###############################################################################
#                           Tests for message_edit                            #
###############################################################################
# def test_edit_non_existent_user(url):
#     requests.delete(url + "clear")
#     user = register_new_account(url)
#     # Create a new channel
#     channel_params = {
#         "token": user["token"],
#         "name": "channel_01",
#         "is_public": True,
#     }
#     channel = requests.post(url + "channels/create", json=channel_params).json()
#     print(channel)
#     # User sends a message
#     message_params = {
#         "token": user["token"],
#         "channel_id": channel["channel_id"],
#         "message": "test message",
#     }
#     message = requests.post(url + "message/send", json=message_params).json()
#     # Non-existent user tries to edit the message
#     message_edit = {
#         "token": user["token"] + 1,
#         "message": message["message_id"],
#         "message": "try editing",
#     }
#     r = requests.put(url + "message/edit", data=message_edit)

#     assert r.status_code == 400


# def test_edit_invalid_message_id(url):
#     requests.delete(url + "clear")
#     user = register_new_account(url)
#     # Create a new channel
#     channel_params = {
#         "token": user["token"],
#         "name": "channel_01",
#         "is_public": True,
#     }
#     channel = requests.post(url + "channels/create", json=channel_params).json()

#     # User sends a message
#     message_params = {
#         "token": user["token"],
#         "channel_id": channel["channel_id"],
#         "message": "test message",
#     }
#     message = requests.post(url + "message/send", json=message_params).json()

#     # User tries to edit message with an invalid message id
#     message_edit = {
#         "token": user["token"] + 1,
#         "message_id": INVALID_MESSAGE_ID,
#         "message": "try editing",
#     }
#     r = requests.put(url + "message/edit", data=message_edit)

#     assert r.status_code == 400


# # User editing a message is not authorised to edit it
# def test_edit_unauthorised_user(url):
#     requests.delete(url + "clear")
#     user01 = requests.post(
#         url + "/auth/register",
#         json={
#             "email": "validemail01@gmail.com",
#             "password": "123abc!01@#",
#             "name_first": "Hayden01",
#             "name_last": "Everest01",
#         },
#     ).json()

#     user02 = requests.post(
#         url + "/auth/register",
#         json={
#             "email": "validemai02l@gmail.com",
#             "password": "123abc!02@#",
#             "name_first": "Hayden02",
#             "name_last": "Everest02",
#         },
#     ).json()

#     # Create a new channel
#     channel_params = {
#         "token": user01["token"],
#         "name": "channel_01",
#         "is_public": True,
#     }
#     channel = requests.post(url + "channels/create", json=channel_params).json()

#     # User 1 sends a message
#     message_params = {
#         "token": user01["token"],
#         "channel_id": channel["channel_id"],
#         "message": "test message",
#     }
#     message = requests.post(url + "message/send", json=message_params).json()

#     # User 2 tries to edit the message
#     message_edit = {
#         "token": user02["token"],
#         "message_id": message["message_id"],
#         "message": "try editing",
#     }
#     r = requests.put(url + "message/edit", data=message_edit)

#     assert r.status_code == 400


# Test that owner of channel can edit any message
def test_edit_owner(url):
    requests.delete(url + "clear")
    user01 = requests.post(
        url + "/auth/register",
        json={
            "email": "validemail01@gmail.com",
            "password": "123abc!01@#",
            "name_first": "Hayden01",
            "name_last": "Everest01",
        },
    ).json()

    user02 = requests.post(
        url + "/auth/register",
        json={
            "email": "validemai02l@gmail.com",
            "password": "123abc!02@#",
            "name_first": "Hayden02",
            "name_last": "Everest02",
        },
    ).json()

    # Create a new channel with User01 as admin
    channel_params = {
        "token": user01["token"],
        "name": "channel_01",
        "is_public": True,
    }
    channel = requests.post(url + "channels/create", json=channel_params).json()
    x = channel["channel_id"]
    print(f"channel id is: {x}")
    requests.post(url + "channel/join", json={
        "token": user02["token"], 
        "channel_id": channel["channel_id"]
    })
    # User 2 sends a message
    message_params = {
        "token": user02["token"],
        "channel_id": channel["channel_id"],
        "message": "test message",
    }
    message = requests.post(url + "message/send", json=message_params).json()

    # User01 (admin) edits it
    message_edit = {
        "token": user01["token"],
        "message_id": message["message_id"],
        "message": "try editing",
    }
    requests.put(url + "message/edit", data=message_edit)

    # Confirm that message was edited successfully, returns {messages, start, end}
    channel_messages_params = {
        "token": user01["token"],
        "channel_id": channel["channel_id"],
        "start": 0,
    }
    channel_messages = requests.get(
        url + "channel/messages", params=channel_messages_params
    ).json()
    print(channel_messages)
    assert channel_messages["messages"][0] == "try editing"

# # Tests that a message is deleted is edit if empty string
# def test_edit_empty_string(url):
#     requests.delete(url + "clear")
#     user = register_new_account(url)

#     # Create a new channel
#     channel_params = {
#         "token": user["token"],
#         "name": "channel_01",
#         "is_public": True,
#     }
#     channel = requests.post(url + "channels/create", json=channel_params).json()

#     # Send message
#     message_params = {
#         "token": user["token"],
#         "channel_id": channel["channel_id"],
#         "message": "test message",
#     }
#     message = requests.post(url + "message/send", json=message_params).json()

#     # Edit message with empty string
#     message_edit = {
#         "token": user["token"],
#         "message_id": message["message_id"],
#         "message": "",
#     }
#     requests.put(url + "message/edit", json=message_edit)

#     # Ensure message id not in database
#     channel_messages_params = {
#         "token": user["token"],
#         "channel_id": channel["channel_id"],
#         "start": 0,
#     }
#     channel_messages = requests.get(
#         url + "channel/messages", json=channel_messages_params
#     ).json()

#     assert message["message_id"] not in channel_messages["messages"].key()