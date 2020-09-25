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

    # FIXME: this should be done with channels_create
    id1 = 1
    database['channels'].append({
        'name': 'channel1',
        'id': id1,
        'is_public': True,
        'ownersid': [usera['u_id']],
        'membersid': [usera['u_id']]
    })
   
    details1 = channel_details(usera['token'], id1)
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


# TODO: test_channel_details invalid token
# TODO: test_channel_details unknwon channel
