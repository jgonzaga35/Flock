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
    user = register_new_account(url)
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
    user01 = requests.post(
        url + "/auth/register",
        json={
            "email": "validemail01@gmail.com",
            "password": "123abc01!@#",
            "name_first": "Hayden01",
            "name_last": "Everest01",
        },
    ).json()
    user02 = requests.post(
        url + "/auth/register",
        json={
            "email": "validemail02@gmail.com",
            "password": "123abc02!@#",
            "name_first": "Hayden02",
            "name_last": "Everest02",
        },
    ).json()
    
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
    user01 = requests.post(
        url + "/auth/register",
        json={
            "email": "validemail01@gmail.com",
            "password": "123abc01!@#",
            "name_first": "Hayden01",
            "name_last": "Everest01",
        },
    ).json()
    user02 = requests.post(
        url + "/auth/register",
        json={
            "email": "validemail02@gmail.com",
            "password": "123abc02!@#",
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
    response = requests.post(url + "channels/create", json=channel_params)
    assert response.status_code == 200
    channel = response.json()
    
    # User 2 sends a message
    response = requests.post(
        url + "channel/join", 
        json={
            "token": user02["token"], 
            "channel_id": channel["channel_id"]
        }
    )
    assert response.status_code == 200
    
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
    
    # Confirm that message was removed successfuly
    channel_message_params = {
        "token": user01["token"],
        "channel_id": channel["channel_id"],
        "start": 0,
    }
    channel_messages = requests.get(url + "channel/messages", params=channel_message_params)
    assert channel_messages.status_code == 403