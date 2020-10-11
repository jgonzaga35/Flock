from message import message_send, message_edit
from database import clear_database

from auth import auth_register
from channels import channels_create

from error import AccessError
import pytest

INVALID_MESSAGE_ID = -1

###############################################################################
#                           Tests for message_send                            #
###############################################################################
def test_send_non_existenet_user():
    clear_database()
    user = register_and_login_user()
    # Create a new channel
    channel = channels_create(user['token'], 'channel_01', is_public=True)
    message = message_send(user['token'], channel['channel_id'], 'new message')
    
    with pytest.raises(AccessError):
        assert message_edit(user['token'] + 1, message['message_id'], 'try editing')
    
def test_send_invalid_message_id():
    clear_database()
    user = register_and_login_user()
    # Create a new channel
    channel = channels_create(user['token'], 'channel_01', is_public=True)
    message = message_send(user['token'], channel['channel_id'], 'new message')
    
    with pytest.raises(AccessError):
        assert message_edit(user['token'], INVALID_MESSAGE_ID, 'try editing')

# User editing a message is not authorised to edit it
def test_send_unauthorised_user():
    clear_database()
    user_01 = register_and_login_user()
    user_02 = register_and_login_user_2()
    
    # Create a new channel
    channel = channels_create(user['token'], 'channel_01', is_public=True)
    message = message_send(user_01['token'], channel['channel_id'], 'new message')
    
    with pytest.raises(AccessError):
        assert message_edit(user_02['token'], message['message_id'], 'try editing')


# Helper functions which registers a user and logs them in
# Return {u_id, token}
def register_and_login_user():
    auth_register('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_01_credentials = auth_login('validemail01@gmail.com', 'validpass@!01')
    return user_01_credentials

def register_and_login_user_2():
    auth_register('validemail02@gmail.com', 'validpass@!02', 'Second', 'User')
    user_02_credentials = auth_login('validemail02@gmail.com', 'validpass@!02')
    return user_02_credentials