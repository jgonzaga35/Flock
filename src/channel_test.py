import pytest
from error import AccessError, InputError
from database import database, clear_database
from auth import auth_register, auth_get_user_data_from_id
from channel import channel_details, formated_user_details_from_user_data
from channels import channels_create


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
