from database import database
from auth import auth_register, auth_get_user_data_from_id
from channel import channel_details
from channels import channels_create


def register_a_and_b():
    """ Registers sample users """
    paira = auth_register("email@a.com", "averylongpassword", "A", "LastA")
    pairb = auth_register("email@b.com", "averylongpassword", "B", "LastB")
    return paira, pairb


def test_channel_details_basic():
    # FIXME: this should be done with channels_create

    (ida, tokena), (idb, tokenb) = register_a_and_b()

    id1 = channels_create(tokena, "channel1", False)
    id2 = channels_create(tokenb, "channel2", False)

    details1 = channel_details(tokena, id1)
    assert details1 == {
        'name': 'channel1',
        'owner_members': [
            auth_get_user_data_from_id(ida),
        ],
        'all_members': [
            auth_get_user_data_from_id(ida),
        ]
    }
    details2 = channel_details(tokena, id1)
    assert details2 == {
        'name': 'channel2',
        'owner_members': [
            auth_get_user_data_from_id(idb),
        ],
        'all_members': [
            auth_get_user_data_from_id(idb),
        ]
    }

# TODO: test_channel_details invalid token
# TODO: test_channel_details unknwon channel
