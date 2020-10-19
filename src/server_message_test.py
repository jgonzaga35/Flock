from test_helpers import url
from error import AccessError, InputError
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

##############################################################
#                   Tests for message/remove                 #
##############################################################
def test_remove_invalid_user_token(url):
    requests.delete(url + "clear")
    user = register_new_account(url)
    print(user)
    # Create a new channel
    channel_params = {
        "token": user["token"],
        "name": "channel_01",
        "is_public": True,
    }
    response = requests.post(url + "channels/create", json=channel_params)
    print(response.status_code)
    channel = response.json()
    print(channel)
    # User sends a message
    message_params = {
        "token": user["token"],
        "channel_id": channel["channel_id"],
        "message": "test message",
    }
    message = reqeusts.post(url +  "message/send", json=message_params).json()
    
    # Non-existent user tries to remove the message
    # TODO Ensure token implementation is correct
    message_remove_params = {
        "token": user["token"] + 1,
        "message_id": message["message_id"],
    }
    
    # Ensure access error raised
    r = reqeusts.delete(url + "message/remove", json=message_remove_params)
    assert r.status_code == 403

# def test_remove_invald_message_id(url):
#     requests.delete(url + "clear")
#     user = register_new_account()
#      # Create a new channel
#     channel_params = {
#         "token": user["token"],
#         "name": "channel_01",
#         "is_public": True,
#     }
#     channel = requests.post(url + "/channels/create", json=channel_params).json()
    
#     # User sends a message
#     message_params = {
#         "token": user["token"],
#         "channel_id": channel["channel_id"],
#         "message": "test message",
#     }
#     message = requests.post(url +  "/message/send", json=message_params).json()
    
#     # User tries to edit message with invalid message id
#     message_remove_params = {
#         "token": user["token"],
#         "message_id": INVALID_MESSAGE_ID
#     }
    
#     # Ensure input error raised
#     r = requests.delete(url + "message/remove", json=message_remove_params)
#     assert r.status_code == 422


# # User removing a message is not authorised to remove it
# def test_remove_unauthorised_user(url):
#     requests.delete(url + "clear")
#     user01, user02 = register_n_users(2)
    
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

#     # User 2 tries to remove message from User 1
#     message_remove_params = {
#         "token": user02["token"],
#         "message_id": message["message_id"],
#     }
    
#     r = requests.delete(url + "message/remove", json=message_remove_params)
#     assert r.status_code == 403

# # Test that owner of channel can remove any message
# def test_remove_owner(url):
#     requests.delete(url + "clear")
#     user01, user02 = register_n_users(2)
    
#     # Create a new channel with User01 as admin
#     channel_params = {
#         "token": user01["token"],
#         "name": "channel_01",
#         "is_public": True,
#     }
#     channel = requests.post(url + "channels/create", json=channel_params).json()

#     # User 2 sends a message
#     message_params = {
#         "token": user02["token"],
#         "channel_id": channel["channel_id"],
#         "message": "test message",
#     }
#     message = requests.post(url + "message/send", json=message_params).json()

#     # User01 (admin) removes it
#     message_remove_params = {
#         "token": user01["token"],
#         "message_id": message["message_id"],
#     }
#     requests.delete(url + "message/remove", json=message_remove_params)
    
#     # Confirm that message was removed successfuly
#     channel_message_params = {
#         "token": user01["token"],
#         "channel_id": channel["channel_id"],
#         "start": 0,
#     }
#     channel_messages = requests.get(url + "channel/messages", json=channel_message_params)
#     # TODO Ensure this is correct
#     assert message["message_id"] not in channel_messages