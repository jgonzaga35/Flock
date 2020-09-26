from channel import channel_details, channel_leave, channel_join, channel_addowner
from channels import channels_create
from auth import auth_login, auth_register
from error import InputError, AccessError
from database import clear_database, database
import pytest

# register a new user and log in, return the dictionary including u_id and token
@pytest.fixture
def fixture_new_user():
    user_info = auth_register('balabala.love@gmail.com', 'qweAsd1232566', 'White', 'Black')
    auth_login('balabala.love@gmail.com', 'qweAsd1232566')
    return user_info

# Join the channel successfully
def test_join_channel_successfully(fixture_new_user):
    clear_database()
    user = fixture_new_user
    channel = channels_create(user['token'], "Channel_A", True)
    channel_join(user['token'], channel['channel_id'])

# user try to join a channel with invalid channel id
def test_join_channel_with_invalid_id(fixture_new_user):
    clear_database()
    user = fixture_new_user
    invalid_channel_id = 233
    with pytest.raises(InputError):
        channel_join(user['token'], invalid_channel_id)

# join a user without authority to a channel    
def test_join_channel_without_authority(fixture_new_user):
    clear_database()
    user_A = fixture_new_user
    channel = channels_create(user_A['token'], "Private_channel", False) # Create a new private channel
    
    '''Create another user which don't have authority to this channel'''
    user_B = auth_register('labalab.love@gmail.com', 'qweASD5200a01', 'Yellow', 'Re')
    auth_login('labalab.love@gmail.com','qweASD5200a01') 
    with pytest.raises(AccessError):
        channel_join(user_B['token'], channel['channel_id'])
    
# user successfully leave the channel
def test_leave_channel_successfully(fixture_new_user):
    clear_database()
    user = fixture_new_user
    private_channal = channels_create(user['token'], 'private_channel', False) #Create private channel
    public_channel = channels_create(user['token'], 'public_channel', True)   #Create public channel
    channel_leave(user['token'], public_channel['channel_id'])
    channel_leave(user['token'], private_channal['channel_id'])
    
def test_inexist_uesr_leave_channel(fixture_new_user):
    clear_database()
    user_A = fixture_new_user
    public_channel = channels_create(user_A['token'], 'public_channel', True)      # User A create a public channel and
    private_channel = channels_create(user_A['token'], 'private_channel', False)   # a private channel
    
    '''Create another user which is not in this two channel'''
    user_B = auth_register('labalab.love@gmail.com', 'qweASD5200a01', 'Yellow', 'Re')
    auth_login('labalab.love@gmail.com','qweASD5200a01')
    with pytest.raises(AccessError):
        channel_leave(user_B['token'], public_channel['channel_id'])
        channel_leave(user_B['token'], private_channel['channel_id'])




def test_channel_leave_channel_id_invalid(fixture_new_user):
    clear_database()
    user = fixture_new_user
    channel_id = channels_create(user['token'], 'channel_A', True)
    invalid_channel_id = channel_id['channel_id'] + 1
    with pytest.raises(InputError):
        channel_leave(user['token'], invalid_channel_id)

if __name__ == '__main__':
    test_join_channel_without_authority(fixture_new_user)