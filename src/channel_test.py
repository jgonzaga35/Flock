from channel import channel_details, channel_leave, channel_join, channel_addowner, formated_user_details_from_user_data
from channels import channels_create
from auth import auth_login, auth_register, auth_get_user_data_from_id
from error import InputError, AccessError
from database import clear_database
import pytest


# register a new user and log in, return the dictionary including u_id and token
def register_a_and_b():
    """ Registers sample users """
    paira = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    pairb = auth_register("email@b.com", "averylongpassword", "B", "LastB")
    return paira, pairb

# Join the channel successfully
def test_join_channel_successfully():
    clear_database()
    user_A, user_B = register_a_and_b()
    channels_create(user_A['token'], "Channel_A", True)
    channels_create(user_B['token'], 'Channel_B', False)

# user try to join a channel with invalid channel id
def test_join_channel_with_invalid_channel_id():
    clear_database()
    user_A, user_B = register_a_and_b() 
    invalid_channel_id = 233
    with pytest.raises(InputError):
        channel_join(user_B['token'], invalid_channel_id)

# join a user without authority to a channel    
def test_join_channel_without_authority():
    clear_database()
    user_A, user_B = register_a_and_b() 
    channel = channels_create(user_A['token'], "Private_channel", False) # Create a new private channel
    
    with pytest.raises(AccessError):
        channel_join(user_B['token'], channel['channel_id'])
    
# user successfully leave the channel
def test_leave_channel_successfully():
    clear_database()
    user_A, user_B = register_a_and_b() 
    private_channal = channels_create(user_A['token'], 'private_channel', False) #Create private channel
    public_channel = channels_create(user_A['token'], 'public_channel', True)   #Create public channel
    channel_leave(user_A['token'], public_channel['channel_id'])
    channel_leave(user_A['token'], private_channal['channel_id'])
    
def test_inexist_uesr_leave_channel():
    clear_database()
    user_A, user_B= register_a_and_b() 
    public_channel = channels_create(user_A['token'], 'public_channel', True)      # User A create a public channel and
    private_channel = channels_create(user_A['token'], 'private_channel', False)   # a private channel
    
    with pytest.raises(AccessError):
        channel_leave(user_B['token'], public_channel['channel_id'])
        channel_leave(user_B['token'], private_channel['channel_id'])




def test_channel_leave_channel_id_invalid():
    clear_database()
    user_A, user_B = register_a_and_b() 
    channel_id = channels_create(user_A['token'], 'channel_A', True)['channel_id']
    invalid_channel_id = channel_id + 1
    with pytest.raises(InputError):
        channel_leave(user_A['token'], invalid_channel_id)



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

if __name__ == '__main__':
    test_join_channel_without_authority(fixture_new_user)