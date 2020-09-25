from channels import channels_create
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



# Helper function that registers a user and logs them in
# Returns {u_id, token}
def register_and_login_user():
    user_01 = auth_register('validemail01@gmail.com', 'validpass@!01', 'First', 'User')
    user_01_credentials = auth_login('validemail01@gmail.com', 'validpass@!01')
    return user_01_credentials