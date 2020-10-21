from test_helpers import url, http_register_n_users
from error import AccessError, InputError
import pytest
import requests
import json

INVALID_MESSAGE_ID = -1

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
        "token": user["token"] + 1,
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
    response = requests.post(url +  "message/send", json=message_params)
    assert response.status_code == 200
    message = response.json()
    
    # User tries to edit message with invalid message id
    message_remove_params = {
        "token": user["token"],
        "message_id": INVALID_MESSAGE_ID
    }
    
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
        json={
            "token": user02["token"], 
            "channel_id": channel["channel_id"]
        }
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


