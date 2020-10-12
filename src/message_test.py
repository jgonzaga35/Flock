from message import message_send, message_edit
from database import clear_database
from auth import auth_register
from channels import channels_create

from test_helpers import url, register_n_users

from error import AccessError
import pytest
import requests

INVALID_MESSAGE_ID = -1

###############################################################################
#                           Tests for message_send                            #
###############################################################################
def test_edit_non_existenet_user(url):
    user = register_n_users(1)
    # Create a new channel
    channel_params = {
        'token': user['token'],
        'name': 'channel_01',
        'is_public': True,
    }
    channel = requests.post(url + 'channels/create', json=channel_params)
    
    # User sends a message
    message_params = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'test message',
    }
    message = requests.post(url + 'message/send', json=message_params)
    
    # Non-existent user tries to edit the message
    message_edit = {
        'token': user['token'] + 1,
        'message': message['message_id'],
        'message': 'try editing',
    }
    r = requests.post(url + 'message/edit', json=message_edit)
    
    assert r.status_code == 403
    
def test_edit_invalid_message_id():
    user = register_n_users(1)
    # Create a new channel
    channel_params = {
        'token': user['token'],
        'name': 'channel_01',
        'is_public': True,
    }
    channel = requests.post(url + 'channels/create', json=channel_params)
    
    # User sends a message
    message_params = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'test message',
    }
    message = requests.post(url + 'message/send', json=message_params)
    
    # User tries to edit message with an invalid message id
    message_edit = {
        'token': user['token'] + 1,
        'message': INVALID_MESSAGE_ID,
        'message': 'try editing',
    }
    r = requests.post(url + 'message/edit', json=message_edit)
    
    assert r.status_code == 403

# User editing a message is not authorised to edit it
def test_edit_unauthorised_user():
    user01, user02 = register_n_users(2)
    
    # Create a new channel
    channel_params = {
        'token': user01['token'],
        'name': 'channel_01',
        'is_public': True,
    }
    channel = requests.post(url + 'channels/create', json=channel_params)
    
    # User 1 sends a message
    message_params = {
        'token': user01['token'],
        'channel_id': channel['channel_id'],
        'message': 'test message',
    }
    message = requests.post(url + 'message/send', json=message_params)
    
    # User 2 tries to edit the message
    message_edit = {
        'token': user02['token'],
        'message': message['message_id'],
        'message': 'try editing',
    }
    r = requests.post(url + 'message/edit', json=message_edit)
    
    assert r.status_code == 403

# Test that owner of channel can edit any message
def test_edit_owner():
    user01, user02 = register_n_users(2)
    
    # Create a new channel with User01 as admin
    channel_params = {
        'token': user01['token'],
        'name': 'channel_01',
        'is_public': True,
    }
    channel = requests.pst(url + 'channels/create', json=channel_params)
    
    # User 2 sends a message
    message_params = {
        'token': user02['token'],
        'channel_id': channel['channel_id'],
        'message': 'test message',
    }
    message = requests.post(url + 'message/send', json=message_params)
    
    # User01 (admin) edits it
    message_edit = {
        'token': user01['token'],
        'message': message['message_id'],
        'message': 'try editing',
    }
    requests.put(url + 'message/edit', json=message_edit)
    
    # Confirm that message was edited successfully, returns {messages, start, end}
    channel_messages_params = {
        'token': user01['token'],
        'channel_id': channel['channel_id']
        'start': 0
    }
    
    assert channel_messages_params['messages'][0] == 'try editing'
    
    