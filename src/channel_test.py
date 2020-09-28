from channel import channel_messages, channel_addowner, channel_join, channel_details, formated_user_details_from_user_data
from auth import auth_register, auth_login, auth_get_user_data_from_id
from channels import channels_create, channels_list
from database import database, clear_database
from error import InputError, AccessError
from word_list import *
import random
import pytest

#################################################################################
#                       Tests for channel_messages
#################################################################################
def test_messages_invalid_channel_ID():
    clear_database()
    user = register_and_login_user('validemailowner01@gmail.com', 'validpass@!owner01', 'Bob', 'Smith')
    invalid_channel_id = -1
    list_of_channels = channels_list(user['token'])
    list_of_channel_id = []
    for channel in list_of_channels:
        list_of_channels.append(channel['channel_id'])
    
    while invalid_channel_id in list_of_channel_id:
        invalid_channel_id *= 2
        
    with pytest.raises(InputError):
        assert channel_messages(user['token'], invalid_channel_id, 0)

def test_messages_user_not_member():
    clear_database()
    user_01= register_and_login_user('validemail01@gmail.com', 'validpass@!owner01', 'Bob', 'Smith')
    user_02 = register_and_login_user('validemail02@gmail.com', 'validpass@!owner02', 'John', 'Smith')
    channel = channels_create(user_01['token'], 'channel_01', is_public = True)
    channel_join(user_01['token'], channel['channel_id'])
    
    with pytest.raises(AccessError):
        assert channel_messages(user_02['token'], channel['channel_id'], 0)
    
# ----------------------------- Add these tests when message_send is implemented ------------------
# def test_messages_negative_start_index():
#     clear_database()
    # # Add a user and log them in
    # user = register_and_login_user('validemailowner01@gmail.com', 'validpass@!owner01', 'Bob', 'Smith')
    
    # # Create a channel and fill with messages
    # channel = channels_create(user['token'], 'new_channel', is_public = True)
    # populate_channel_hundred_messages(user['token'], channel['channel_id'])
#     with pytest.raises(InputError):
#         assert channel_messages(user['token'], channel['channel_id'], -1)

# def test_messages_simple():
#     clear_database()
#     # Add a user and log them in
#     user = register_and_login_user('validemailowner01@gmail.com', 'validpass@!owner01', 'Bob', 'Smith')
    
#     # Create a channel and fill with messages
#     channel = channels_create(user['token'], 'new_channel', is_public = True)
#     message_send(user['token'], channel['channel_id]', "Hello World!"])
#     res = channel_messages(user['token'], channel['channel_id'], 0)
#     assert res['messages'][0] == {"Hello World!"}

# def test_messages_start_overflow():
    # clear_database()
    # user = register_and_login_user('validemail01@gmail.com', 'validpass@!owner01', 'Bob', 'Smith')
    # channel = channels_create(user['token'], 'channel_01', is_public = True)
    # channel_join(user['token'], channel['channel_id'])
    # message_send(user['token'], channel['channel_id'], 'Hello World!')
    # with pytest.raises(InputError):
    #     assert channel_messages(user['token'], channel['channel_id'], 100)

# def test_messages_start_underflow():
#     clear_database()
#     user = register_and_login_user('validemail01@gmail.com', 'validpass@!owner01', 'Bob', 'Smith')
#     channel = channels_create(user['token'], 'channel_01', is_public = True)
#     channel_join(user['token'], channel['channel_id'])
#     message_send(user['token'], channel['channel_id'], 'Hello World!')
#     assert channel_messages(user['token'], channel['channel_id'], 0) == -1

# # Helper function to send 100 messages to a given channel
# def populate_channel_hundred_messages(token, channel_id):
#     for i in range(1,100):
#         index = random.randint(0, len(word_list) - 1)
#         message = word_list[index]
#         message_send(token, channel_id, message)

# ---------------------------------------------------------------------------------------------
# Helper function that registers a user and logs them in
# Returns {u_id, token}
def register_and_login_user(email, password, name_first, name_last):
    user = auth_register(email, password, name_first, name_last)
    user_credentials = auth_login(email, password)
    return user_credentials

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
#################################################################################



def register_a_and_b():
    """ Registers sample users """
    paira = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    pairb = auth_register("email@b.com", "averylongpassword", "B", "LastB")
    return paira, pairb


def test_channel_details_basic():
    clear_database()

    usera, userb = register_a_and_b()

    channel_id = channels_create(usera['token'], 'channel1', True)['channel_id']
   
    details1 = channel_details(usera['token'], channel_id)
    assert details1 == {
        'name': 'channel1',
        'owner_members': [
            formated_user_details_from_user_data(
                auth_get_user_data_from_id(usera['u_id'])
            )
        ],
        'all_members': [
            formated_user_details_from_user_data(
                auth_get_user_data_from_id(usera['u_id'])
            )
        ]
    }

def test_channel_details_private():
    clear_database()

    usera, userb = register_a_and_b()

    channel_id = channels_create(userb['token'], 'channel2', False)['channel_id']

    assert channel_details(userb['token'], channel_id) == {
        'name': 'channel2',
        'owner_members': [
            formated_user_details_from_user_data(
                auth_get_user_data_from_id(userb['u_id'])
            )
        ],
        'all_members': [
            formated_user_details_from_user_data(
                auth_get_user_data_from_id(userb['u_id'])
            )
        ]
    }

    with pytest.raises(AccessError):
        channel_details(usera['token'], channel_id)

def test_channel_details_invalid_id():
    clear_database()

    usera, _ = register_a_and_b()

    # fixme: this should be done with channel create
    with pytest.raises(InputError):
        channel_details(usera['token'], 1)