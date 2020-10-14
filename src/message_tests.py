from message import message_remove, message_send
from channels import channels_create, channels_list, channel_messages
from test_helpers import register_n_users
from database import clear_database

import pytest 
from error import AccessError, InputError

INVALID_USER_TOKEN = -1
INVALID_MESSAGE_ID = -1
#######################################################
#               Tests for message_remove              #
#######################################################
def test_remove_invalid_user_token():
    clear_database()
    user = register_n_users(1)

    # Create a new channel
    channel = channels_create(user['token'], 'channel01', is_public=True)
    # User sends a message
    message = message_send(user['token'], channel['channel_id'], 'test message')
    # Non-existent user tries to remove the message
    with pytest.raises(AccessError):
        message_remove(INVALID_USER_TOKEN, message['message_id'])

def test_remove_invalid_message_id():
    clear_database()
    user = register_n_users(1)

    # Create a new channel
    channel = channels_create(user['token'], 'channel01', is_public=True)
    # User sends a message
    message = message_send(user['token'], channel['channel_id'], 'test message')
    # user tries to remove emssage with invalid message id
    with pytest.raises(AccessError):
        message_remove(user['token'], INVALID_MESSAGE_ID)

# User tries to remove a message that they are not authorised to remove
def test_remove_unauthorised_user():
    user01, user02 = register_n_users(2)

    # Create channel with message from user01
    channel = channels_create(user['token'], 'channel', is_public=True)
    message = message_send(user01['token'], channel['channel_id'], 'test message')
    # User02 tries to remove message from user01
    with pytest.raises(AccessError):
        message_remove(user02['token'], message['message_id'])
    
# Test that the owner of the channel can remove any message    
def test_remove_owner_permissions():
    clear_database()
    user01, user02 = register_n_users(2)

    # Create a new channel with user01 as admin
    channel = channels_create(user01['tokne'], 'channel', is_public=True)

    message = message_send(user02['token'], channel['channel_id'], 'test message')
    message_remove(user01['token'], message['message_id'])
    channel_messages = channel_messages(user01['token'], channel['channel_id'], 0)
    
    # How do I check whether the removed message is actually removed?
    # I can check for the actual message:
    #       assert 'test message' in channel_messages['messages']
    # but this won't work - what if another user sent the same message? 
    # i.e. two identical message were present in the channel
    #
    # Since the output of channel_messages doesn't contain the channel_id,
    # I can't check that the message was actually removed without
    # doing white-box testing