from channel import channel_invite, channel_details, channel_join
from channels import channels_create
from auth import auth_get_user_data_from_id
from test_helpers import register_n_users, assert_contains_users_id
from other import clear
import pytest
from error import InputError, AccessError


def test_channel_invite_from_unauthorised_user():
    clear()
    usera, userb = register_n_users(2)
    channel_id = channels_create(userb["token"], "userb_channel", False)["channel_id"]

    with pytest.raises(AccessError):
        assert channel_invite(usera["token"], channel_id, userb["u_id"])


def test_channel_invite_invalid_id():
    clear()
    user = register_n_users(1)
    channel_id = channels_create(user["token"], "ch", is_public=False)["channel_id"]

    with pytest.raises(InputError):
        channel_invite(user["token"], channel_id, u_id=-1)


def test_channel_invite_invalid_token():
    clear()
    with pytest.raises(AccessError):
        channel_invite(-1, 0, 0)


def test_channel_invite_simple():
    clear()
    usera, userb = register_n_users(2)
    channel_id = channels_create(userb["token"], "userb_channel", False)["channel_id"]

    usera_info = {
        "u_id": usera["u_id"],
        "name_first": auth_get_user_data_from_id(usera["u_id"])["first_name"],
        "name_last": auth_get_user_data_from_id(usera["u_id"])["last_name"],
    }

    channel_members_info = channel_details(userb["token"], channel_id)["all_members"]
    assert usera_info not in channel_members_info

    channel_invite(userb["token"], channel_id, usera["u_id"])
    updated_channel_members_info = channel_details(userb["token"], channel_id)[
        "all_members"
    ]
    assert usera_info in updated_channel_members_info


def test_channel_invite_member_already_in_channel():
    clear()
    usera, userb = register_n_users(2)
    channel_id = channels_create(userb["token"], "userb_channel", True)["channel_id"]

    usera_info = {
        "u_id": usera["u_id"],
        "name_first": auth_get_user_data_from_id(usera["u_id"])["first_name"],
        "name_last": auth_get_user_data_from_id(usera["u_id"])["last_name"],
    }

    channel_join(usera["token"], channel_id)
    channel_invite(userb["token"], channel_id, usera["u_id"])
    channel_members_info = channel_details(userb["token"], channel_id)["all_members"]

    usera_count = 0
    for user in channel_members_info:
        if user == usera_info:
            usera_count = usera_count + 1
    assert usera_count == 1


def test_channel_invite_multiple_channels():
    clear()
    usera, userb = register_n_users(2)
    channela = channels_create(usera["token"], "usera_ch", is_public=False)
    channelb = channels_create(userb["token"], "userb_ch", is_public=False)

    channel_invite(usera["token"], channela["channel_id"], userb["u_id"])

    detailsa = channel_details(usera["token"], channela["channel_id"])
    detailsb = channel_details(userb["token"], channelb["channel_id"])

    assert_contains_users_id(detailsa["all_members"], [usera["u_id"], userb["u_id"]])
    assert_contains_users_id(detailsa["owner_members"], [usera["u_id"]])

    assert_contains_users_id(detailsb["all_members"], [userb["u_id"]])
    assert_contains_users_id(detailsb["owner_members"], [userb["u_id"]])


def test_channel_invite_invalid_channel_id():
    clear()
    usera, userb = register_n_users(2)

    with pytest.raises(InputError):
        channel_invite(usera["token"], channel_id=-1, u_id=userb["u_id"])
