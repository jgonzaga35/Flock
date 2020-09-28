from channel import channel_details, channel_leave, channel_join, channel_addowner, formated_user_details_from_user_data
from channels import channels_create
from auth import auth_login, auth_register, auth_get_user_data_from_id
from error import InputError, AccessError
from database import clear_database
import pytest


# register a new user and log in, return the dictionary including u_id and token
def register_one_user():
    """ Registers sample users """
    paira = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    return paira

def register_a_and_b():
    """ Registers sample users """
    paira = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    pairb = auth_register("email@b.com", "averylongpassword", "B", "LastB")
    return paira, pairb

def register_a_b_and_c():
    """ Registers sample users """
    paira = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    pairb = auth_register("email@b.com", "averylongpassword", "B", "LastB")
    pairc = auth_register("email@c.com", "averylongpassword", "C", "LastC")
    return paira, pairb, pairc

# Join the channel successfully
def test_join_channel_successfully():
    clear_database()
    user_A, user_B = register_a_and_b()
    public_channel = channels_create(user_A['token'], "Channel_A", True)
    channel_join(user_B['token'], public_channel['channel_id'])

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
    
def test_inexist_uesr_leave_channel_private():
    clear_database()
    user_A, user_B= register_a_and_b() 
    private_channel = channels_create(user_A['token'], 'private_channel', False)   # a private channel
    
    with pytest.raises(AccessError):
        channel_leave(user_B['token'], private_channel['channel_id'])

def test_inexist_uesr_leave_channel_public():
    clear_database()
    user_A, user_B= register_a_and_b() 
    public_channel = channels_create(user_A['token'], 'public_channel', True)      # User A create a public channel and
    
    with pytest.raises(AccessError):
        channel_leave(user_B['token'], public_channel['channel_id'])




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

def test_add_owner_successfully():
    clear_database()
    user_A, user_B = register_a_and_b()
    private_channel = channels_create(user_A['token'], "private_channel", False)
    channel_addowner(user_A['token'], private_channel['channel_id'], user_B['u_id'])

def test_add_owner_with_invalid_channel_id():
    clear_database()
    user_A, user_B = register_a_and_b()
    public_channel = channels_create(user_A['token'], "public_channel", True)
    channel_join(user_A['token'], public_channel)
    with pytest.raises(InputError):
        channel_addowner(user_A['token'], private_channel['channel_id'] + 1, user_B['u_id']) #channel_id + 1 is invalid

def test_add_owner_repeatedly():
    clear_database()
    user_A, user_B = register_a_and_b()
    private_channel = channels_create(user_A['token'], "private_channel", False)
    with pytest.raises(InputError):
        channel_addowner(user_A['token'], private_channel['channel_id'], user_A['u_id'])

def test_add_invalid_user_to_owner():
    clear_database()
    user_A = register_one_user()
    private_channel = channels_create(user_A['token'], "private_channel", False)
    invalid_uid = 233
    with pytest.raises(InputError):
        channel_addowner(user_A['token'], private_channel['channel_id'], invalid_uid)


# We assume all of the user are in a public channel
# One of them are the owner whereas other two are common user in this channel
def test_add_owner_by_non_owner():
    clear_database()
    user_A, user_B, user_C = register_a_b_and_c()
    public_channel = channels_create(user_A['token'], "public_channel", True) #user_A create the channel and be the owner
    channel_join(user_C['token'], public_channel['channel_id']) # Other two user join in the channel
    channel_join(user_B['token'], public_channel['channel_id'])
    with pytest.raises(AccessError):
        channel_addowner(user_B['token'], public_channel['channel_id'], user_C['u_id']) # user_B who are not owner add common user
                                                                                        # user_C be the owner


if __name__ == '__main__':
    test_join_channel_without_authority(fixture_new_user)