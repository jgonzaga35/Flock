from channel import channel_messages, channel_addowner, channel_join
from auth import auth_register, auth_login
from channels import channels_create
from database import database
from error import InputError, AccessError
import pytest

INVALID_CHANNEL_ID = -1

# Note: Tokens are currently User ID for iteration 1
def test_messages_invalid_channel_ID():
    with pytest.raises(InputError):
        assert channel_messages(0, INVALID_CHANNEL_ID, 0)

def test_messages_negative_start_index():
    new_channel_ID = channels_create(0, 'new_channel', 'is_public')
    with pytest.raises(InputError):
        assert channel_messages(0, new_channel_ID['channel_id'], -1)

def test_messages_invalid_start_index():
    ''' Start is greater than the total # of messages in channel '''
    new_channel_ID = channels_create(0, 'new_channel', 'is_public')
    assert channel_messsages(0, new_channel_ID['channel_id'], 0) == -1
    
# Helper function that creates a sample channel with 3 users (including 1 owner)
def create_sample_channel():
    # Register a owner and two users and logs them in
    owner_credentials = register_and_login_user('validemailowner@gmail.com', 'validpass@!owner', 'Channel', 'Owner')
    user_01_credentials = register_and_login_user('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_02_credentials = register_and_login_user('validemail@gmail.com', 'validpass@!02', 'Second', 'User')
    
    # Create a channel, with token of owner
    channel_ID = channels_create(owner_credentials['token'], 'channel_01', is_public = True)

    # Add users to the channel
    channel_join(owner_credentials['token'], channel_ID)
    channel_join(user_01_credentials['token'], channel_ID)
    channel_join(user_02_credentials['token'], channel_ID)

# Registers a user and logs them in
# Returns {u_id, token}
def register_and_login_user(email, password, name_first, name_last):
    user = auth_register('validemailowner@gmail.com', 'validpass@!owner', 'Channel', 'Owner')
    user_credentials = auth_login('validemailowner@gmail.com', 'validpass@!owner')
    return user_credentials

# Helper function to send 10 messages to a given channel
# def populate_channel_ten_messages(channel_id):
    # database['channels']