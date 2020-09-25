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
    


# Helper function that creates a sample channel with sample messages and users    
def create_sample_channel_01():
    # Register a owner and two users and logs them in
    owner = auth_register('validemailowner@gmail.com', 'validpass@!owner', 'Channel', 'Owner')
    owner_credentials = auth_login('validemailowner@gmail.com', 'validpass@!owner')
    user_01 = auth_register('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_01_credentials = auth_login('validemail01@gmail.com', 'validpass@!01')
    user_02 = auth_register('validemail@gmail.com', 'validpass@!02', 'Second', 'User' )
    user_01_credentials = auth_login('validemail@gmail.com', 'validpass@!02')
    
    # Create a channel
    channel_ID_01 = channels_create(owner_credentials['token'], 'channel_01', 'is_public')
    
    # Add users to the channel
    channel_join(owner_credentials['token'], channel_ID_01)
    channel_join(user_01_credentials['token'], channel_ID_01)
    channel_join(user_02_credentials['token'], channel_ID_01)

# Helper function to send 10 messages to a given channel
#def add_ten_messages_to_channel(channel_id):
    #database['channels'] = 