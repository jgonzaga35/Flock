from channels import channels_create, channels_list, channels_listall
from channel import channel_leave, channel_details
from database import database, clear_database
from error import InputError, AccessError
from auth import auth_register, auth_login
import pytest

def test_create_simple():
    clear_database()
    user = register_and_login_user()
    channel = channels_create(user['token'], 'channel_name', is_public=True)

    details = channel_details(user['token'], channel['channel_id'])
    assert details['name'] == 'channel_name'

def test_create_private():
    clear_database()
    usera = auth_register("email@a.com", "averylongpassword", "first", "last")
    userb = auth_register("email@b.com", "averylongpassword", "firstb", "lastb")
    channel = channels_create(usera['token'], 'channel', is_public=False)

    details = channel_details(usera['token'], channel['channel_id'])
    assert details['name'] == 'channel'

    with pytest.raises(AccessError):
        channel_details(userb['token'], channel['channel_id'])

def test_long_name_error():
    clear_database()
    user = register_and_login_user()
    with pytest.raises(InputError):
        channels_create(user['token'], 'channel name longer than twenty char', True)

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
    token = user['token']
    channel_id = channels_create(token, 'channel', is_public = True)['channel_id']
    total_channels = [channel_details(token, channel_id)]
    assert(channels_list(token) == total_channels)

def test_channels_list_private():
    clear_database()
    user = register_and_login_user()
    token = user['token']
    channel_id = channels_create(token, 'channel', is_public = True)['channel_id']
    total_channels = [channel_details(token, channel_id)]
    assert(channels_list(token) == total_channels)

def test_channels_list_multiple():
    clear_database()
    user = register_and_login_user()
    token = user['token']
    channel_id_1 = channels_create(token, 'channel1', is_public = True)['channel_id']
    channel_id_2 = channels_create(token, 'channel2', is_public = False)['channel_id']
    channel_id_3 = channels_create(token, 'channel3', is_public = True)['channel_id']
    channel_ids = [channel_id_1, channel_id_2, channel_id_3]
    total_channels = []
    for channel_id in channel_ids:
        total_channels.append(channel_details(token, channel_id))
    assert(channels_list(token) == total_channels)

def register_and_login_multiple_users(email, password, first_name, last_name):
    auth_register(email, password, first_name, last_name)
    user_credentials = auth_login(email, password)
    return user_credentials

def test_channels_list_unauthorised():
    clear_database()
    user_01 = register_and_login_multiple_users('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_01_token = user_01['token']
    user_02 = register_and_login_multiple_users('validemail02@gmail.com', 'validpass@!02', 'Second', 'User')
    user_01_channel_id = channels_create(user_01['token'], 'channel1', is_public = True)['channel_id']
    channels_create(user_02['token'], 'channel2', is_public = False)['channel_id']

    authorised_channels = [channel_details(user_01_token, user_01_channel_id)]
    assert(channels_list(user_01_token) == authorised_channels)

def test_channels_list_unauthorised_complex():
    clear_database()
    user_01 = register_and_login_multiple_users('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_02 = register_and_login_multiple_users('validemail02@gmail.com', 'validpass@!02', 'Second', 'User')
    user_03 = register_and_login_multiple_users('validemail03@gmail.com', 'validpass@!03', 'Third', 'User')
    user_01_channel_id = channels_create(user_01['token'], 'channel1', is_public = True)['channel_id']
    user_02_channel_id = channels_create(user_02['token'], 'channel2', is_public = False)['channel_id']
    user_03_channel_id = channels_create(user_03['token'], 'channel3', is_public = True)['channel_id']

    assert(channels_list(user_01['token']) == [channel_details(user_01['token'], user_01_channel_id)])
    assert(channels_list(user_02['token']) == [channel_details(user_02['token'], user_02_channel_id)])
    assert(channels_list(user_03['token']) == [channel_details(user_03['token'], user_03_channel_id)])

def test_channels_list_empty():
    clear_database()
    user_01 = register_and_login_multiple_users('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    assert(channels_list(user_01['token']) == [])

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
    token = user_01['token']
    channel_id_1 = channels_create(token, 'channel1', is_public = True)['channel_id']
    channel_id_2 = channels_create(token, 'channel2', is_public = True)['channel_id']
    channel_id_3 = channels_create(token, 'channel3', is_public = True)['channel_id']

    channel_ids = [channel_id_1, channel_id_2, channel_id_3]
    total_channels = []
    for channel_id in channel_ids:
        total_channels.append(channel_details(token, channel_id))

    assert(channels_listall(user_01['token']) == total_channels)

def test_channels_listall_private():
    clear_database()
    user_01 = register_and_login_multiple_users('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    token = user_01['token']
    channel_id_1 = channels_create(token, 'channel1', is_public = False)['channel_id']
    channel_id_2 = channels_create(token, 'channel2', is_public = False)['channel_id']
    channel_id_3 = channels_create(token, 'channel3', is_public = False)['channel_id']

    channel_ids = [channel_id_1, channel_id_2, channel_id_3]
    total_channels = []
    for channel_id in channel_ids:
        total_channels.append(channel_details(token, channel_id))

    assert(channels_listall(user_01['token']) == total_channels)

def test_channels_listall_multiple_users():
    clear_database()

    user_01 = register_and_login_multiple_users('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_02 = register_and_login_multiple_users('validemail02@gmail.com', 'validpass@!02', 'Second', 'User')
    user_03 = register_and_login_multiple_users('validemail03@gmail.com', 'validpass@!03', 'Third', 'User')
    
    channel_id_1 = channels_create(user_01['token'], 'channel1', is_public = False)['channel_id']
    channel_id_2 = channels_create(user_02['token'], 'channel2', is_public = False)['channel_id']
    channel_id_3 = channels_create(user_03['token'], 'channel3', is_public = False)['channel_id']

    tokens = [user_01['token'], user_02['token'], user_03['token']]
    channel_ids = [channel_id_1, channel_id_2, channel_id_3]
    total_channels = []
    i = 0
    for channel_id in channel_ids:
        total_channels.append(channel_details(tokens[i], channel_id))
        i = i + 1
    
    assert(channels_listall(user_01['token']) == total_channels)
    