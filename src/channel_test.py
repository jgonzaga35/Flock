from channel import channel_messages, channel_leave, channel_addowner, channel_join, channel_details, formated_user_details_from_user_data
from auth import auth_register, auth_login, auth_get_user_data_from_id
from channels import channels_create, channels_list
from database import database, clear_database
from error import InputError, AccessError
from word_list import word_list
import random
import pytest

#################################################################################
#                       Tests for channel_messages
#################################################################################
def test_messages_no_messages():
    clear_database()
    user = register_and_login_user(
        'validemailowner01@gmail.com', 'validpass@!owner01', 'Bob', 'Smith'
    )
    channel = channels_create(user['token'], 'channel', is_public = True)
    messages_in_channel = channel_messages(user['token'], channel['channel_id'], start = 0)
    
    assert len(messages_in_channel['messages']) == 0
    assert messages_in_channel['start'] == 0
    assert messages_in_channel['end'] == -1
    
def test_messages_invalid_channel_ID():
    clear_database()
    user = register_and_login_user(
        'validemailowner01@gmail.com', 'validpass@!owner01', 'Bob', 'Smith'
    )
    invalid_channel_id = -1
    with pytest.raises(InputError):
        assert channel_messages(user['token'], invalid_channel_id, 0)

def test_messages_user_not_member():
    clear_database()
    user_01= register_and_login_user(
        'validemail01@gmail.com', 'validpass@!owner01', 'Bob', 'Smith'
    )
    user_02 = register_and_login_user(
        'validemail02@gmail.com', 'validpass@!owner02', 'John', 'Smith'
    )
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
# Returns {u_id, token}
def register_and_login_user(email, password, name_first, name_last):
    user = auth_register(email, password, name_first, name_last)
    return user 

# Helper function that creates a sample channel with 3 users (including 1 owner)
def create_sample_channel():
    # Register a owner and two users and logs them in
    owner_credentials = register_and_login_user(
        'validemailowner@gmail.com', 'validpass@!owner', 'Channel', 'Owner'
    )
    user_01_credentials = register_and_login_user(
        'validemail01@gmail.com', 'validpass@!01', 'First', 'User'
    )
    user_02_credentials = register_and_login_user(
        'validemail@gmail.com', 'validpass@!02', 'Second', 'User'
    )
    
    # Create a channel, with token of owner
    channel_ID = channels_create(owner_credentials['token'], 'channel_01', is_public = True)

    # Add users to the channel
    channel_join(owner_credentials['token'], channel_ID)
    channel_join(user_01_credentials['token'], channel_ID)
    channel_join(user_02_credentials['token'], channel_ID)
#################################################################################



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

if __name__ == '__main__':
    test_join_channel_without_authority(fixture_new_user)
