from channels import channels_create, channels_list, channels_listall
from channel import channel_leave, channel_details
from database import database, clear_database
from error import InputError
from auth import auth_register, auth_login
import pytest

def test_create_simple():
    clear_database()
    user = register_and_login_user()
    channel = channels_create(user['token'], 'channel', is_public = True)
    channel_id = channel['channel_id']
    assert channel_id == 0

def test_channel_name():
    clear_database()
    user = register_and_login_user()
    channel = channels_create(user['token'], 'channel_name', is_public = True)
    channel_id = channel['channel_id']
    channel_name = database['channels'][channel_id]['name']
    assert channel_name == 'channel_name'

def test_create_public():
    clear_database()
    user = register_and_login_user()
    channel = channels_create(user['token'], 'channel', is_public = True)
    channel_id = channel['channel_id']
    public_status = database['channels'][channel_id]['is_public']
    assert public_status == True

def test_create_private():
    clear_database()
    user = register_and_login_user()
    channel = channels_create(user['token'], 'channel', is_public = False)
    channel_id = channel['channel_id']
    public_status = database['channels'][channel_id]['is_public']
    assert public_status == False

def test_long_name_error():
    clear_database()
    user = register_and_login_user()
    with pytest.raises(InputError):
        channels_create(user['token'], 'channel name longer than twenty char', is_public = True)

def test_creator_becomes_owner_and_member():
    clear_database()
    user = register_and_login_user()
    channel = channels_create(user['token'], 'channel', is_public=True)
    details = channel_details(user['token'], channel['channel_id'])

    assert len(details['owner_members']) == 1
    assert details['owner_members'][0]['u_id'] == user['u_id']

    assert len(details['all_members']) == 1
    assert details['all_members'][0]['u_id'] == user['u_id']

# Helper function that registers a user and logs them in
# Returns {u_id, token}
def register_and_login_user():
    auth_register('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_01_credentials = auth_login('validemail01@gmail.com', 'validpass@!01')
    return user_01_credentials

# Provide a list of all channels (and their associated details) 
# that the authorised user is part of
def test_channels_list_public():
    clear_database()
    user = register_and_login_user()
    channels_create(user['token'], 'channel', is_public = True)
    total_channels = []
    for channel in database['channels']:
        total_channels.append(channel)

    assert(channels_list(user['token']) == total_channels)

def test_channels_list_private():
    clear_database()
    user = register_and_login_user()
    channels_create(user['token'], 'channel', is_public = False)
    total_channels = []
    for channel in database['channels']:
        total_channels.append(channel)

    assert(channels_list(user['token']) == total_channels)

def test_channels_list_multiple():
    clear_database()
    user = register_and_login_user()
    channels_create(user['token'], 'channel1', is_public = True)
    channels_create(user['token'], 'channel2', is_public = False)
    channels_create(user['token'], 'channel3', is_public = True)
    total_channels = []
    for channel in database['channels']:
        total_channels.append(channel)

    assert(channels_list(user['token']) == total_channels)

def register_and_login_multiple_users(email, password, first_name, last_name):
    auth_register(email, password, first_name, last_name)
    user_credentials = auth_login(email, password)
    return user_credentials

def test_channels_list_unauthorised():
    clear_database()
    user_01 = register_and_login_multiple_users('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_02 = register_and_login_multiple_users('validemail02@gmail.com', 'validpass@!02', 'Second', 'User')
    channels_create(user_01['token'], 'channel1', is_public = True)
    channels_create(user_02['token'], 'channel2', is_public = False)
    total_channels = []
    for channel in database['channels']:
        total_channels.append(channel)

    channels = channels_list(user_01['token'])
    assert(channels == [total_channels[0]])

def test_channels_list_unauthorised_complex():
    clear_database()
    user_01 = register_and_login_multiple_users('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_02 = register_and_login_multiple_users('validemail02@gmail.com', 'validpass@!02', 'Second', 'User')
    user_03 = register_and_login_multiple_users('validemail03@gmail.com', 'validpass@!03', 'Third', 'User')
    channels_create(user_01['token'], 'channel1', is_public = True)
    channels_create(user_02['token'], 'channel2', is_public = False)
    channels_create(user_03['token'], 'channel3', is_public = True)

    total_channels = []
    for channel in database['channels']:
        total_channels.append(channel)

    channels = channels_list(user_01['token'])
    assert(channels == [total_channels[0]])

def test_channels_list_empty():
    clear_database()
    user_01 = register_and_login_multiple_users('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    total_channels = []
    for channel in database['channels']:
        total_channels.append(channel)

    channels = channels_list(user_01['token'])
    assert(channels == total_channels)
 
def test_channels_listall_empty():
    clear_database()
    user_01 = register_and_login_multiple_users('validemail01@gmail.com', 'validpass@!01', 'First', 'User')  
    total_channels = []
    for channel in database['channels']:
        total_channels.append(channel)

    assert(channels_listall(user_01['token']) == total_channels)

def test_channels_listall_public():
    clear_database()
    user_01 = register_and_login_multiple_users('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_02 = register_and_login_multiple_users('validemail02@gmail.com', 'validpass@!02', 'Second', 'User')
    user_03 = register_and_login_multiple_users('validemail03@gmail.com', 'validpass@!03', 'Third', 'User')
    channels_create(user_01['token'], 'channel1', is_public = True)
    channels_create(user_02['token'], 'channel2', is_public = True)
    channels_create(user_03['token'], 'channel3', is_public = True)
    total_channels = []
    for channel in database['channels']:
        total_channels.append(channel)

    assert(channels_listall(user_01['token']) == total_channels)
    assert(channels_listall(user_02['token']) == total_channels)
    assert(channels_listall(user_03['token']) == total_channels)

def test_channels_listall_private():
    clear_database()
    user_01 = register_and_login_multiple_users('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_02 = register_and_login_multiple_users('validemail02@gmail.com', 'validpass@!02', 'Second', 'User')
    user_03 = register_and_login_multiple_users('validemail03@gmail.com', 'validpass@!03', 'Third', 'User')
    channels_create(user_01['token'], 'channel1', is_public = False)
    channels_create(user_02['token'], 'channel2', is_public = False)
    channels_create(user_03['token'], 'channel3', is_public = False)
    total_channels = []
    for channel in database['channels']:
        total_channels.append(channel)
    assert(channels_listall(user_01['token']) == total_channels)
    assert(channels_listall(user_02['token']) == total_channels)
    assert(channels_listall(user_03['token']) == total_channels)
    